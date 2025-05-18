from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import stripe
from .models import Booking, Payment, Invoice, Aircraft, FlightService, FlightBooking
# Importar nuevas vistas de charter
from .views_charter import (
    CharterHomeView, AircraftListView, AircraftDetailView,
    CharterBookingCreateView, CharterBookingConfirmationView,
    UserCharterBookingsView, CharterBookingDetailView,
    CharterBookingCancelView, calculate_charter_price
)
from .serializers import BookingSerializer, PaymentSerializer, InvoiceSerializer, AircraftSerializer, FlightServiceSerializer, FlightBookingSerializer
from rest_framework.decorators import action
from django.core.mail import send_mail
from accounts.mixins import AdminRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

stripe.api_key = settings.STRIPE_SECRET_KEY

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(client=self.request.user)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(booking__client=self.request.user)

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Invoice.objects.all()
        return Invoice.objects.filter(booking__client=self.request.user)

class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        try:
            booking = Booking.objects.get(id=booking_id, client=request.user)
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(booking.total * 100),  # Convert to cents
                        'product_data': {
                            'name': f'Booking {booking.booking_number}',
                            'description': f'Flight from {booking.flight.departure_location} to {booking.flight.arrival_location}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/booking/success/'),
                cancel_url=request.build_absolute_uri('/booking/cancel/'),
                metadata={
                    'booking_id': booking.id,
                    'booking_number': booking.booking_number,
                }
            )
            
            return Response({'session_id': session.id})
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class StripeWebhookView(APIView):
    permission_classes = []  # No authentication required for webhooks

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response(status=400)
        except stripe.error.SignatureVerificationError:
            return Response(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            booking_id = session['metadata']['booking_id']
            
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.status = Booking.BookingStatus.CONFIRMED
                booking.stripe_payment_intent_id = session['payment_intent']
                booking.payment_status = 'PAID'
                booking.save()
                
                # Create payment record
                Payment.objects.create(
                    booking=booking,
                    payment_type=Payment.PaymentType.FULL,
                    amount=booking.total,
                    status=Payment.PaymentStatus.COMPLETED,
                    stripe_payment_intent_id=session['payment_intent'],
                    payment_method='card',
                    description=f'Full payment for booking {booking.booking_number}'
                )
            except Booking.DoesNotExist:
                return Response(status=404)

        return Response(status=200)

class GenerateInvoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
            if not request.user.is_staff and request.user != booking.client:
                return Response({'error': 'Not authorized'}, status=403)
            
            invoice = Invoice.objects.create(
                booking=booking,
                status=Invoice.InvoiceStatus.ISSUED,
                subtotal=booking.subtotal,
                tax=booking.tax,
                discount=booking.discount,
                total=booking.total,
                issue_date=booking.created_at.date(),
                due_date=booking.created_at.date(),  # Set appropriate due date logic
                payment_terms='Payment due immediately'
            )
            
            # Generate PDF logic here
            # ...
            
            return Response({
                'invoice_id': invoice.id,
                'invoice_number': invoice.invoice_number
            })
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class AircraftViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [permissions.AllowAny]

class FlightServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FlightService.objects.all()
    serializer_class = FlightServiceSerializer
    permission_classes = [permissions.AllowAny]

class FlightBookingViewSet(viewsets.ModelViewSet):
    queryset = FlightBooking.objects.all()
    serializer_class = FlightBookingSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)

        # Send confirmation email
        send_mail(
            'Confirmación de Reserva - Smooth Airlines',
            f'Su reserva con ID {booking.id} ha sido confirmada. Detalles: \n\n'
            f'Avión: {booking.aircraft.name}\n'
            f'Origen: {booking.departure_location}\n'
            f'Destino: {booking.arrival_location}\n'
            f'Fecha de salida: {booking.departure_time}\n'
            f'Precio total: ${booking.total_price}',
            'no-reply@smooth-airlines.com',
            [self.request.user.email],
            fail_silently=False,
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_bookings(self, request):
        user = request.user
        bookings = self.queryset.filter(user=user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

class AircraftListView(AdminRequiredMixin, ListView):
    model = Aircraft
    template_name = 'bookings/aircraft_list.html'
    context_object_name = 'aircrafts'

class AircraftCreateView(AdminRequiredMixin, CreateView):
    model = Aircraft
    fields = ['name', 'model', 'capacity', 'status']
    template_name = 'bookings/aircraft_form.html'
    success_url = '/admin-panel/aeronaves/'

class AircraftUpdateView(AdminRequiredMixin, UpdateView):
    model = Aircraft
    fields = ['name', 'model', 'capacity', 'status']
    template_name = 'bookings/aircraft_form.html'
    success_url = '/admin-panel/aeronaves/'

class AircraftDeleteView(AdminRequiredMixin, DeleteView):
    model = Aircraft
    template_name = 'bookings/aircraft_confirm_delete.html'
    success_url = '/admin-panel/aeronaves/'