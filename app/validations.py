from datetime import datetime
from math import isfinite
from flask import jsonify
from app.models import TripStatus
from re import fullmatch
def validate_date(body, field_name):
    value = body[field_name].strip()
    if not isinstance(value, str) or not value.strip():
        return jsonify({"error": "INVALID_DATE_TYPE", "message": f"{field_name} must be a string in YYYY-MM-DD format"}), 400
    if not fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return jsonify({"error": "INVALID_DATE_FORMAT", "message": f"{field_name} must be in YYYY-MM-DD format"}), 400
    value = value.strip()
    try:
        datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "INVALID_DATE", "message": f"{field_name} must be a valid date in YYYY-MM-DD format"}), 400
    return None


def validate_positive_number(body, field_name):
    value = body[field_name]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return jsonify({"error": "INVALID_NUMBER", "message": f"{field_name} must be a number"}), 400
    if not isfinite(value) or value <= 0:
        return jsonify({"error": "NUMBER_NOT_POSITIVE", "message": f"{field_name} must be a positive number"}), 400
    return None

def validate_text(body, field_name, max_length=None):
    value=body[field_name]
    if not isinstance(value, str) or not value.strip():
        return jsonify({"error":"INVALID_TEXT","message":f"{field_name} must be a non-empty string"}),400
    cleaned_value = value.strip()
    if max_length is not None and len(cleaned_value) > max_length:
        return jsonify({"error":"TEXT_TOO_LONG","message":f"{field_name} cannot be more than {max_length} characters"}),400
    return None

def validate_positive_int(body, field_name):
    value = body[field_name]
    if isinstance(value, bool) or not isinstance(value, int):
        return jsonify({"error": "INVALID_INTEGER", "message": f"{field_name} must be an integer"}), 400
    if value <= 0:
        return jsonify({"error": "INTEGER_NOT_POSITIVE", "message": f"{field_name} must be a positive integer"}), 400
    return None

def validate_missing_field(data,required_fields):
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": "MISSING_FIELDS","message": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    return None

def validate_email(data, field_name):
    value = data[field_name]
    if not isinstance(value, str) or not value.strip():
        return jsonify({
            "error": "INVALID_EMAIL",
            "message": f"{field_name} must be a valid email address"
        }), 400
    value = value.strip()
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    if not fullmatch(email_pattern, value):
        return jsonify({
            "error": "INVALID_EMAIL",
            "message": f"{field_name} must be a valid email address"
        }), 400
    return None

def validate_start_end_date(data):
    start_date_error=validate_date(data,"start_date")
    if(start_date_error is not None):
        return start_date_error
    end_date_error=validate_date(data,"end_date")
    if(end_date_error is not None):
        return end_date_error
    start_date=datetime.strptime(data["start_date"].strip(), "%Y-%m-%d").date()
    end_date=datetime.strptime(data["end_date"].strip(), "%Y-%m-%d").date()
    if end_date < start_date:
        return jsonify({"error": "INVALID_DATE_RANGE", "message": "end_date must be on or after start_date"}), 400
    return None
    
def validate_create_trip(data):
    missing_fields_error=validate_missing_field(data,[
        "destination",
        "start_date",
        "end_date",
        "budget",
        "max_travelers"
        ])
    if missing_fields_error!=None:
        return missing_fields_error
    destination_error=validate_text(data,"destination",120)
    if destination_error is not None:
        return destination_error
    date_error=validate_start_end_date(data)
    if date_error is not None:
        return date_error
    budget_error=validate_positive_number(data,"budget")
    if budget_error is not None:
        return budget_error
    max_travelers_error=validate_positive_int(data,"max_travelers")
    if(max_travelers_error is not None):
        return max_travelers_error
    return None
def validate_budget_greater_equal_expense(data,existing):
    if "budget" not in data:
        return None
    if existing.total_expenses()>data["budget"]:
        return jsonify({"error":"INVALID_BUDGET_AMOUNT","message":f"New budget must be greater than existing expenses.Existing total expenses: {existing.total_expenses()}"}),409
