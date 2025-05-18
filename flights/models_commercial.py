from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import User
import uuid

class CommercialFlight(models.Model):
    """Modelo para vuelos comerciales ofrecidos por aerolíneas"""
    
    class CabinClass(models.TextChoices):
        ECONOMY = 'ECONOMY', _('Económica')
        PREMIUM_ECONOMY = 'PREMIUM_ECONOMY', _('Económica Premium')
        BUSINESS = 'BUSINESS', _('Negocios')
        FIRST = 'FIRST', _('Primera')
    
    # Información básica del vuelo
    flight_number = models.CharField(_('Número de vuelo'), max_length=10)
    airline = models.CharField(_('Aerolínea'), max_length=100)
    airline_logo = models.ImageField(_('Logo de aerolínea'), upload_to='airline_logos/', blank=True, null=True)
      # Origen y destino
    origin = models.CharField(_('Aeropuerto de origen'), max_length=100, default='')
    origin_code = models.CharField(_('Código IATA origen'), max_length=3, default='')
    destination = models.CharField(_('Aeropuerto de destino'), max_length=100, default='')
    destination_code = models.CharField(_('Código IATA destino'), max_length=3, default='')
    
    # Horarios
    departure_time = models.DateTimeField(_('Fecha y hora de salida'))
    arrival_time = models.DateTimeField(_('Fecha y hora de llegada'))
    duration = models.DurationField(_('Duración'))
    
    # Escalas
    has_stops = models.BooleanField(_('Tiene escalas'), default=False)
    stops_count = models.IntegerField(_('Número de escalas'), default=0)
    stops_detail = models.JSONField(_('Detalles de escalas'), default=list, blank=True)
    
    # Precios por clase
    price_economy = models.DecimalField(_('Precio clase económica'), max_digits=10, decimal_places=2)
    price_premium_economy = models.DecimalField(_('Precio clase económica premium'), max_digits=10, decimal_places=2, null=True, blank=True)
    price_business = models.DecimalField(_('Precio clase negocios'), max_digits=10, decimal_places=2, null=True, blank=True)
    price_first = models.DecimalField(_('Precio primera clase'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Servicios a bordo
    has_wifi = models.BooleanField(_('Wi-Fi a bordo'), default=False)
    has_entertainment = models.BooleanField(_('Entretenimiento a bordo'), default=False)
    has_power_outlets = models.BooleanField(_('Enchufes eléctricos'), default=False)
    has_complimentary_meal = models.BooleanField(_('Comida incluida'), default=False)
    
    # Estado del vuelo
    status = models.CharField(
        _('Estado'), 
        max_length=20,
        choices=[
            ('SCHEDULED', _('Programado')),
            ('DELAYED', _('Retrasado')),
            ('BOARDING', _('Abordando')),
            ('IN_AIR', _('En vuelo')),
            ('LANDED', _('Aterrizado')),
            ('CANCELLED', _('Cancelado')),
        ],
        default='SCHEDULED'
    )    # Avión
    aircraft_type = models.CharField(_('Tipo de aeronave'), max_length=100, blank=True)    
    # Metadatos
    created_at = models.DateTimeField(_('Fecha de creación'), default=timezone.now)
    updated_at = models.DateTimeField(_('Fecha de actualización'), auto_now=True)
    
    # API relacionada
    source_api = models.CharField(_('API de origen'), max_length=50, blank=True)
    external_id = models.CharField(_('ID externo'), max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.airline} {self.flight_number} ({self.origin_code} - {self.destination_code})"
    
    class Meta:
        verbose_name = _('Vuelo comercial')
        verbose_name_plural = _('Vuelos comerciales')
        ordering = ['departure_time']


class CommercialBooking(models.Model):
    """Modelo para reservas de vuelos comerciales"""
    
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pendiente')
        CONFIRMED = 'CONFIRMED', _('Confirmada')
        CHECKED_IN = 'CHECKED_IN', _('Facturado')
        COMPLETED = 'COMPLETED', _('Completado')
        CANCELLED = 'CANCELLED', _('Cancelado')
    
    # Información básica de la reserva
    booking_reference = models.CharField(_('Código de reserva'), max_length=10, unique=True)
    client = models.ForeignKey(User, on_delete=models.PROTECT, related_name='commercial_bookings')
    flight = models.ForeignKey(CommercialFlight, on_delete=models.PROTECT, related_name='bookings')
    
    # Detalles de la reserva
    cabin_class = models.CharField(
        _('Clase'), 
        max_length=20, 
        choices=CommercialFlight.CabinClass.choices,
        default=CommercialFlight.CabinClass.ECONOMY
    )
    
    # Estado
    status = models.CharField(
        _('Estado'),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
      # Precios
    price = models.DecimalField(_('Precio'), max_digits=10, decimal_places=2)
    tax = models.DecimalField(_('Impuestos'), max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(_('Precio total'), max_digits=10, decimal_places=2)
    
    # Metadatos
    booking_date = models.DateTimeField(_('Fecha de reserva'), default=timezone.now)
    updated_at = models.DateTimeField(_('Fecha de actualización'), auto_now=True)
    
    def __str__(self):
        return f"Reserva {self.booking_reference} - {self.flight}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generar código de reserva único
            ref = uuid.uuid4().hex[:6].upper()
            while CommercialBooking.objects.filter(booking_reference=ref).exists():
                ref = uuid.uuid4().hex[:6].upper()
            self.booking_reference = ref
        
        # Calcular precio total
        if not self.total_price:
            self.total_price = self.price + self.tax
            
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Reserva de vuelo comercial')
        verbose_name_plural = _('Reservas de vuelos comerciales')


class Passenger(models.Model):
    """Modelo para pasajeros en una reserva"""
    
    booking = models.ForeignKey(CommercialBooking, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(_('Nombre'), max_length=100)
    last_name = models.CharField(_('Apellido'), max_length=100)
    document_type = models.CharField(_('Tipo de documento'), max_length=50)
    document_number = models.CharField(_('Número de documento'), max_length=50)
    date_of_birth = models.DateField(_('Fecha de nacimiento'))
    
    # Información de asiento
    seat_number = models.CharField(_('Número de asiento'), max_length=10, blank=True)
    has_checked_in = models.BooleanField(_('Ha hecho check-in'), default=False)
    
    # Extras
    special_assistance = models.BooleanField(_('Necesita asistencia especial'), default=False)
    special_meal = models.CharField(_('Comida especial'), max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.booking.booking_reference}"
    
    class Meta:
        verbose_name = _('Pasajero')
        verbose_name_plural = _('Pasajeros')


class Seat(models.Model):
    """Modelo para asientos en vuelos comerciales"""
    
    class SeatType(models.TextChoices):
        STANDARD = 'STANDARD', _('Estándar')
        EXIT_ROW = 'EXIT_ROW', _('Fila de salida')
        EXTRA_LEGROOM = 'EXTRA_LEGROOM', _('Espacio adicional')
        PREFERRED = 'PREFERRED', _('Preferente')
        WINDOW = 'WINDOW', _('Ventana')
        MIDDLE = 'MIDDLE', _('Centro')
        AISLE = 'AISLE', _('Pasillo')
    
    class SeatStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', _('Disponible')
        RESERVED = 'RESERVED', _('Reservado')
        OCCUPIED = 'OCCUPIED', _('Ocupado')
        BLOCKED = 'BLOCKED', _('Bloqueado')
    
    # Información del asiento
    flight = models.ForeignKey(CommercialFlight, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(_('Número de asiento'), max_length=10)
    seat_row = models.IntegerField(_('Fila'))
    seat_column = models.CharField(_('Columna'), max_length=1)
    cabin_class = models.CharField(
        _('Clase'), 
        max_length=20,
        choices=CommercialFlight.CabinClass.choices,
        default=CommercialFlight.CabinClass.ECONOMY
    )
    
    # Tipo y estado
    seat_type = models.CharField(
        _('Tipo de asiento'),
        max_length=20,
        choices=SeatType.choices,
        default=SeatType.STANDARD
    )
    status = models.CharField(
        _('Estado'),
        max_length=20,
        choices=SeatStatus.choices,
        default=SeatStatus.AVAILABLE
    )
    
    # Precio adicional (si aplica)
    extra_price = models.DecimalField(_('Precio adicional'), max_digits=10, decimal_places=2, default=0)
    
    # Pasajero asignado (si existe)
    passenger = models.ForeignKey(Passenger, on_delete=models.SET_NULL, null=True, blank=True, related_name='seat')
    
    def __str__(self):
        return f"{self.seat_number} - {self.flight.flight_number} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = _('Asiento')
        verbose_name_plural = _('Asientos')
        unique_together = ('flight', 'seat_number')
        ordering = ['seat_row', 'seat_column']
