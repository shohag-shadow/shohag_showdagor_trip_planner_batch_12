from app.models import db,Trip,TripStatus
from flask import jsonify
from datetime import datetime
def get_all_trips():
    trips=Trip.query.all()
    return jsonify([trip.to_dict() for trip in trips]),200
def create_new_trip(data):
    trip=Trip(
        destination=data["destination"],
        start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
        end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
        budget=data["budget"],
        max_travelers=data["max_travelers"]
    )
    db.session.add(trip)
    db.session.commit()
    return jsonify(trip.to_dict()), 201