def validate_update_trip(data):
    checks_applied=0
    if "destination" in data:
        checks_applied+=1
        destination_error=validate_text(data,"destination",120)
        if destination_error is not None:
            return destination_error
    if "start_date" in data:
        checks_applied+=1
        start_date_error=validate_date(data,"start_date")
        if start_date_error is not None:
            return start_date_error
    if "end_date" in data:
        checks_applied+=1
        end_date_error=validate_date(data,"end_date")
        if end_date_error is not None:
            return end_date_error
    if "budget" in data:
        checks_applied+=1
        budget_error=validate_positive_number(data,"budget")
        if budget_error is not None:
            return budget_error
    if "max_travelers" in data:
        checks_applied+=1
        max_travelers_error=validate_positive_int(data,"max_travelers")
        if max_travelers_error is not None:
            return max_travelers_error
    if checks_applied==0:
        return jsonify({"error":"EMPTY_REQUEST_BODY","message":"Request body must be a non-empty JSON object"}),400
    return None

def validate_update_trip_time(data,existing):
    if "start_date" in data or "end_date" in data:
        start=None
        end=None
        if "start_date" in data:
            start=datetime.strptime(data["start_date"].strip(),"%Y-%m-%d").date()
        else:
            start=existing.start_date
        if "end_date" in data:
            end=datetime.strptime(data["end_date"].strip(),"%Y-%m-%d").date()
        else:
            end=existing.end_date
        if start is not None and end is not None and end<start:
            return jsonify({"error":"INVALID_DATE_RANGE","message":"end_date must be on or after start_date"}),400
    return None
def validate_time_update_for_travelers(trip):
    travelers_with_overlap=[]
    for membership in trip.travelers:
        traveler=membership.traveler
        if not traveler.can_join_trip(trip):
            travelers_with_overlap.append(traveler.email)
    if len(travelers_with_overlap)>0:
        return jsonify({"error":"DATE_CONFLICT_WITH_TRAVELERS","message":f"date update conflicts with other trips of these travelers: {', '.join(travelers_with_overlap)}"}),409
    return None
def validate_update_trip_status(data,existing):
    missing_field_error=validate_missing_field(data,["status"])
    if missing_field_error is not None:
        return missing_field_error
    status=data["status"].strip().upper()
    if status not in [TripStatus.planned.value,TripStatus.ongoing.value,TripStatus.completed.value,TripStatus.cancelled.value]:
        return jsonify({"error": "INVALID_STATUS", "message": f"invalid status : status must be from [{TripStatus.planned.value} , {TripStatus.ongoing.value} , {TripStatus.completed.value} , {TripStatus.cancelled.value}]"}), 400
    if status== TripStatus.planned.value:
        if existing.status != TripStatus.planned.value:
            return jsonify({"error":"INVALID_STATUS_TRANSITION","message":f"cannot set status from {existing.status} to {status}"}),409
    if status== TripStatus.ongoing.value:
        if existing.status != TripStatus.planned.value:
            return jsonify({"error":"INVALID_STATUS_TRANSITION","message":f"cannot set status from {existing.status} to {status}"}),409
    if status== TripStatus.completed.value:
        if existing.status != TripStatus.ongoing.value:
            return jsonify({"error":"INVALID_STATUS_TRANSITION","message":f"cannot set status from {existing.status} to {status}"}),409
    if status== TripStatus.cancelled.value:
        if existing.status == TripStatus.completed.value :
            return jsonify({"error":"INVALID_STATUS_TRANSITION","message":f"cannot set status from {existing.status} to {status}"}),409
    return None

def validate_max_trip_travelers(data,existing):
    if "max_travelers" in data:
        if not existing.can_update_max(data["max_travelers"]):
            return jsonify({"error":"MAX_TRAVELERS_BELOW_CURRENT","message":f"cannot set max traveller below the number of travellers already assigned in this trip"}),409
    return None

def validate_traveler(data):
    missing_field_error=validate_missing_field(data,["email","name"])
    if missing_field_error is not None:
        return missing_field_error
    email_error=validate_email(data,"email")
    if email_error is not None:
        return email_error
    name_error=validate_text(data,"name",120)
    if name_error is not None:
        return name_error
    return None

def validate_add_trip_expenses(data):
    missing_field_error=validate_missing_field(data,["title","amount"])
    if missing_field_error is not None:
        return missing_field_error
    title_error=validate_text(data,"title",120)
    if title_error is not None:
        return title_error
    amount_error=validate_positive_number(data,"amount")
    if amount_error is not None:
        return amount_error
    return None