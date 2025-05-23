# Generated by Django 5.0.1 on 2025-05-18 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_aircraft_flightservice_flightbooking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aircraft',
            name='hourly_rate',
        ),
        migrations.RemoveField(
            model_name='aircraft',
            name='image',
        ),
        migrations.RemoveField(
            model_name='aircraft',
            name='manufacturer',
        ),
        migrations.RemoveField(
            model_name='aircraft',
            name='type',
        ),
        migrations.AddField(
            model_name='aircraft',
            name='status',
            field=models.CharField(choices=[('AVAILABLE', 'Disponible'), ('MAINTENANCE', 'En Mantenimiento')], default='AVAILABLE', max_length=50),
        ),
        migrations.AlterField(
            model_name='aircraft',
            name='capacity',
            field=models.IntegerField(),
        ),
    ]
