from rest_framework import serializers
from .models import Vehicle, SecurityService, ConciergeService, ServiceBooking, Service

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            'id', 'name', 'type', 'manufacturer', 'model',
            'year', 'color', 'license_plate', 'passenger_capacity',
            'is_armored', 'hourly_rate', 'is_available',
            'current_location', 'main_image'
        ]

class SecurityServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityService
        fields = [
            'id', 'name', 'level', 'description', 'personnel_count',
            'armed_personnel', 'includes_vehicle', 'hourly_rate',
            'minimum_hours'
        ]

class ConciergeServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConciergeService
        fields = [
            'id', 'name', 'type', 'description', 'provider_name',
            'location', 'price', 'is_available', 'requires_advance_notice',
            'advance_notice_hours'
        ]

class ServiceBookingSerializer(serializers.ModelSerializer):
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)
    security_service_details = SecurityServiceSerializer(source='security_service', read_only=True)
    concierge_service_details = ConciergeServiceSerializer(source='concierge_service', read_only=True)
    
    class Meta:
        model = ServiceBooking
        fields = [
            'id', 'client', 'flight', 'vehicle', 'vehicle_details',
            'security_service', 'security_service_details',
            'concierge_service', 'concierge_service_details',
            'start_time', 'end_time', 'location', 'status',
            'base_price', 'additional_charges', 'total_price',
            'special_requests', 'internal_notes'
        ]
        read_only_fields = ['total_price']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id', 'type', 'name', 'description', 'price',
            'start_date', 'end_date', 'location', 'status',
            'vehicle_type', 'security_level', 'hotel_name',
            'room_type', 'special_requests', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """
        Validar que la fecha de inicio sea anterior a la fecha de fin
        """
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "La fecha de inicio debe ser anterior a la fecha de fin"
                )
        return data 