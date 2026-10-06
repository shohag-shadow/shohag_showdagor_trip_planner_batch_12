from datetime import datetime
from math import isfinite
from flask import jsonify

def validate_date(body, field_name):
    value = body[field_name]
    if not isinstance(value, str) or not value.strip():
        return jsonify({"error": f"{field_name} must be a string in YYYY-MM-DD format"}), 400
    value = value.strip()
    try:
        datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": f"{field_name} must be a valid date in YYYY-MM-DD format"}), 400
    return None


def validate_positive_number(body, field_name):
    value = body[field_name]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return jsonify({"error": f"{field_name} must be a number"}), 400
    if not isfinite(value) or value <= 0:
        return jsonify({"error": f"{field_name} must be a positive number"}), 400
    return None

def validate_text(body, field_name, max_length=None):
    value=body[field_name]
    if not isinstance(value, str) or not value.strip():
        return jsonify({"error":f"{field_name} must be a non-empty string"}),400
    cleaned_value = value.strip()
    if max_length is not None and len(cleaned_value) > max_length:
        return jsonify({"error":f"{field_name} cannot be more than {max_length} characters"}),400
    return None

def validate_positive_int(body, field_name):
    value = body[field_name]
    if isinstance(value, bool) or not isinstance(value, int):
        return jsonify({"error": f"{field_name} must be an integer"}), 400
    if value <= 0:
        return jsonify({"error": f"{field_name} must be a positive integer"}), 400
    return None

def validate_missing_field(data,required_fields):
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing": missing_fields
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
    return jsonify({"error": "end_date must be on or after start_date"}), 400
    return None
    
def validate_create_trip(data):
    missing_fields_error=validate_missing_field(data,[
        "destination",
        "start_date",
        "end_date",
        "budget",
        "max_travelers"
        ])
    if(missing_fields_error!=None):
        return missing_fields_error
    destination_error=validate_text(data,"destination",120)
    if(destination_error is not None):
        return destination_error
    date_error=validate_start_end_date(data)
    if(date_error is not None):
        return date_error
    budget_error=validate_positive_number(data,"budget")
    if(budget_error is not None):
        return budget_error
    max_travelers_error=validate_positive_int(data,"max_travelers")
    if(max_travelers_error is not None):
        return max_travelers_error
    return None