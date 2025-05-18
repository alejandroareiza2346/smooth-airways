from django.urls import path
from .views_commercial import (
    CommercialHomeView, CommercialFlightResultsView, CommercialFlightDetailView,
    SeatMapView, FlightBookingView, CommercialBookingConfirmationView,
    UserFlightsView, CommercialBookingDetailView, select_seat
)

urlpatterns = [
    # Páginas principales de vuelos comerciales
    path('commercial/', CommercialHomeView.as_view(), name='commercial_home'),
    path('commercial/results/', CommercialFlightResultsView.as_view(), name='commercial_flight_results'),
    path('commercial/flight/<int:pk>/', CommercialFlightDetailView.as_view(), name='commercial_flight_detail'),
    
    # Mapa de asientos y reservas
    path('commercial/flight/<int:pk>/seats/', SeatMapView.as_view(), name='commercial_seat_map'),
    path('commercial/flight/<int:pk>/book/', FlightBookingView.as_view(), name='commercial_flight_booking'),
    path('commercial/booking/confirmation/', CommercialBookingConfirmationView.as_view(), name='commercial_booking_confirmation'),
    
    # Mis vuelos
    path('commercial/my-flights/', UserFlightsView.as_view(), name='user_commercial_flights'),
    path('commercial/booking/<int:pk>/', CommercialBookingDetailView.as_view(), name='commercial_booking_detail'),
    
    # APIs
    path('api/booking/<int:booking_id>/passenger/<int:passenger_id>/select-seat/', select_seat, name='api_select_seat'),
]
