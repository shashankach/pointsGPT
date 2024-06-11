from django.db import models

# Create your models here.
class FlightSearchResult:
    def __init__(self, program=None, date=None, airline=None, origin=None, destination=None, class_available=None, seats_available=None, mileage_cost=None, direct_cost=None, direct_flight=None, partner=None, bonus=None):
        self.program = program
        self.date = date
        self.airline = airline
        self.origin = origin
        self.destination = destination
        self.class_available = class_available
        self.seats_available = seats_available
        self.mileage_cost = mileage_cost
        self.direct_cost = direct_cost
        self.direct_flight = direct_flight
        self.partner = partner
        self.bonus = bonus

    def to_json(self):
        return {
            'program': self.program,
            'date': self.date,
            'airline': self.airline,
            'origin': self.origin,
            'destination': self.destination,
            'class_available': self.class_available,
            'seats_available': self.seats_available,
            'mileage_cost': self.mileage_cost,
            'direct_cost': self.direct_cost,
            'direct_flight': self.direct_flight,
            'partner': self.partner,
            'bonus': self.bonus
        }
    
    def to_output(self):
        return (
        "Flight Information:\n"
        f"- Program: {self.program}\n"
        f"- Date: {self.date}\n"
        f"- Airline: {self.airline}\n"
        f"- From: {self.origin} to {self.destination}\n"
        f"- {self.class_available.capitalize()} Available: {'Yes' if self.class_available else 'No'}\n"
        f"- Seats Available: {self.seats_available}\n"
        f"- Mileage Cost: {self.mileage_cost} (Direct Cost: {self.direct_cost})\n"
        f"- Direct Flight: {'Yes' if self.direct_flight else 'No'}\n"
    )