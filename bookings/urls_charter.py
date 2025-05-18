from django.urls import path
from .views_charter import (
    CharterHomeView, AircraftListView, AircraftDetailView,
    CharterBookingCreateView, CharterBookingConfirmationView,
    UserCharterBookingsView, CharterBookingDetailView,
    CharterBookingCancelView, calculate_charter_price
)

urlpatterns = [
    # Páginas principales de vuelos privados (charter)
    path('charter/', CharterHomeView.as_view(), name='charter_home'),
    path('charter/aircraft/', AircraftListView.as_view(), name='charter_aircraft_list'),
    path('charter/aircraft/<int:pk>/', AircraftDetailView.as_view(), name='charter_aircraft_detail'),
    
    # Reservas de vuelos charter
    path('charter/booking/<int:aircraft_id>/', CharterBookingCreateView.as_view(), name='charter_booking_create'),
    path('charter/booking/confirmation/', CharterBookingConfirmationView.as_view(), name='charter_booking_confirmation'),
    path('charter/bookings/', UserCharterBookingsView.as_view(), name='user_charter_bookings'),
    path('charter/booking/<int:pk>/', CharterBookingDetailView.as_view(), name='charter_booking_detail'),
    path('charter/booking/<int:pk>/cancel/', CharterBookingCancelView.as_view(), name='charter_booking_cancel'),
    
    # API para cálculos en tiempo real
    path('api/charter/calculate-price/', calculate_charter_price, name='api_calculate_charter_price'),
]
