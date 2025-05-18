from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from flights.models import Flight

class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        SEDAN = 'SEDAN', _('Luxury Sedan')
        SUV = 'SUV', _('Luxury SUV')
        LIMOUSINE = 'LIMO', _('Limousine')
        VAN = 'VAN', _('Executive Van')
        ARMORED = 'ARMORED', _('Armored Vehicle')

    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10,
        choices=VehicleType.choices
    )
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=50)
    license_plate = models.CharField(max_length=20)
    passenger_capacity = models.IntegerField()
    is_armored = models.BooleanField(default=False)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    current_location = models.CharField(max_length=100)
    main_image = models.ImageField(upload_to='vehicles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.year} {self.manufacturer} {self.model}"

class SecurityService(models.Model):
    class SecurityLevel(models.TextChoices):
        BASIC = 'BASIC', _('Basic')
        ADVANCED = 'ADVANCED', _('Advanced')
        EXECUTIVE = 'EXECUTIVE', _('Executive')
        DIPLOMATIC = 'DIPLOMATIC', _('Diplomatic')

    name = models.CharField(max_length=100)
    level = models.CharField(
        max_length=10,
        choices=SecurityLevel.choices
    )
    description = models.TextField()
    personnel_count = models.IntegerField()
    armed_personnel = models.BooleanField(default=False)
    includes_vehicle = models.BooleanField(default=False)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_hours = models.IntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"

class ConciergeService(models.Model):
    class ServiceType(models.TextChoices):
        RESTAURANT = 'RESTAURANT', _('Restaurant Reservation')
        HOTEL = 'HOTEL', _('Hotel Booking')
        EVENT = 'EVENT', _('Event Access')
        SHOPPING = 'SHOPPING', _('Personal Shopping')
        WELLNESS = 'WELLNESS', _('Wellness & Spa')
        EXPERIENCE = 'EXPERIENCE', _('Unique Experience')

    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20,
        choices=ServiceType.choices
    )
    description = models.TextField()
    provider_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    requires_advance_notice = models.BooleanField(default=False)
    advance_notice_hours = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} at {self.provider_name}"

class ServiceBooking(models.Model):
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='service_bookings')
    flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_bookings')
    
    # Service references (optional based on booking type)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, null=True, blank=True)
    security_service = models.ForeignKey(SecurityService, on_delete=models.PROTECT, null=True, blank=True)
    concierge_service = models.ForeignKey(ConciergeService, on_delete=models.PROTECT, null=True, blank=True)
    
    # Booking details
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Notes and requirements
    special_requests = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        service_type = "Multiple Services"
        if self.vehicle and not (self.security_service or self.concierge_service):
            service_type = "Vehicle Service"
        elif self.security_service and not (self.vehicle or self.concierge_service):
            service_type = "Security Service"
        elif self.concierge_service and not (self.vehicle or self.security_service):
            service_type = "Concierge Service"
        
        return f"{service_type} for {self.client.get_full_name()} on {self.start_time.date()}"

    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.base_price + self.additional_charges
        super().save(*args, **kwargs)

class Service(models.Model):
    class ServiceType(models.TextChoices):
        TRANSPORT = 'TRANSPORT', _('Transporte de Lujo')
        SECURITY = 'SECURITY', _('Seguridad Personal')
        CONCIERGE = 'CONCIERGE', _('Servicio Concierge')
        CATERING = 'CATERING', _('Catering Premium')
        HOTEL = 'HOTEL', _('Reserva de Hotel')
        EXPERIENCE = 'EXPERIENCE', _('Experiencia VIP')

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    type = models.CharField(max_length=20, choices=ServiceType.choices)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pendiente'),
            ('CONFIRMED', 'Confirmado'),
            ('IN_PROGRESS', 'En Progreso'),
            ('COMPLETED', 'Completado'),
            ('CANCELLED', 'Cancelado'),
        ],
        default='PENDING'
    )
    
    # Campos específicos para cada tipo de servicio
    vehicle_type = models.CharField(max_length=100, blank=True)  # Para TRANSPORT
    security_level = models.CharField(max_length=50, blank=True)  # Para SECURITY
    hotel_name = models.CharField(max_length=200, blank=True)    # Para HOTEL
    room_type = models.CharField(max_length=100, blank=True)     # Para HOTEL
    special_requests = models.TextField(blank=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('servicio')
        verbose_name_plural = _('servicios') 