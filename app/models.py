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

class Traveller(db.Model):
    __tablename__="travellers"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120),nullable=False,unique=True)
    memberships = db.relationship("TripTraveller",back_populates="traveller",cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Traveller {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
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
    memberships = db.relationship("TripTraveller",back_populates="trip",cascade="all, delete-orphan")
    expenses = db.relationship("Expense",back_populates="trip",cascade="all, delete-orphan")

    @property
    def is_full(self):
        return len(self.memberships) >= self.max_travelers
        
    def total_expenses(self):
        return round(sum(expense.amount for expense in self.expenses),6)

    def can_add_expense(self,amount):
        return round(self.total_expenses + amount,6) <= self.budget
    def __repr__(self):
        return f"<Trip {self.id}>"

    def to_dict(self,include_travellers=False):
        data = {
            "id": self.id,
            "destination":self.destination,
            "start_date":self.start_date.isoformat(),
            "end_date":self.end_date.isoformat(),
            "budget":self.budget,
            "max_travelers":self.max_travelers,
            "status":self.status
        }
        if include_travellers:
            data["travellers"] = [m.traveller.to_dict() for m in self.memberships]
        return data

class TripTraveller(db.Model):
    __tablename__ = "trip_travellers"

    trip_id = db.Column(db.Integer,db.ForeignKey("trips.id",ondelete="CASCADE"),primary_key=True)
    traveller_id = db.Column(db.Integer,db.ForeignKey("travellers.id",ondelete="CASCADE"),primary_key=True)
    joined_at = db.Column(db.DateTime, server_default=db.func.now())
    trip = db.relationship("Trip",back_populates="memberships")
    traveller = db.relationship("Traveller",back_populates="memberships")

    def __repr__(self):
        return f"<TripTraveller trip={self.trip_id} traveller={self.traveller_id}>"

    def to_dict(self):
        return {
            "trip_id":self.trip_id,
            "traveller_id":self.traveller_id,
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