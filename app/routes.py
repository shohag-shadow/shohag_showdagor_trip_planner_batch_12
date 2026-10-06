from flask import Blueprint, request
from app.services import get_trips_service,create_trip_service,get_trip_service
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
    trip_or_error=update_trip_service(trip_id)
    return trip_or_error