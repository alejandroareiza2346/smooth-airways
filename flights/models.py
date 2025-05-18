from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

# Importamos modelos de vuelos comerciales 
from .models_commercial import CommercialFlight, CommercialBooking, Passenger, Seat

class Aircraft(models.Model):
    class AircraftType(models.TextChoices):
        LIGHT_JET = 'LIGHT', _('Light Jet')
        MIDSIZE_JET = 'MIDSIZE', _('Midsize Jet')
        SUPER_MIDSIZE = 'SUPER_MIDSIZE', _('Super Midsize Jet')
        HEAVY_JET = 'HEAVY', _('Heavy Jet')
        ULTRA_LONG_RANGE = 'ULTRA', _('Ultra Long Range')
        VIP_AIRLINER = 'VIP', _('VIP Airliner')

    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20,
        choices=AircraftType.choices
    )
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    year_manufactured = models.IntegerField()
    passenger_capacity = models.IntegerField()
    range_nm = models.IntegerField(help_text="Range in nautical miles")
    cruise_speed_kts = models.IntegerField(help_text="Cruise speed in knots")
    
    # Amenities
    has_wifi = models.BooleanField(default=False)
    has_phone = models.BooleanField(default=False)
    has_entertainment = models.BooleanField(default=False)
    has_meeting_room = models.BooleanField(default=False)
    has_bedroom = models.BooleanField(default=False)
    
    # Media
    main_image = models.ImageField(upload_to='aircraft/', null=True, blank=True)
    floor_plan = models.ImageField(upload_to='aircraft/floorplans/', null=True, blank=True)
    
    # Pricing
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_hours = models.IntegerField(default=2)
    
    # Status
    is_active = models.BooleanField(default=True)
    maintenance_status = models.CharField(max_length=50, default='Available')
    current_location = models.CharField(max_length=100)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.manufacturer} {self.model} ({self.registration_number})"

class Flight(models.Model):
    class FlightStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    # Basic flight info
    flight_number = models.CharField(max_length=20, unique=True)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.PROTECT)
    departure_location = models.CharField(max_length=100)
    arrival_location = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    
    # Client info
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='flights')
    passenger_count = models.IntegerField()
    passenger_manifest = models.JSONField(default=list)
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=FlightStatus.choices,
        default=FlightStatus.PENDING
    )
    actual_departure_time = models.DateTimeField(null=True, blank=True)
    actual_arrival_time = models.DateTimeField(null=True, blank=True)
    flight_duration = models.DurationField(null=True, blank=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_services_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Flight details
    flight_plan = models.TextField(blank=True)
    catering_requirements = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    
    # Weather and conditions
    weather_briefing = models.TextField(blank=True)
    flight_conditions = models.CharField(max_length=50, blank=True)
    
    # Crew
    pilot_names = models.JSONField(default=list)
    cabin_crew_names = models.JSONField(default=list)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Flight {self.flight_number}: {self.departure_location} to {self.arrival_location}"

    def save(self, *args, **kwargs):
        if not self.flight_number:
            # Generate a unique flight number
            prefix = 'SA'  # Smooth Airlines
            last_flight = Flight.objects.order_by('-id').first()
            if last_flight:
                last_number = int(last_flight.flight_number[2:])
                new_number = last_number + 1
            else:
                new_number = 1000
            self.flight_number = f"{prefix}{new_number}"
        
        # Calculate total price
        self.total_price = self.base_price + self.additional_services_price
        
        super().save(*args, **kwargs)

# Eliminamos la clase CommercialFlight para usar la del módulo models_commercial.py
# Nota: La clase original se ha movido a models_commercial.py

# La clase Seat también ha sido movida a models_commercial.py