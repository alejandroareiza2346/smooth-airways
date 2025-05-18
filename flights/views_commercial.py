from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from django import forms
from django.utils import timezone

from flights.models_commercial import CommercialFlight, CommercialBooking, Passenger, Seat
from accounts.mixins import ClientRequiredMixin

import json
from datetime import datetime, timedelta

class FlightSearchForm(forms.Form):
    """Formulario de búsqueda de vuelos"""
    origin = forms.CharField(max_length=3, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Origen (ej. BOG)',
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
    }))
    destination = forms.CharField(max_length=3, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Destino (ej. MDE)',
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
    }))
    departure_date = forms.DateField(required=True, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
    }))
    return_date = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
    }))
    passengers = forms.IntegerField(min_value=1, max_value=9, initial=1, widget=forms.NumberInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
    }))
    cabin_class = forms.ChoiceField(choices=CommercialFlight.CabinClass.choices, initial=CommercialFlight.CabinClass.ECONOMY,
                                   widget=forms.Select(attrs={
                                       'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
                                   }))


class CommercialHomeView(FormView):
    """Vista principal para búsqueda de vuelos comerciales"""
    template_name = 'flights/commercial/home.html'
    form_class = FlightSearchForm
    
    def form_valid(self, form):
        # Guardar parámetros de búsqueda en la sesión
        self.request.session['flight_search'] = {
            'origin': form.cleaned_data['origin'].upper(),
            'destination': form.cleaned_data['destination'].upper(),
            'departure_date': form.cleaned_data['departure_date'].strftime('%Y-%m-%d'),
            'return_date': form.cleaned_data['return_date'].strftime('%Y-%m-%d') if form.cleaned_data['return_date'] else None,
            'passengers': form.cleaned_data['passengers'],
            'cabin_class': form.cleaned_data['cabin_class']
        }
        return redirect('commercial_flight_results')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Destinos populares para mostrar en la página principal
        context['popular_destinations'] = [
            {'code': 'MDE', 'name': 'Medellín', 'image': 'path/to/medellin.jpg'},
            {'code': 'CTG', 'name': 'Cartagena', 'image': 'path/to/cartagena.jpg'},
            {'code': 'SMR', 'name': 'Santa Marta', 'image': 'path/to/santamarta.jpg'},
            {'code': 'BOG', 'name': 'Bogotá', 'image': 'path/to/bogota.jpg'},
        ]
        return context


class CommercialFlightResultsView(ListView):
    """Resultados de la búsqueda de vuelos comerciales"""
    model = CommercialFlight
    template_name = 'flights/commercial/flight_results.html'
    context_object_name = 'flights'
    
    def get_queryset(self):
        search_params = self.request.session.get('flight_search', {})
        if not search_params:
            return CommercialFlight.objects.none()
        
        origin = search_params.get('origin', '')
        destination = search_params.get('destination', '')
        departure_date = search_params.get('departure_date')
        
        if not (origin and destination and departure_date):
            return CommercialFlight.objects.none()
        
        # Convertir fecha de texto a objeto datetime para filtrar
        try:
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
            
            # Filtrar vuelos por origen, destino y fecha de salida
            queryset = CommercialFlight.objects.filter(
                origin_code=origin,
                destination_code=destination,
                departure_time__date=departure_date,
                status__in=['SCHEDULED', 'DELAYED']
            ).order_by('departure_time')
            
            return queryset
            
        except (ValueError, TypeError):
            return CommercialFlight.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = self.request.session.get('flight_search', {})
        context['search_params'] = search_params
        
        # Añadir vuelos de vuelta si es un viaje redondo
        if search_params.get('return_date'):
            try:
                return_date = datetime.strptime(search_params['return_date'], '%Y-%m-%d').date()
                return_flights = CommercialFlight.objects.filter(
                    origin_code=search_params.get('destination', ''),
                    destination_code=search_params.get('origin', ''),
                    departure_time__date=return_date,
                    status__in=['SCHEDULED', 'DELAYED']
                ).order_by('departure_time')
                context['return_flights'] = return_flights
            except (ValueError, TypeError):
                context['return_flights'] = []
        
        return context


class CommercialFlightDetailView(DetailView):
    """Detalle de un vuelo comercial específico"""
    model = CommercialFlight
    template_name = 'flights/commercial/flight_detail.html'
    context_object_name = 'flight'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener información sobre disponibilidad de asientos
        seats = Seat.objects.filter(flight=self.object)
        context['available_seats'] = seats.filter(status='AVAILABLE').count()
        context['total_seats'] = seats.count()
        
        # Recuperar parámetros de búsqueda de la sesión
        context['search_params'] = self.request.session.get('flight_search', {})
        
        return context


