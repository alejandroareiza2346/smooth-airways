from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sessions.models import Session
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import User, PasswordResetToken
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class MembershipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'membership_tier': user.membership_tier,
            'membership_start_date': user.membership_start_date,
            'membership_end_date': user.membership_end_date,
            'membership_number': user.membership_number,
            'is_premium': user.is_premium,
        })

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if email already exists
        if User.objects.filter(email=serializer.validated_data['email']).exists():
            return Response({
                'error': 'El correo electrónico ya está registrado.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save(is_active=False)  # Set user as inactive until email is verified

        # Generate email verification token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_url = f"{settings.FRONTEND_URL}/verify-email?uid={uid}&token={token}"

        # Send verification email
        send_mail(
            'Verifica tu correo electrónico - Smooth Airlines',
            f'Por favor, verifica tu correo electrónico haciendo clic en el siguiente enlace: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response({
            'message': 'Registro exitoso. Por favor, verifica tu correo electrónico para activar tu cuenta.'
        }, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        uid = request.GET.get('uid')
        token = request.GET.get('token')

        try:
            user_id = force_bytes(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({
                    'message': 'Correo electrónico verificado exitosamente. Ahora puedes iniciar sesión.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'El enlace de verificación es inválido o ha expirado.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'El enlace de verificación es inválido.'
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Check if the user is active
        if not user.is_active:
            return Response({
                'error': 'Esta cuenta está desactivada. Por favor, contacta al soporte.'
            }, status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        # Update session expiration
        request.session.set_expiry(3600)  # 1 hour

        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Delete all tokens for the user
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({
            'message': 'Sesión cerrada exitosamente.'
        }, status=status.HTTP_200_OK)

class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            # Delete any existing tokens
            PasswordResetToken.objects.filter(user=user).delete()

            # Create new token
            token = PasswordResetToken.objects.create(
                user=user,
                token=get_random_string(64)
            )

            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token.token}"
            send_mail(
                'Restablecer Contraseña - Smooth Airlines',
                f'Para restablecer tu contraseña, haz clic en el siguiente enlace: {reset_url}\n\n'
                f'Este enlace expirará en 24 horas.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            return Response({
                'error': 'No se encontró una cuenta con este correo electrónico.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "message": "Si existe una cuenta con este email, recibirás instrucciones para restablecer tu contraseña."
        })

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token_obj = PasswordResetToken.objects.get(
                token=serializer.validated_data['token']
            )

            # Check if the token is still valid
            if not token_obj.is_valid:
                token_obj.delete()
                return Response({
                    'error': 'El token ha expirado o es inválido.'
                }, status=status.HTTP_400_BAD_REQUEST)

            user = token_obj.user
            user.set_password(serializer.validated_data['password'])
            user.save()

            # Delete the used token
            token_obj.delete()

            return Response({
                'message': 'Contraseña actualizada exitosamente.'
            })
        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': 'Token inválido o expirado.'
            }, status=status.HTTP_400_BAD_REQUEST)

class AdminOnlyView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        return Response({"message": "Solo accesible para administradores."})

@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('accounts:user-profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'accounts/user_profile.html', {'form': form})