from rest_framework import serializers
from .models import Booking, Payment, Invoice, Aircraft, FlightService, FlightBooking
from flights.serializers import FlightSerializer
from services.serializers import ServiceBookingSerializer

class BookingSerializer(serializers.ModelSerializer):
    flight_details = FlightSerializer(source='flight', read_only=True)
    service_booking_details = ServiceBookingSerializer(source='service_bookings', many=True, read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'booking_number', 'client', 'status',
            'flight', 'flight_details', 'service_bookings',
            'service_booking_details', 'subtotal', 'tax',
            'discount', 'total', 'stripe_payment_intent_id',
            'payment_status', 'deposit_amount', 'deposit_paid',
            'created_at', 'updated_at', 'cancelled_at',
            'cancellation_reason', 'special_requests',
            'internal_notes'
        ]
        read_only_fields = [
            'booking_number', 'subtotal', 'tax', 'total',
            'stripe_payment_intent_id', 'payment_status',
            'created_at', 'updated_at', 'cancelled_at'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'payment_type', 'amount',
            'status', 'stripe_payment_intent_id',
            'stripe_charge_id', 'payment_method',
            'payment_date', 'description', 'receipt_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'stripe_payment_intent_id', 'stripe_charge_id',
            'receipt_url', 'created_at', 'updated_at'
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id', 'booking', 'invoice_number', 'status',
            'subtotal', 'tax', 'discount', 'total',
            'issue_date', 'due_date', 'paid_date',
            'pdf_file', 'notes', 'payment_terms',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'invoice_number', 'created_at', 'updated_at'
        ]

class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = '__all__'

class FlightServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightService
        fields = '__all__'

class FlightBookingSerializer(serializers.ModelSerializer):
    aircraft = AircraftSerializer(read_only=True)
    services = FlightServiceSerializer(many=True, read_only=True)

    class Meta:
        model = FlightBooking
        fields = '__all__'