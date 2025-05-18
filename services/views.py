from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle, SecurityService, ConciergeService, ServiceBooking, Service
from .serializers import (
    VehicleSerializer, SecurityServiceSerializer,
    ConciergeServiceSerializer, ServiceBookingSerializer,
    ServiceSerializer
)

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

class SecurityServiceViewSet(viewsets.ModelViewSet):
    queryset = SecurityService.objects.all()
    serializer_class = SecurityServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

class ConciergeServiceViewSet(viewsets.ModelViewSet):
    queryset = ConciergeService.objects.all()
    serializer_class = ConciergeServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

class ServiceBookingViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ServiceBooking.objects.all()
        return ServiceBooking.objects.filter(client=self.request.user)

class ServiceSearchView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        service_type = self.request.query_params.get('type', None)
        if not service_type:
            return []

        if service_type == 'vehicle':
            return Vehicle.objects.filter(is_available=True)
        elif service_type == 'security':
            return SecurityService.objects.all()
        elif service_type == 'concierge':
            return ConciergeService.objects.filter(is_available=True)
        return []

    def get_serializer_class(self):
        service_type = self.request.query_params.get('type', None)
        if service_type == 'vehicle':
            return VehicleSerializer
        elif service_type == 'security':
            return SecurityServiceSerializer
        elif service_type == 'concierge':
            return ConciergeServiceSerializer
        return VehicleSerializer  # Default serializer

class ServiceAvailabilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        service_type = request.query_params.get('type', None)
        date = request.query_params.get('date', None)
        
        if not service_type or not date:
            return Response({'error': 'Both service type and date are required'}, status=400)
            
        if service_type == 'vehicle':
            available = Vehicle.objects.filter(is_available=True).exclude(
                servicebooking__start_time__date=date
            )
            serializer = VehicleSerializer(available, many=True)
        elif service_type == 'security':
            available = SecurityService.objects.exclude(
                servicebooking__start_time__date=date
            )
            serializer = SecurityServiceSerializer(available, many=True)
        elif service_type == 'concierge':
            available = ConciergeService.objects.filter(is_available=True).exclude(
                servicebooking__start_time__date=date
            )
            serializer = ConciergeServiceSerializer(available, many=True)
        else:
            return Response({'error': 'Invalid service type'}, status=400)
            
        return Response(serializer.data)

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'status', 'location']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Service.objects.all()
        return Service.objects.filter(client=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user) 