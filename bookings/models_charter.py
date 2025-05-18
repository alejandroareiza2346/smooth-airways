from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import User

class PrivateAircraft(models.Model):
    """Modelo para aeronaves de alquiler privado (charter)"""
    
    class AircraftType(models.TextChoices):
        PRIVATE_JET = 'PRIVATE_JET', _('Jet Privado')
        EXECUTIVE = 'EXECUTIVE', _('Avión Ejecutivo')
        HELICOPTER = 'HELICOPTER', _('Helicóptero')
    
    # Informaci�n b�sica
    name = models.CharField(_('Nombre'), max_length=100)
    model = models.CharField(_('Modelo'), max_length=100)
    type = models.CharField(
        _('Tipo'), 
        max_length=20, 
        choices=AircraftType.choices
    )
    registration_number = models.CharField(_('Número de registro'), max_length=20, unique=True)
    capacity = models.IntegerField(_('Capacidad de pasajeros'))
    range_km = models.IntegerField(_('Alcance en kilómetros'))
    cruise_speed = models.IntegerField(_('Velocidad crucero en km/h'))
    
    # Precios y disponibilidad
    hourly_rate = models.DecimalField(_('Tarifa por hora'), max_digits=12, decimal_places=2)
    status = models.CharField(
        _('Estado'),
        max_length=50, 
        choices=[
            ('AVAILABLE', _('Disponible')), 
            ('MAINTENANCE', _('En Mantenimiento')),
            ('RESERVED', _('Reservado'))
        ], 
        default='AVAILABLE'
    )
    
    # Caracter�sticas
    description = models.TextField(_('Descripción'), blank=True)
    image = models.ImageField(_('Imagen principal'), upload_to='aircraft_images/', blank=True, null=True)
    interior_image = models.ImageField(_('Imagen del interior'), upload_to='aircraft_images/interior/', blank=True, null=True)
    has_wifi = models.BooleanField(_('Wi-Fi a bordo'), default=False)
    has_entertainment = models.BooleanField(_('Sistema de entretenimiento'), default=False)
    has_meeting_room = models.BooleanField(_('Sala de reuniones'), default=False)
    has_bedroom = models.BooleanField(_('Dormitorio'), default=False)
    has_chef = models.BooleanField(_('Servicio de chef'), default=False)
    
    # Metadatos
    created_at = models.DateTimeField(_('Fecha de creación'), default=timezone.now)
    updated_at = models.DateTimeField(_('Fecha de actualización'), auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    class Meta:
        verbose_name = _('Aeronave privada')
        verbose_name_plural = _('Aeronaves privadas')


class CharterBooking(models.Model):
    """Modelo para reservas de vuelos privados (charter)"""
    
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pendiente')
        CONFIRMED = 'CONFIRMED', _('Confirmada')
        IN_FLIGHT = 'IN_FLIGHT', _('En vuelo')
        COMPLETED = 'COMPLETED', _('Completada')
        CANCELLED = 'CANCELLED', _('Cancelada')
    
    # Informaci�n b�sica de la reserva
    booking_number = models.CharField(_('N�mero de reserva'), max_length=20, unique=True)
    client = models.ForeignKey(User, verbose_name=_('Cliente'), on_delete=models.PROTECT, related_name='charter_bookings')
    aircraft = models.ForeignKey(PrivateAircraft, verbose_name=_('Aeronave'), on_delete=models.PROTECT, related_name='bookings')
    
    # Detalles del vuelo
    departure_location = models.CharField(_('Origen'), max_length=100)
    arrival_location = models.CharField(_('Destino'), max_length=100)
    departure_datetime = models.DateTimeField(_('Fecha y hora de salida'))
    return_datetime = models.DateTimeField(_('Fecha y hora de regreso'), null=True, blank=True)
    is_round_trip = models.BooleanField(_('Es viaje redondo'), default=False)
    passenger_count = models.IntegerField(_('Número de pasajeros'))
    
    # Estado
    status = models.CharField(
        _('Estado'), 
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    
    # Precios
    base_price = models.DecimalField(_('Precio base'), max_digits=12, decimal_places=2)
    services_price = models.DecimalField(_('Precio de servicios adicionales'), max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(_('Precio total'), max_digits=12, decimal_places=2)
    
    # Metadatos
    created_at = models.DateTimeField(_('Fecha de creaci�n'), default=timezone.now)
    updated_at = models.DateTimeField(_('Fecha de actualizaci�n'), auto_now=True)
    
    # Información adicional
    notes = models.TextField(_('Notas especiales'), blank=True)
    
    def __str__(self):
        return f"Reserva {self.booking_number} - {self.client.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.booking_number:
            # Generar número único de reserva
            prefix = 'SC'  # Smooth Charter
            last_booking = CharterBooking.objects.order_by('-id').first()
            if last_booking:
                last_number = int(last_booking.booking_number[2:])
                new_number = last_number + 1
            else:
                new_number = 1000
            self.booking_number = f"{prefix}{new_number}"
        
        if not self.total_price:
            # Calcular precio total
            self.total_price = self.base_price + self.services_price
            
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('Reserva de vuelo privado')
        verbose_name_plural = _('Reservas de vuelos privados')


class CharterService(models.Model):
    """Servicios adicionales para vuelos privados"""
    
    name = models.CharField(_('Nombre del servicio'), max_length=100)
    description = models.TextField(_('Descripción'))
    price = models.DecimalField(_('Precio'), max_digits=10, decimal_places=2)
    icon = models.CharField(_('Icono'), max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.name} (${self.price})"
    
    class Meta:
        verbose_name = _('Servicio de charter')
        verbose_name_plural = _('Servicios de charter')


class BookingService(models.Model):
    """Relación entre reservas y servicios seleccionados"""
    
    booking = models.ForeignKey(CharterBooking, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(CharterService, on_delete=models.PROTECT)
    quantity = models.IntegerField(_('Cantidad'), default=1)
    
    def __str__(self):
        return f"{self.service.name} x{self.quantity} - {self.booking.booking_number}"
