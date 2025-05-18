import random
from datetime import datetime, timedelta

def get_commercial_flights(origin, destination, date):
    """
    Simula una API de aerolíneas comerciales que devuelve vuelos disponibles.
    """
    airlines = ['Airline A', 'Airline B', 'Airline C']
    flights = []

    for _ in range(random.randint(3, 7)):
        departure_time = datetime.strptime(date, '%Y-%m-%d') + timedelta(hours=random.randint(6, 18))
        arrival_time = departure_time + timedelta(hours=random.randint(2, 10))
        flights.append({
            'origin': origin,
            'destination': destination,
            'airline': random.choice(airlines),
            'departure_time': departure_time.strftime('%Y-%m-%d %H:%M:%S'),
            'arrival_time': arrival_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': str(arrival_time - departure_time),
            'price_economy': round(random.uniform(100, 500), 2),
            'price_business': round(random.uniform(600, 1200), 2),
            'price_first': round(random.uniform(1500, 3000), 2),
            'services': 'Wi-Fi, Entretenimiento, Comidas',
        })

    return flights
