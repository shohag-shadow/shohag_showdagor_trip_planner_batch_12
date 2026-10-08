from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from enum import Enum
import sqlite3
class TripStatus(Enum):
    planned="PLANNED"
    ongoing="ONGOING"
    completed="COMPLETED"
    cancelled="CANCELLED"

    
db = SQLAlchemy()


@event.listens_for(Engine,"connect")
def enable_sqlite_foreign_keys(dbapi_connection,connection_record):
    if isinstance(dbapi_connection,sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

class Traveler(db.Model):
    __tablename__="travelers"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    email = db.Column(db.String(120),nullable=False,unique=True)
    name = db.Column(db.String(120), nullable=False)
    trips = db.relationship("TripTraveler",back_populates="traveler",cascade="all, delete-orphan")
    def can_join_trip(self,new_trip):
        for membership in self.trips:
            trip = membership.trip
            if trip.id==new_trip.id:
                continue
            if trip.status == TripStatus.cancelled.value:
                continue
            if trip.start_date <= new_trip.end_date and new_trip.start_date <= trip.end_date:
                return False
        return True
    def __repr__(self):
        return f"<Traveler {self.id}>"

    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "email":self.email
        }

class Trip(db.Model):
    __tablename__ = "trips"
    __table_args__ = (
        db.CheckConstraint("end_date >= start_date",name="ck_trip_dates"),
        db.CheckConstraint("max_travelers > 0",name="ck_trip_max_travelers"),
        db.CheckConstraint("budget >= 0",name="ck_trip_budget")
    )

    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    max_travelers = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=TripStatus.planned.value)
    travelers = db.relationship("TripTraveler",back_populates="trip",cascade="all, delete-orphan")
    expenses = db.relationship("Expense",back_populates="trip",cascade="all, delete-orphan")

    def can_update_max(self,update):
        return len(self.travelers)<=update
    def is_full(self):
        return len(self.travelers) >= self.max_travelers
    def total_expenses(self):
        return round(sum(expense.amount for expense in self.expenses),6)
    def remaining_budget(self):
        return round(self.budget-self.total_expenses(),6)
    def can_add_expense(self,amount):
        return round(self.total_expenses() + amount,6) <= round(self.budget,6)
    def get_travelers(self):
        return [people.traveler for people in self.travelers]
    def __repr__(self):
        return f"<Trip {self.id}>"
    def to_dict(self,include_travelers=False):
        data = {
            "id": self.id,
            "destination":self.destination,
            "start_date":self.start_date.isoformat(),
            "end_date":self.end_date.isoformat(),
            "budget":self.budget,
            "max_travelers":self.max_travelers,
            "status":self.status
        }
        if include_travelers:
            data["travelers"] = [m.traveler.to_dict() for m in self.travelers]
        return data

class TripTraveler(db.Model):
    __tablename__ = "trip_travelers"
    trip_id = db.Column(db.Integer,db.ForeignKey("trips.id",ondelete="CASCADE"),primary_key=True)
    traveler_id = db.Column(db.Integer,db.ForeignKey("travelers.id",ondelete="CASCADE"),primary_key=True)
    joined_at = db.Column(db.DateTime, server_default=db.func.now())
    trip = db.relationship("Trip",back_populates="travelers")
    traveler = db.relationship("Traveler",back_populates="trips")

    def __repr__(self):
        return f"<TripTraveler trip={self.trip_id} traveler={self.traveler_id}>"

    def to_dict(self):
        return {
            "trip_id":self.trip_id,
            "traveler_id":self.traveler_id,
            "joined_at":self.joined_at.isoformat() if self.joined_at else None
        }

class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    trip_id = db.Column(db.Integer,db.ForeignKey("trips.id",ondelete="CASCADE"),nullable=False)
    amount = db.Column(db.Float, nullable=False)
    trip = db.relationship("Trip",back_populates="expenses")

    def __repr__(self):
        return f"<Expense {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title":self.title,
            "trip_id":self.trip_id,
            "amount":self.amount
        }