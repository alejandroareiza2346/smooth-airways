from rest_framework import serializers
from .models import Flight, Aircraft, CommercialFlight, Seat

class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    aircraft_details = AircraftSerializer(source='aircraft', read_only=True)
    
    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'aircraft', 'aircraft_details',
            'departure_location', 'arrival_location',
            'departure_time', 'arrival_time',
            'passenger_count', 'status', 'base_price',
            'additional_services_price', 'total_price',
            'catering_requirements', 'special_requests',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['flight_number', 'total_price']

    def validate(self, data):
        """
        Validate that departure time is before arrival time
        and passenger count doesn't exceed aircraft capacity
        """
        if data.get('departure_time') and data.get('arrival_time'):
            if data['departure_time'] >= data['arrival_time']:
                raise serializers.ValidationError(
                    "La hora de salida debe ser anterior a la hora de llegada"
                )
        
        if data.get('aircraft') and data.get('passenger_count'):
            if data['passenger_count'] > data['aircraft'].passenger_capacity:
                raise serializers.ValidationError(
                    f"El número de pasajeros excede la capacidad de la aeronave "
                    f"({data['aircraft'].passenger_capacity} pasajeros)"
                )
        
        return data

class CommercialFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommercialFlight
        fields = '__all__'

class AdvancedCommercialFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommercialFlight
        fields = [
            'id', 'origin', 'destination', 'airline', 'departure_time', 'arrival_time',
            'duration', 'stops', 'stop_details', 'price_economy', 'price_business',
            'price_first', 'services', 'image', 'has_wifi', 'has_entertainment',
            'has_power_outlets', 'has_meals', 'has_luxury_seating'
        ]

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'flight', 'seat_number', 'cabin_class', 'status']