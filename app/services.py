from app.models import db,Trip,TripStatus
from flask import jsonify
from datetime import datetime
from app.validations import validate_create_trip
def get_trips_service():
    trips=Trip.query.all()
    return jsonify([trip.to_dict() for trip in trips]),200
def create_trip_service(data):
    validation_error=validate_create_trip(data)
    if(validation_error is not None):
        return validation_error
    trip=Trip(
        destination=data["destination"].strip(),
        start_date=datetime.strptime(data["start_date"].strip(), "%Y-%m-%d").date(),
        end_date=datetime.strptime(data["end_date"].strip(), "%Y-%m-%d").date(),
        budget=data["budget"],
        max_travelers=data["max_travelers"]
    )
    db.session.add(trip)
    db.session.commit()
    return jsonify(trip.to_dict()), 201

def get_trip_service(trip_id):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"Trip not found"}),404
    return jsonify(trip.to_dict()),200