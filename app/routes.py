from flask import Blueprint, request
from app.services import get_trips_service,create_trip_service,get_trip_service,update_trip_service,delete_trip_service,add_traveler_service,remove_traveler_service,add_trip_expenses_service,update_trip_status_service,get_trip_summary_service
api = Blueprint("api", __name__, url_prefix="/api/v1")

@api.route("/trips",methods=["GET"])
def get_trips():
    trips=get_trips_service()
    return trips

@api.route("/trips",methods=["POST"])
def create_trip():
    trip_or_error=create_trip_service(request.get_json())
    return trip_or_error

@api.route("/trips/<int:trip_id>",methods=["GET"])
def get_trip(trip_id):
    trip_or_error=get_trip_service(trip_id)
    return trip_or_error

@api.route("/trips/<int:trip_id>",methods=["PUT"])
def update_trip(trip_id):
    trip_or_error=update_trip_service(trip_id,request.get_json())
    return trip_or_error

@api.route("/trips/<int:trip_id>",methods=["DELETE"])
def delete_trip(trip_id):
    deleted_or_error=delete_trip_service(trip_id)
    return deleted_or_error

@api.route("/trips/<int:trip_id>/travelers",methods=["POST"])
def add_traveler(trip_id):
    traveler_or_error=add_traveler_service(trip_id,request.get_json())
    return traveler_or_error

@api.route("/trips/<int:trip_id>/travelers/<int:traveler_id>",methods=["DELETE"])
def remove_traveler(trip_id,traveler_id):
    removed_or_error=remove_traveler_service(trip_id,traveler_id)
    return removed_or_error

@api.route("/trips/<int:trip_id>/expenses",methods=["POST"])
def add_trip_expenses(trip_id):
    trip_expenses_or_error=add_trip_expenses_service(trip_id,request.get_json())
    return trip_expenses_or_error

@api.route("/trips/<int:trip_id>/status",methods=["PATCH"])
def update_trip_status(trip_id):
    updated_trip_or_error=update_trip_status_service(trip_id,request.get_json())
    return updated_trip_or_error
    
@api.route("/trips/<int:trip_id>/summary",methods=["GET"])
def get_trip_summary(trip_id):
    trip_summary_or_error=get_trip_summary_service(trip_id)
    return trip_summary_or_error