class SeatMapView(DetailView):
    """Vista del mapa de asientos de un vuelo"""
    model = CommercialFlight
    template_name = 'flights/commercial/seat_map.html'
    context_object_name = 'flight'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Organizar asientos por filas y columnas
        seats = Seat.objects.filter(flight=self.object).order_by('seat_row', 'seat_column')
        
        # Agrupar por cabina
        seat_map = {
            'ECONOMY': {},
            'PREMIUM_ECONOMY': {},
            'BUSINESS': {},
            'FIRST': {}
        }
        
        for seat in seats:
            cabin = seat.cabin_class
            row = seat.seat_row
            
            if row not in seat_map[cabin]:
                seat_map[cabin][row] = []
                
            seat_map[cabin][row].append(seat)
        
        context['seat_map'] = seat_map
        context['selected_cabin'] = self.request.GET.get('cabin', 'ECONOMY')
        
        # Recuperar parámetros de búsqueda de la sesión
        context['search_params'] = self.request.session.get('flight_search', {})
        
        return context


class FlightBookingView(LoginRequiredMixin, ClientRequiredMixin, FormView):
    """Vista para crear una reserva de vuelo"""
    template_name = 'flights/commercial/flight_booking.html'
    form_class = forms.Form  # Se construirá dinámicamente en get_form
    success_url = reverse_lazy('commercial_booking_confirmation')
    
    def get_flight(self):
        flight_id = self.kwargs.get('pk')
        return get_object_or_404(CommercialFlight, id=flight_id)
    
    def get_form(self, form_class=None):
        flight = self.get_flight()
        search_params = self.request.session.get('flight_search', {})
        passengers_count = search_params.get('passengers', 1)
        
        # Crear un formulario dinámico basado en el número de pasajeros
        class PassengerForm(forms.Form):
            cabin_class = forms.ChoiceField(
                choices=CommercialFlight.CabinClass.choices,
                initial=search_params.get('cabin_class', 'ECONOMY'),
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        
        # Añadir campos para cada pasajero
        for i in range(1, passengers_count + 1):
            PassengerForm.base_fields[f'first_name_{i}'] = forms.CharField(
                max_length=100, 
                label=f'Nombre del pasajero {i}',
                widget=forms.TextInput(attrs={'class': 'form-input'})
            )
            PassengerForm.base_fields[f'last_name_{i}'] = forms.CharField(
                max_length=100, 
                label=f'Apellido del pasajero {i}',
                widget=forms.TextInput(attrs={'class': 'form-input'})
            )
            PassengerForm.base_fields[f'document_type_{i}'] = forms.ChoiceField(
                choices=[('PASSPORT', 'Pasaporte'), ('ID_CARD', 'Cédula'), ('DRIVER', 'Licencia')],
                label=f'Tipo de documento del pasajero {i}',
                widget=forms.Select(attrs={'class': 'form-select'})
            )
            PassengerForm.base_fields[f'document_number_{i}'] = forms.CharField(
                max_length=50, 
                label=f'Número de documento del pasajero {i}',
                widget=forms.TextInput(attrs={'class': 'form-input'})
            )
            PassengerForm.base_fields[f'date_of_birth_{i}'] = forms.DateField(
                label=f'Fecha de nacimiento del pasajero {i}',
                widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
            )
        
        return PassengerForm(**self.get_form_kwargs())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flight = self.get_flight()
        context['flight'] = flight
        context['search_params'] = self.request.session.get('flight_search', {})
        
        # Calcular precio total basado en la clase y número de pasajeros
        search_params = self.request.session.get('flight_search', {})
        cabin_class = search_params.get('cabin_class', 'ECONOMY')
        passengers = search_params.get('passengers', 1)
        
        price_field = f'price_{cabin_class.lower()}'
        if hasattr(flight, price_field) and getattr(flight, price_field):
            price = getattr(flight, price_field) * passengers
            context['total_price'] = price
        else:
            context['total_price'] = flight.price_economy * passengers
        
        return context
    
    def form_valid(self, form):
        flight = self.get_flight()
        search_params = self.request.session.get('flight_search', {})
        cabin_class = form.cleaned_data.get('cabin_class', search_params.get('cabin_class', 'ECONOMY'))
        passengers_count = search_params.get('passengers', 1)
        
        # Calcular precio
        price_field = f'price_{cabin_class.lower()}'
        if hasattr(flight, price_field) and getattr(flight, price_field):
            price = getattr(flight, price_field)
        else:
            price = flight.price_economy
            
        total_price = price * passengers_count
        
        # Crear la reserva
        booking = CommercialBooking.objects.create(
            client=self.request.user,
            flight=flight,
            cabin_class=cabin_class,
            price=price,
            tax=total_price * 0.19,  # 19% de impuesto
            total_price=total_price * 1.19
        )
        
        # Crear registros de pasajeros
        for i in range(1, passengers_count + 1):
            Passenger.objects.create(
                booking=booking,
                first_name=form.cleaned_data[f'first_name_{i}'],
                last_name=form.cleaned_data[f'last_name_{i}'],
                document_type=form.cleaned_data[f'document_type_{i}'],
                document_number=form.cleaned_data[f'document_number_{i}'],
                date_of_birth=form.cleaned_data[f'date_of_birth_{i}']
            )
        
        # Guardar ID de reserva en sesión para la página de confirmación
        self.request.session['last_commercial_booking_id'] = booking.id
        
        return super().form_valid(form)


class CommercialBookingConfirmationView(LoginRequiredMixin, ClientRequiredMixin, TemplateView):
    """Confirmación de la reserva de vuelo comercial"""
    template_name = 'flights/commercial/booking_confirmation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.request.session.get('last_commercial_booking_id')
        if booking_id:
            booking = get_object_or_404(CommercialBooking, id=booking_id, client=self.request.user)
            context['booking'] = booking
            context['passengers'] = Passenger.objects.filter(booking=booking)
            
            # Eliminar el ID de la sesión después de utilizarlo
            del self.request.session['last_commercial_booking_id']
            
        return context


class UserFlightsView(LoginRequiredMixin, ClientRequiredMixin, ListView):
    """Lista de vuelos del usuario actual"""
    model = CommercialBooking
    template_name = 'flights/commercial/user_flights.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return CommercialBooking.objects.filter(client=self.request.user).order_by('-booking_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Filtrar por vuelos pasados y futuros
        upcoming_bookings = []
        past_bookings = []
        
        for booking in self.get_queryset():
            if booking.flight.departure_time > now:
                upcoming_bookings.append(booking)
            else:
                past_bookings.append(booking)
        
        context['upcoming_bookings'] = upcoming_bookings
        context['past_bookings'] = past_bookings
        
        return context


class CommercialBookingDetailView(LoginRequiredMixin, ClientRequiredMixin, DetailView):
    """Detalle de una reserva específica"""
    model = CommercialBooking
    template_name = 'flights/commercial/booking_detail.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        # Solo permitir ver reservas propias
        return CommercialBooking.objects.filter(client=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['passengers'] = Passenger.objects.filter(booking=self.object)
        return context


@require_POST
def select_seat(request, booking_id, passenger_id):
    """API para seleccionar un asiento"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=401)
        
    try:
        booking = CommercialBooking.objects.get(id=booking_id, client=request.user)
        passenger = Passenger.objects.get(id=passenger_id, booking=booking)
        seat_number = request.POST.get('seat_number')
        
        if not seat_number:
            return JsonResponse({'error': 'Número de asiento no proporcionado'}, status=400)
            
        # Verificar que el asiento esté disponible
        try:
            seat = Seat.objects.get(
                flight=booking.flight,
                seat_number=seat_number,
                status='AVAILABLE'
            )
            
            # Si el pasajero ya tenía un asiento, liberarlo
            try:
                old_seat = Seat.objects.get(passenger=passenger)
                old_seat.passenger = None
                old_seat.status = 'AVAILABLE'
                old_seat.save()
            except Seat.DoesNotExist:
                pass
                
            # Asignar el nuevo asiento
            seat.passenger = passenger
            seat.status = 'RESERVED'
            seat.save()
            
            # Actualizar el número de asiento del pasajero
            passenger.seat_number = seat_number
            passenger.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Asiento {seat_number} asignado correctamente'
            })
            
        except Seat.DoesNotExist:
            return JsonResponse({'error': 'El asiento no existe o no está disponible'}, status=400)
            
    except (CommercialBooking.DoesNotExist, Passenger.DoesNotExist):
        return JsonResponse({'error': 'Reserva o pasajero no encontrado'}, status=404)
