from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CommercialFlightViewSet, AdvancedCommercialFlightViewSet, SeatViewSet, fetch_commercial_flights, fetch_real_commercial_flights, flight_history, flight_history_view

# Importar urls de los nuevos módulos
from .urls_commercial import urlpatterns as commercial_urlpatterns

router = DefaultRouter()
router.register(r'flights', views.FlightViewSet)
router.register(r'aircraft', views.AircraftViewSet)
router.register(r'commercial-flights', CommercialFlightViewSet, basename='commercial-flight')
router.register(r'advanced-commercial-flights', AdvancedCommercialFlightViewSet, basename='advanced-commercial-flight')
router.register(r'seats', SeatViewSet, basename='seat')

urlpatterns = [
    path('', include(router.urls)),
    path('seats/seat-map/', SeatViewSet.as_view({'get': 'seat_map'}), name='seat-map'),
    path('fetch-commercial-flights/', fetch_commercial_flights, name='fetch-commercial-flights'),    path('fetch-real-commercial-flights/', fetch_real_commercial_flights, name='fetch-real-commercial-flights'),
    path('flight-history/', flight_history, name='flight-history'),
    path('flight-history-view/', flight_history_view, name='flight-history-view'),
]

# Agregar las urls de vuelos comerciales
urlpatterns += commercial_urlpatterns