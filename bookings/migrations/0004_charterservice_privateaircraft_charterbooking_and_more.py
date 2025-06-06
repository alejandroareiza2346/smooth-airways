# Generated by Django 5.0.1 on 2025-05-18 07:45

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_remove_aircraft_hourly_rate_remove_aircraft_image_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CharterService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre del servicio')),
                ('description', models.TextField(verbose_name='Descripción')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio')),
                ('icon', models.CharField(blank=True, max_length=50, verbose_name='Icono')),
            ],
            options={
                'verbose_name': 'Servicio de charter',
                'verbose_name_plural': 'Servicios de charter',
            },
        ),
        migrations.CreateModel(
            name='PrivateAircraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('model', models.CharField(max_length=100, verbose_name='Modelo')),
                ('type', models.CharField(choices=[('PRIVATE_JET', 'Jet Privado'), ('EXECUTIVE', 'Avión Ejecutivo'), ('HELICOPTER', 'Helicóptero')], max_length=20, verbose_name='Tipo')),
                ('registration_number', models.CharField(max_length=20, unique=True, verbose_name='Número de registro')),
                ('capacity', models.IntegerField(verbose_name='Capacidad de pasajeros')),
                ('range_km', models.IntegerField(verbose_name='Alcance en kilómetros')),
                ('cruise_speed', models.IntegerField(verbose_name='Velocidad crucero en km/h')),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Tarifa por hora')),
                ('status', models.CharField(choices=[('AVAILABLE', 'Disponible'), ('MAINTENANCE', 'En Mantenimiento'), ('RESERVED', 'Reservado')], default='AVAILABLE', max_length=50, verbose_name='Estado')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('image', models.ImageField(blank=True, null=True, upload_to='aircraft_images/', verbose_name='Imagen principal')),
                ('interior_image', models.ImageField(blank=True, null=True, upload_to='aircraft_images/interior/', verbose_name='Imagen del interior')),
                ('has_wifi', models.BooleanField(default=False, verbose_name='Wi-Fi a bordo')),
                ('has_entertainment', models.BooleanField(default=False, verbose_name='Sistema de entretenimiento')),
                ('has_meeting_room', models.BooleanField(default=False, verbose_name='Sala de reuniones')),
                ('has_bedroom', models.BooleanField(default=False, verbose_name='Dormitorio')),
                ('has_chef', models.BooleanField(default=False, verbose_name='Servicio de chef')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
            ],
            options={
                'verbose_name': 'Aeronave privada',
                'verbose_name_plural': 'Aeronaves privadas',
            },
        ),
        migrations.CreateModel(
            name='CharterBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_number', models.CharField(max_length=20, unique=True, verbose_name='N�mero de reserva')),
                ('departure_location', models.CharField(max_length=100, verbose_name='Origen')),
                ('arrival_location', models.CharField(max_length=100, verbose_name='Destino')),
                ('departure_datetime', models.DateTimeField(verbose_name='Fecha y hora de salida')),
                ('return_datetime', models.DateTimeField(blank=True, null=True, verbose_name='Fecha y hora de regreso')),
                ('is_round_trip', models.BooleanField(default=False, verbose_name='Es viaje redondo')),
                ('passenger_count', models.IntegerField(verbose_name='Número de pasajeros')),
                ('status', models.CharField(choices=[('PENDING', 'Pendiente'), ('CONFIRMED', 'Confirmada'), ('IN_FLIGHT', 'En vuelo'), ('COMPLETED', 'Completada'), ('CANCELLED', 'Cancelada')], default='PENDING', max_length=20, verbose_name='Estado')),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Precio base')),
                ('services_price', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Precio de servicios adicionales')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Precio total')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de creaci�n')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualizaci�n')),
                ('notes', models.TextField(blank=True, verbose_name='Notas especiales')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='charter_bookings', to=settings.AUTH_USER_MODEL, verbose_name='Cliente')),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='bookings.privateaircraft', verbose_name='Aeronave')),
            ],
            options={
                'verbose_name': 'Reserva de vuelo privado',
                'verbose_name_plural': 'Reservas de vuelos privados',
            },
        ),
        migrations.CreateModel(
            name='BookingService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='Cantidad')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='bookings.charterbooking')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bookings.charterservice')),
            ],
        ),
    ]
