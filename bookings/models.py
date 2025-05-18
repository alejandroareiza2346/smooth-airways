from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from flights.models import Flight
from services.models import ServiceBooking

# Importamos modelos de charter
from .models_charter import PrivateAircraft, CharterBooking, CharterService, BookingService

class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING = 'PENDING', _('Pending Payment')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        REFUNDED = 'REFUNDED', _('Refunded')

    # Basic booking info
    booking_number = models.CharField(max_length=20, unique=True)
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bookings')
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.DRAFT
    )
    
    # Related services
    flight = models.OneToOneField(Flight, on_delete=models.PROTECT, related_name='booking')
    service_bookings = models.ManyToManyField(ServiceBooking, blank=True, related_name='main_booking')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment info
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=20, default='UNPAID')
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_paid = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    cancellation_reason = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Booking {self.booking_number} - {self.client.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.booking_number:
            # Generate a unique booking number
            prefix = 'SB'  # Smooth Booking
            last_booking = Booking.objects.order_by('-id').first()
            if last_booking:
                last_number = int(last_booking.booking_number[2:])
                new_number = last_number + 1
            else:
                new_number = 1000
            self.booking_number = f"{prefix}{new_number}"
        
        # Calculate total
        self.total = self.subtotal + self.tax - self.discount
        
        super().save(*args, **kwargs)

class Payment(models.Model):
    class PaymentType(models.TextChoices):
        DEPOSIT = 'DEPOSIT', _('Deposit')
        FULL = 'FULL', _('Full Payment')
        ADDITIONAL = 'ADDITIONAL', _('Additional Charge')
        REFUND = 'REFUND', _('Refund')

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        REFUNDED = 'REFUNDED', _('Refunded')

    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name='payments')
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Payment details
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    description = models.TextField(blank=True)
    receipt_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.booking.booking_number}"

class Invoice(models.Model):
    class InvoiceStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        ISSUED = 'ISSUED', _('Issued')
        PAID = 'PAID', _('Paid')
        VOID = 'VOID', _('Void')

    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name='invoices')
    invoice_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT
    )
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    # PDF storage
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    payment_terms = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.booking.booking_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate a unique invoice number
            prefix = 'SI'  # Smooth Invoice
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number[2:])
                new_number = last_number + 1
            else:
                new_number = 1000
            self.invoice_number = f"{prefix}{new_number}"
        
        # Calculate total
        self.total = self.subtotal + self.tax - self.discount
        
        super().save(*args, **kwargs)

class Aircraft(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    capacity = models.IntegerField()
    status = models.CharField(max_length=50, choices=[('AVAILABLE', 'Disponible'), ('MAINTENANCE', 'En Mantenimiento')], default='AVAILABLE')

    def __str__(self):
        return f"{self.name} ({self.model})"

class FlightService(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class FlightBooking(models.Model):
    class BookingStatus(models.TextChoices):
        PENDIENTE = 'PENDIENTE', _('Pendiente')
        CONFIRMADA = 'CONFIRMADA', _('Confirmada')
        VOLANDO = 'VOLANDO', _('Volando')
        COMPLETADA = 'COMPLETADA', _('Completada')

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='flight_bookings')
    aircraft = models.ForeignKey(Aircraft, on_delete=models.PROTECT, related_name='bookings')
    services = models.ManyToManyField(FlightService, blank=True, related_name='bookings')
    departure_location = models.CharField(max_length=100)
    arrival_location = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    return_time = models.DateTimeField(null=True, blank=True)
    passengers = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDIENTE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.user.email}"

    def save(self, *args, **kwargs):
        # Validate passenger count
        if self.passengers > self.aircraft.capacity:
            raise ValueError("El número de pasajeros excede la capacidad del avión.")

        # Calculate total price
        flight_duration_hours = (self.return_time - self.departure_time).total_seconds() / 3600
        aircraft_cost = flight_duration_hours * self.aircraft.hourly_rate
        services_cost = sum(service.price for service in self.services.all())
        self.total_price = aircraft_cost + services_cost

        super().save(*args, **kwargs)