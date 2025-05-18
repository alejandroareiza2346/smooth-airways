from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, View, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings
from flights.models import Flight
from services.models import Service, ServiceBooking
from accounts.models import User
from accounts.mixins import ClientRequiredMixin, AdminRequiredMixin
from datetime import datetime, timedelta
from django import forms
import uuid
from axes.utils import reset
from django.contrib.auth.models import Group
from bookings.models import Aircraft, Booking

# Forms
class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-gold',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-gold',
            'placeholder': '********'
        })
    )

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-gold',
            'placeholder': '********'
        })
    )
    confirm_password = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-gold',
            'placeholder': '********'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-gold',
                'placeholder': 'correo@ejemplo.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-gold',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-gold',
                'placeholder': 'Apellido'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password:
            if len(password) < 8:
                raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres')
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError('La contraseña debe contener al menos un número')
            if not any(char.isupper() for char in password):
                raise forms.ValidationError('La contraseña debe contener al menos una letra mayúscula')
            if password != confirm_password:
                raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned_data

# Authentication Views
class CustomLoginView(View):
    template_name = 'core/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'¡Bienvenido de nuevo, {user.first_name}!')
                    next_url = request.GET.get('next')
                    return redirect(next_url if next_url else 'core:dashboard')
                else:
                    messages.error(request, 'Tu cuenta no está activa. Por favor, verifica tu correo electrónico.')
            else:
                messages.error(request, 'Email o contraseña incorrectos.')
        return render(request, self.template_name, {'form': form})

class CustomLogoutView(LogoutView):
    next_page = 'core:home'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, '¡Hasta pronto!')
        return super().dispatch(request, *args, **kwargs)

class RegisterView(CreateView):
    template_name = 'core/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('core:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.username = user.email
        user.is_active = False  # User needs to verify email
        user.save()
        
        # Send welcome email with verification link
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = self.request.build_absolute_uri(
            reverse_lazy('core:verify_email', kwargs={'uidb64': uid, 'token': token})
        )
        
        subject = '¡Bienvenido a Smooth Airlines!'
        html_message = render_to_string('core/emails/welcome.html', {
            'user': user,
            'verify_url': verification_url
        })
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            messages.success(self.request, 'Cuenta creada exitosamente. Por favor verifica tu correo electrónico.')
        except Exception as e:
            messages.error(self.request, 'Error al enviar el correo de verificación. Por favor contacta a soporte.')
            user.delete()
            return redirect(self.success_url)
        
        return redirect(self.success_url)

class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                messages.success(request, '¡Email verificado! Ahora puedes iniciar sesión.')
                return redirect('core:login')
            else:
                messages.error(request, 'El enlace de verificación es inválido o ha expirado.')
                return redirect('core:register')
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'El enlace de verificación es inválido.')
            return redirect('core:register')

def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = request.build_absolute_uri(
                reverse_lazy('core:verify_email', kwargs={'uidb64': uid, 'token': token})
            )
            
            subject = 'Verificación de Email - Smooth Airlines'
            html_message = render_to_string('core/emails/verification.html', {
                'user': user,
                'verify_url': verification_url
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=html_message,
                fail_silently=False,
            )
            messages.success(request, 'El correo de verificación ha sido reenviado.')
        except User.DoesNotExist:
            messages.error(request, 'No se encontró una cuenta inactiva con ese email.')
    return redirect('core:login')

# Custom Password Reset Views
class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'core/password_reset.html'
    email_template_name = 'core/emails/password_reset_email.html'
    subject_template_name = 'core/emails/password_reset_subject.txt'
    success_url = reverse_lazy('core:password_reset_done')
    success_message = "Se han enviado las instrucciones para restablecer tu contraseña al correo proporcionado."

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'core/password_reset_done.html'

class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'core/password_reset_confirm.html'
    success_url = reverse_lazy('core:password_reset_complete')
    success_message = "Tu contraseña ha sido actualizada exitosamente."

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'core/password_reset_complete.html'

# Feature Views
class FlightsView(TemplateView):
    template_name = 'core/flights.html'

class HotelsView(TemplateView):
    template_name = 'core/hotels.html'

class ExperiencesView(TemplateView):
    template_name = 'core/experiences.html'

class SecurityView(TemplateView):
    template_name = 'core/security.html'

class MembershipView(TemplateView):
    template_name = 'core/membership.html'

# Dashboard Views
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_staff:
            # Admin dashboard data
            context['total_users'] = User.objects.count()
            context['active_users'] = User.objects.filter(is_active=True).count()
            context['total_flights'] = Flight.objects.count()
            context['total_bookings'] = Booking.objects.count()
            context['total_aircrafts'] = Aircraft.objects.count()
            context['monthly_revenue'] = 0  # TODO: Implement revenue calculation
        else:
            # User dashboard data
            context['user_flights'] = Flight.objects.filter(bookings__user=user).distinct()
            context['user_bookings'] = Booking.objects.filter(user=user)
            context['active_services'] = ServiceBooking.objects.filter(user=user, status='active')
        
        return context

# Static Pages
class AboutView(TemplateView):
    template_name = 'core/about.html'

class ContactView(TemplateView):
    template_name = 'core/contact.html'

class PrivacyView(TemplateView):
    template_name = 'core/privacy.html'

class TermsView(TemplateView):
    template_name = 'core/terms.html'

def home(request):
    return render(request, 'core/home.html')

# Admin Views
class AdminDashboardView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['total_flights'] = Flight.objects.count()
        context['total_bookings'] = Booking.objects.count()
        return context

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'core/profile.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 
              'date_of_birth', 'nationality', 'preferred_language',
              'dietary_preferences', 'emergency_contact_name',
              'emergency_contact_phone']
    success_url = reverse_lazy('core:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado exitosamente.')
        return super().form_valid(form)

# Admin User Views
class AdminUserListView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/users_list.html'

class AdminUserCreateView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/user_form.html'

class AdminUserDetailView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/user_detail.html'

class AdminUserUpdateView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/user_form.html'

# Admin Flights
class AdminFlightsListView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/flights_list.html'

class AdminFlightFormView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/flight_form.html'

# Admin Hotels
class AdminHotelsListView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/hotels_list.html'

class AdminHotelFormView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/hotel_form.html'

# Admin Payments
class AdminPaymentsListView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/payments_list.html'

# Admin Experiences
class AdminExperiencesListView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'core/admin/experiences_list.html'
