from app.models import db,Trip,TripStatus,Traveler,TripTraveler
from flask import jsonify
from datetime import datetime
from app.validations import validate_create_trip,validate_update_trip,validate_update_trip_time,validate_update_trip_status,validate_max_trip_travelers,validate_traveler

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
    return jsonify(trip.to_dict(True)),200



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
    max_traveler_error=validate_max_trip_travelers(data,trip)
    if max_traveler_error is not None:
        return max_traveler_error
    update_status_error=validate_update_trip_status(data,trip)
    if update_status_error is not None:
        return update_status_error
    if "status" in data:
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
    return jsonify(trip.to_dict(True)),200

def delete_trip_service(trip_id):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"Trip not found"}),404
    db.session.delete(trip)
    db.session.commit()
    return jsonify({"message":"Trip deleted successfully"}),200

def add_traveler_service(trip_id,data):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"Trip not found"}),404
    if trip.is_full():
        return jsonify({"error":"Trip is full"}),409
    traveler_validation_error=validate_traveler(data)
    if traveler_validation_error is not None:
        return traveler_validation_error
    email=data["email"].strip()
    name=data["name"].strip()
    traveler=db.session.execute(db.select(Traveler).filter_by(email=email)).scalar_one_or_none()
    if traveler is None:
        traveler=Traveler(email=email,name=name)
        db.session.add(traveler)
        db.session.flush()
    else:
        if traveler.name != name:
            return jsonify({"error":f"already a traveler exist with the same email and a different name:{traveler.name}"}),409
    trip_traveler=db.session.get(TripTraveler,(trip.id,traveler.id))
    if trip_traveler is None:
        if not traveler.can_join_trip(trip):
            return jsonify({"error":"Traveler already has an overlapping trip"}),409
        trip_traveler=TripTraveler(trip_id=trip.id,traveler_id=traveler.id)
        db.session.add(trip_traveler)
    else:
        return jsonify({"error":"Cannot add the same traveler to a trip twice"}),409
    db.session.commit()
    return jsonify(trip.to_dict(True)),201

def remove_traveler_service(trip_id,traveler_id):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"Trip not found"}),404
    traveler=db.session.get(Traveler,traveler_id)
    if traveler is None:
        return jsonify({"error":"Traveler not found"}),404
    trip_traveler=db.session.get(TripTraveler,(trip.id,traveler.id))
    if trip_traveler is None:
        return jsonify({"error":"Invalid delete,traveler is not in the trip"}),404
    db.session.delete(trip_traveler)
    db.session.flush()
    if len(traveler.trips)==0:
        db.session.delete(traveler)
    db.session.commit()
    return jsonify({"message":"Traveler removed successfully"}),200