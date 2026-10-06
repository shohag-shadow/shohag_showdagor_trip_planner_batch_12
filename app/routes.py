from flask import Blueprint, request
from app.services import get_all_trips,create_new_trip
api = Blueprint("api", __name__, url_prefix="/api/v1")

@api.route("/trips",methods=["GET"])
def get_trips():
    trips=get_all_trips()
    return trips
@api.route("/trips",methods=["POST"])
def create_trip():
    trip=create_new_trip(request.get_json())
    return trip
