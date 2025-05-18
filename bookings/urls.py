from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AircraftViewSet, FlightServiceViewSet, FlightBookingViewSet, AircraftListView, AircraftCreateView, AircraftUpdateView, AircraftDeleteView
from . import views

router = DefaultRouter()
router.register(r'aircrafts', AircraftViewSet, basename='aircraft')
router.register(r'services', FlightServiceViewSet, basename='service')
router.register(r'bookings', FlightBookingViewSet, basename='booking')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')

# Importar urls de los nuevos módulos
from .urls_charter import urlpatterns as charter_urlpatterns

urlpatterns = [
    path('checkout/session/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('invoice/generate/<int:booking_id>/', views.GenerateInvoiceView.as_view(), name='generate-invoice'),
    path('my-bookings/', FlightBookingViewSet.as_view({'get': 'my_bookings'}), name='my-bookings'),
    path('', include(router.urls)),
    path('admin-panel/aeronaves/', AircraftListView.as_view(), name='aircraft_list'),
    path('admin-panel/aeronaves/crear/', AircraftCreateView.as_view(), name='aircraft_create'),    path('admin-panel/aeronaves/<int:pk>/editar/', AircraftUpdateView.as_view(), name='aircraft_edit'),
    path('admin-panel/aeronaves/<int:pk>/eliminar/', AircraftDeleteView.as_view(), name='aircraft_delete'),
]

# Agregar las urls de charter 
urlpatterns += charter_urlpatterns