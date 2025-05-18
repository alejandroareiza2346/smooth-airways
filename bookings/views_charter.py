from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages

from .models_charter import PrivateAircraft, CharterBooking, CharterService, BookingService
from accounts.mixins import ClientRequiredMixin

import json
from datetime import datetime, timedelta

class CharterHomeView(TemplateView):
    """Vista principal para el servicio de vuelos privados"""
    template_name = 'bookings/charter/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aircraft_types'] = PrivateAircraft.AircraftType.choices
        # Obtener aeronaves destacadas
        context['featured_aircraft'] = PrivateAircraft.objects.filter(
            status='AVAILABLE'
        ).order_by('?')[:3]  # Seleccionar 3 aleatorias disponibles
        return context


class AircraftListView(ListView):
    """Lista de aeronaves disponibles"""
    model = PrivateAircraft
    template_name = 'bookings/charter/aircraft_list.html'
    context_object_name = 'aircraft_list'
    
    def get_queryset(self):
        queryset = PrivateAircraft.objects.filter(status='AVAILABLE')
        
        # Filtrar por tipo si se proporciona
        aircraft_type = self.request.GET.get('type')
        if aircraft_type:
            queryset = queryset.filter(type=aircraft_type)
        
        # Filtrar por capacidad mínima
        min_capacity = self.request.GET.get('min_capacity')
        if min_capacity:
            queryset = queryset.filter(capacity__gte=int(min_capacity))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aircraft_types'] = PrivateAircraft.AircraftType.choices
        return context


class AircraftDetailView(DetailView):
    """Detalle de una aeronave específica"""
    model = PrivateAircraft
    template_name = 'bookings/charter/aircraft_detail.html'
    context_object_name = 'aircraft'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = CharterService.objects.all()
        return context


class CharterBookingCreateView(LoginRequiredMixin, ClientRequiredMixin, CreateView):
    """Crear una nueva reserva de vuelo privado"""
    model = CharterBooking
    template_name = 'bookings/charter/booking_create.html'
    fields = ['departure_location', 'arrival_location', 'departure_datetime', 
              'return_datetime', 'is_round_trip', 'passenger_count', 'notes']
    success_url = reverse_lazy('charter_booking_confirmation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aircraft_id = self.kwargs.get('aircraft_id')
        context['aircraft'] = get_object_or_404(PrivateAircraft, id=aircraft_id)
        context['services'] = CharterService.objects.all()
        return context
    
    def form_valid(self, form):
        aircraft_id = self.kwargs.get('aircraft_id')
        aircraft = get_object_or_404(PrivateAircraft, id=aircraft_id)
        
        # Asignar el cliente actual y la aeronave
        form.instance.client = self.request.user
        form.instance.aircraft = aircraft
        
        # Calcular precios
        departure = form.instance.departure_datetime
        if form.instance.is_round_trip and form.instance.return_datetime:
            return_time = form.instance.return_datetime
            duration = (return_time - departure).total_seconds() / 3600  # Horas
        else:
            # Para vuelos de ida, estimamos 2 horas por defecto
            duration = 2
        
        # Precio base según duración y tarifa horaria
        form.instance.base_price = aircraft.hourly_rate * duration
        
        # Servicios adicionales (se procesarán después de guardar)
        booking = form.save()
        
        # Procesar servicios seleccionados desde el formulario
        services_data = self.request.POST.getlist('services')
        if services_data:
            total_services_price = 0
            for service_id in services_data:
                service = get_object_or_404(CharterService, id=service_id)
                BookingService.objects.create(
                    booking=booking,
                    service=service,
                    quantity=1
                )
                total_services_price += service.price
            
            # Actualizar precio de servicios y total
            booking.services_price = total_services_price
            booking.total_price = booking.base_price + total_services_price
            booking.save()
        
        # Guardar en sesión el id de la reserva para la página de confirmación
        self.request.session['last_charter_booking_id'] = booking.id
        
        return super().form_valid(form)


class CharterBookingConfirmationView(LoginRequiredMixin, ClientRequiredMixin, TemplateView):
    """Confirmación de reserva de vuelo privado"""
    template_name = 'bookings/charter/booking_confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.request.session.get('last_charter_booking_id')
        if booking_id:
            booking = get_object_or_404(CharterBooking, id=booking_id, client=self.request.user)
            context['booking'] = booking
            # Obtener servicios relacionados
            context['booking_services'] = BookingService.objects.filter(booking=booking)
            
            # Eliminar de la sesión
            del self.request.session['last_charter_booking_id']
        return context


class UserCharterBookingsView(LoginRequiredMixin, ClientRequiredMixin, ListView):
    """Lista de reservas del usuario actual"""
    model = CharterBooking
    template_name = 'bookings/charter/user_bookings.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return CharterBooking.objects.filter(client=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_bookings = self.get_queryset().filter(
            Q(status='PENDING') | Q(status='CONFIRMED') | Q(status='IN_FLIGHT')
        )
        past_bookings = self.get_queryset().filter(
            Q(status='COMPLETED') | Q(status='CANCELLED')
        )
        context['active_bookings'] = active_bookings
        context['past_bookings'] = past_bookings
        return context


class CharterBookingDetailView(LoginRequiredMixin, ClientRequiredMixin, DetailView):
    """Detalle de una reserva específica"""
    model = CharterBooking
    template_name = 'bookings/charter/booking_detail.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        # Solo permitir ver reservas propias del usuario
        return CharterBooking.objects.filter(client=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking_services'] = BookingService.objects.filter(booking=self.object)
        return context


class CharterBookingCancelView(LoginRequiredMixin, ClientRequiredMixin, UpdateView):
    """Cancelar una reserva de vuelo privado"""
    model = CharterBooking
    template_name = 'bookings/charter/booking_cancel.html'
    fields = ['cancellation_reason']
    success_url = reverse_lazy('user_charter_bookings')
    
    def get_queryset(self):
        # Solo permitir cancelar reservas propias en estado pendiente o confirmado
        return CharterBooking.objects.filter(
            client=self.request.user,
            status__in=['PENDING', 'CONFIRMED']
        )
    
    def form_valid(self, form):
        booking = form.instance
        booking.status = CharterBooking.BookingStatus.CANCELLED
        booking.cancelled_at = timezone.now()
        messages.success(self.request, f'La reserva {booking.booking_number} ha sido cancelada.')
        return super().form_valid(form)


# API Views para cálculos en tiempo real

def calculate_charter_price(request):
    """Calcular precio estimado de vuelo charter"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            aircraft_id = data.get('aircraft_id')
            duration_hours = float(data.get('duration_hours', 2))
            services = data.get('services', [])
            
            aircraft = PrivateAircraft.objects.get(id=aircraft_id)
            
            # Cálculo básico de precios
            base_price = aircraft.hourly_rate * duration_hours
            
            # Precio de servicios
            services_price = 0
            if services:
                services_objs = CharterService.objects.filter(id__in=services)
                services_price = sum(service.price for service in services_objs)
            
            total_price = base_price + services_price
            
            return JsonResponse({
                'base_price': float(base_price),
                'services_price': float(services_price),
                'total_price': float(total_price)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Método no permitido'}, status=405)
