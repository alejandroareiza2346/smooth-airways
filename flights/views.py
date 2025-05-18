from rest_framework import viewsets, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from .models import Flight, Aircraft, CommercialFlight, Seat
# Importar nuevas vistas comerciales
from .views_commercial import (
    CommercialHomeView, CommercialFlightResultsView, CommercialFlightDetailView,
    SeatMapView, FlightBookingView, CommercialBookingConfirmationView,
    UserFlightsView, CommercialBookingDetailView, select_seat
)
from .serializers import FlightSerializer, AircraftSerializer, CommercialFlightSerializer, AdvancedCommercialFlightSerializer, SeatSerializer
from .api_simulation import get_commercial_flights
import requests
from .api_config import API_BASE_URL, API_ACCESS_KEY
import random
from rest_framework.permissions import AllowAny
from datetime import datetime
from django.shortcuts import render

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['departure_location', 'arrival_location', 'status']
    search_fields = ['flight_number', 'departure_location', 'arrival_location']
    ordering_fields = ['departure_time', 'arrival_time', 'created_at']
    ordering = ['-departure_time']

    def get_queryset(self):
        queryset = Flight.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='CONFIRMED')
        return queryset

class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type', 'manufacturer', 'is_active']
    search_fields = ['name', 'manufacturer', 'model']
    ordering = ['name']

class FlightSearchView(generics.ListAPIView):
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Flight.objects.all()
        departure = self.request.query_params.get('departure', None)
        arrival = self.request.query_params.get('arrival', None)
        date = self.request.query_params.get('date', None)

        if departure:
            queryset = queryset.filter(departure_location__icontains=departure)
        if arrival:
            queryset = queryset.filter(arrival_location__icontains=arrival)
        if date:
            queryset = queryset.filter(departure_time__date=date)

        return queryset

class AircraftAvailabilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        aircraft_type = request.query_params.get('type', None)
        date = request.query_params.get('date', None)
        
        if not aircraft_type or not date:
            return Response({'error': 'Both aircraft type and date are required'}, status=400)
            
        available_aircraft = Aircraft.objects.filter(
            type=aircraft_type,
            is_active=True
        ).exclude(
            flight__departure_time__date=date
        )
        
        serializer = AircraftSerializer(available_aircraft, many=True)
        return Response(serializer.data)

class CommercialFlightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommercialFlight.objects.all()
    serializer_class = CommercialFlightSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['origin', 'destination', 'airline']

class AdvancedCommercialFlightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommercialFlight.objects.all()
    serializer_class = AdvancedCommercialFlightSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['origin', 'destination', 'airline']
    ordering_fields = ['departure_time', 'price_economy', 'price_business', 'price_first']

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer

    def get_queryset(self):
        flight_id = self.request.query_params.get('flight_id')
        if flight_id:
            return self.queryset.filter(flight_id=flight_id)
        return self.queryset

    def perform_update(self, serializer):
        if serializer.validated_data.get('status') == Seat.SeatStatus.RESERVED:
            # Additional logic for reserving a seat can be added here
            pass
        serializer.save()

    @action(detail=False, methods=['get'], url_path='seat-map', url_name='seat-map')
    def seat_map(self, request):
        flight_id = self.query_params.get('flight_id')
        if not flight_id:
            return Response({"error": "Se requiere el ID del vuelo."}, status=400)

        seats = self.queryset.filter(flight_id=flight_id).order_by('seat_number')
        serializer = self.get_serializer(seats, many=True)
        return Response({"seat_map": serializer.data})

@api_view(['GET'])
def fetch_commercial_flights(request):
    origin = request.query_params.get('origin')
    destination = request.query_params.get('destination')
    date = request.query_params.get('date')

    if not origin or not destination or not date:
        return Response({"error": "Se requieren los parámetros 'origin', 'destination' y 'date'."}, status=400)

    flights = get_commercial_flights(origin, destination, date)
    return Response(flights)

@api_view(['GET'])
@permission_classes([AllowAny])
def fetch_real_commercial_flights(request):
    origin = request.query_params.get('origin')
    destination = request.query_params.get('destination')
    date = request.query_params.get('date')

    if not origin or not destination or not date:
        return Response({"error": "Se requieren los parámetros 'origin', 'destination' y 'date'."}, status=400)

    params = {
        'access_key': API_ACCESS_KEY,
        'dep_iata': origin,
        'arr_iata': destination,
        'flight_date': date,
        'limit': 10  # Limitar los resultados para pruebas iniciales
    }

    response = requests.get(f"{API_BASE_URL}flights", params=params)

    if response.status_code == 200:
        data = response.json()
        if 'error' in data:
            return Response({"error": data['error']['message']}, status=400)

        flights = [
            {
                'origin': flight['departure']['iata'],
                'destination': flight['arrival']['iata'],
                'airline': flight['airline']['name'],
                'departure_time': flight['departure']['scheduled'],
                'arrival_time': flight['arrival']['scheduled'],
                'duration': 'N/A',  # La API no proporciona duración directamente
                'price_economy': round(random.uniform(100, 500), 2),
                'price_business': round(random.uniform(600, 1200), 2),
                'price_first': round(random.uniform(1500, 3000), 2),
                'services': 'Wi-Fi, Entretenimiento, Comidas',
            }
            for flight in data.get('data', [])
        ]
        return Response(flights)
    else:
        return Response({"error": f"Error al consultar la API: {response.status_code}"}, status=response.status_code)

@api_view(['GET'])
@permission_classes([AllowAny])
def flight_history(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Usuario no autenticado."}, status=401)

    current_date = datetime.now()
    past_flights = CommercialFlight.objects.filter(
        arrival_time__lt=current_date
    ).order_by('-arrival_time')

    upcoming_flights = CommercialFlight.objects.filter(
        departure_time__gte=current_date
    ).order_by('departure_time')

    past_serializer = CommercialFlightSerializer(past_flights, many=True)
    upcoming_serializer = CommercialFlightSerializer(upcoming_flights, many=True)

    return Response({
        "past_flights": past_serializer.data,
        "upcoming_flights": upcoming_serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def flight_history_view(request):
    user = request.user
    if not user.is_authenticated:
        return render(request, 'core/flight_history.html', {"error": "Usuario no autenticado."})

    current_date = datetime.now()
    past_flights = CommercialFlight.objects.filter(
        arrival_time__lt=current_date
    ).order_by('-arrival_time')

    upcoming_flights = CommercialFlight.objects.filter(
        departure_time__gte=current_date
    ).order_by('departure_time')

    return render(request, 'core/flight_history.html', {
        "past_flights": past_flights,
        "upcoming_flights": upcoming_flights
    })