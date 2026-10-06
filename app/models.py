from flask_sqlalchemy import SQLAlchemy
from enum import Enum
class TripStatus(Enum):
    planned="PLANNED"
    ongoing="ONGOING"
    completed="COMPLETED"
    cancelled="CANCELLED"
db = SQLAlchemy()
class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    max_travelers = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=TripStatus.planned.value)

    def __repr__(self):
        return f"<Trip {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "destination":self.destination,
            "start_date":self.start_date,
            "end_date":self.end_date,
            "budget":self.budget,
            "max_travelers":self.max_travelers,
            "status":self.status
        }