from app.models import db,Trip,TripStatus,Traveler,TripTraveler,Expense
from flask import jsonify
from datetime import datetime
from app.validations import validate_create_trip,validate_update_trip,validate_update_trip_time,validate_update_trip_status,validate_max_trip_travelers,validate_traveler,validate_add_trip_expenses

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
        return jsonify({"error":"TRIP_NOT_FOUND","message":"Trip not found"}),404
    return jsonify(trip.to_dict(True)),200



def update_trip_service(trip_id,data):
    validation_error=validate_update_trip(data)
    if(validation_error is not None):
            return validation_error
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"TRIP_NOT_FOUND","message":"Trip not found"}),404
    update_time_error=validate_update_trip_time(data,trip)
    if update_time_error is not None:
        return update_time_error
    max_traveler_error=validate_max_trip_travelers(data,trip)
    if max_traveler_error is not None:
        return max_traveler_error
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
        return jsonify({"error":"TRIP_NOT_FOUND","message":"Trip not found"}),404
    db.session.delete(trip)
    db.session.commit()
    return jsonify({"message":"Trip deleted successfully"}),200

def add_traveler_service(trip_id,data):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"TRIP_NOT_FOUND","message":"Trip not found"}),404
    if trip.is_full():
        return jsonify({"error":"TRIP_FULL","message":"The trip has reached its maximum traveler capacity."}),409
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
            return jsonify({"error":"TRAVELER_EMAIL_CONFLICT","message":f"already a traveler exist with the same email and a different name:{traveler.name}"}),409
    trip_traveler=db.session.get(TripTraveler,(trip.id,traveler.id))
    if trip_traveler is None:
        if not traveler.can_join_trip(trip):
            return jsonify({"error":"TRAVELER_TRIP_OVERLAP","message":"Traveler already has an overlapping trip"}),409
        if trip.status != TripStatus.planned.value:
            return jsonify({"error":"TRIP_NOT_PLANNED","message":"Traveller can only join a trip during planning"}),409
        trip_traveler=TripTraveler(trip_id=trip.id,traveler_id=traveler.id)
        db.session.add(trip_traveler)
    else:
        return jsonify({"error":"TRAVELER_ALREADY_IN_TRIP","message":"Cannot add the same traveler to a trip twice"}),409
    db.session.commit()
    return jsonify(trip.to_dict(True)),201

def remove_traveler_service(trip_id,traveler_id):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"TRIP_NOT_FOUND","message":"Trip not found"}),404
    traveler=db.session.get(Traveler,traveler_id)
    if traveler is None:
        return jsonify({"error":"TRAVELER_NOT_FOUND","message":"Traveler not found"}),404
    trip_traveler=db.session.get(TripTraveler,(trip.id,traveler.id))
    if trip_traveler is None:
        return jsonify({"error":"TRAVELER_NOT_IN_TRIP","message":"Invalid delete,traveler is not in the trip"}),404
    db.session.delete(trip_traveler)
    db.session.flush()
    if len(traveler.trips)==0:
        db.session.delete(traveler)
    db.session.commit()
    return jsonify({"message":"Traveler removed successfully"}),200

def add_trip_expenses_service(trip_id,data):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"TRIP_NOT_FOUND","message":"Trip not found"}),404
    validation_error=validate_add_trip_expenses(data)
    if validation_error is not None:
        return validation_error
    if trip.status not in [TripStatus.planned.value,TripStatus.ongoing.value]:
        return jsonify({"error":"EXPENSE_NOT_ALLOWED","message":"expense can only be added in planning and ongoing phase of a trip"}),409
    if not trip.can_add_expense(data["amount"]):
        return jsonify({"error":"EXPENSE_EXCEEDS_BUDGET","message":f"expense cannot be larger than remaining budget, your remaining budget is {trip.remaining_budget()}"}),409
    expense=Expense(
        title=data["title"].strip(),
        trip_id=trip.id,
        amount=data["amount"]
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.to_dict()), 201

def update_trip_status_service(trip_id,data):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"TRIP_NOT_FOUND","message":"Trip not found"}),404
    update_status_error=validate_update_trip_status(data,trip)
    if update_status_error is not None:
        return update_status_error
    trip.status=data["status"].strip().upper()
    db.session.commit()
    return jsonify(trip.to_dict()), 200

def get_trip_summary_service(trip_id):
    trip=db.session.get(Trip,trip_id)
    if trip is None:
        return jsonify({"error":"TRIP_NOT_FOUND","message":"Trip not found"}),404
    travelers_count=len(trip.travelers)
    return jsonify({
        "traveler_count":travelers_count,
        "available_seats":trip.max_travelers-travelers_count,
        "total_expense":trip.total_expenses(),
        "remaining_budget":trip.remaining_budget()
    }),200