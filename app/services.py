from app.models import db,Trip,TripStatus
from flask import jsonify
from datetime import datetime
from app.validations import validate_create_trip,validate_update_trip,validate_update_trip_time,validate_update_trip_status
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


#todo:add validation for updating max_travelers based on number of travellers in a plan after adding travellers model
def update_trip_service(trip_id,data):
    validation_error=validate_update_trip(data)
    if(validation_error is not None):
            return validation_error
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"Trip not found"}),404
    update_time_error=validate_update_trip_time(data,trip)
    if update_time_error is not None:
        return update_time_error
    if "status" in data:
        update_status_error=validate_update_trip_status(data,trip)
        if update_status_error is not None:
            return update_status_error
        trip.status=data["status"].strip().upper()
    if "destination" in data:
        trip.destination=data["destination"].strip()
    if "start_date" in data:
        trip.start_date=datetime.strptime(data["start_date"].strip(),"%Y-%m-%d").date()
    if "end_date" in data:
        trip.end_date=datetime.strptime(data["end_date"].strip(),"%Y-%m-%d").date()
    if "budget" in data:
        trip.budget=data["budget"]
    if "max_travelers" in data:
        trip.max_travelers=data["max_travelers"]
    db.session.commit()
    return jsonify(trip.to_dict()),200

def delete_trip_service(trip_id):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"Trip not found"}),404
    db.session.delete(trip)
    db.session.commit()
    return jsonify({"message":"Trip deleted successfully"}),200