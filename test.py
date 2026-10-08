import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.test_client() as client:
        yield client
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_unknown_route_returns_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.get_json()["error"] == "INVALID_ROUTE"


def test_wrong_method_returns_405(client):
    response = client.post("/health")
    assert response.status_code == 405
    assert response.get_json()["error"] == "INVALID_METHOD"

def test_create_trip(client):
    response=client.post("/api/v1/trips",json={
        "destination": "Cox's Bazar",
        "start_date": "2026-10-20",
        "end_date": "2026-10-23",
        "budget": 30000,
        "max_travelers": 5
    })
    created=response.get_json()
    assert response.status_code == 201
    assert created["status"] == "PLANNED"
    assert created["start_date"] == "2026-10-20"
    assert created["end_date"] == "2026-10-23"
    assert created["budget"] == 30000
    assert created["max_travelers"] == 5


def test_create_trip_destination_required(client):
    destination_required=client.post("/api/v1/trips",json={
        # "destination": "Cox's Bazar",
        "start_date": "2026-10-20",
        "end_date": "2026-10-23",
        "budget": 30000,
        "max_travelers": 5
    })
    
    assert destination_required.status_code == 400
    assert destination_required.get_json()["error"] == "MISSING_FIELDS"


def test_create_trip_start_date_required(client):
    start_date_required=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            # "start_date": "2026-10-20",
            "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert start_date_required.status_code == 400
    assert start_date_required.get_json()["error"] == "MISSING_FIELDS"


def test_create_trip_end_date_required(client):
    end_date_required=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-20",
            # "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert end_date_required.status_code == 400
    assert end_date_required.get_json()["error"] == "MISSING_FIELDS"


def test_create_trip_budget_required(client):
    budget_required=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-20",
            "end_date": "2026-10-23",
            # "budget": 30000,
            "max_travelers": 5
        })
        
    assert budget_required.status_code == 400
    assert budget_required.get_json()["error"] == "MISSING_FIELDS"


def test_create_trip_max_travelers_required(client):
    max_travelers_required=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-20",
            "end_date": "2026-10-23",
            "budget": 30000,
            # "max_travelers": 5
        })
        
    assert max_travelers_required.status_code == 400
    assert max_travelers_required.get_json()["error"] == "MISSING_FIELDS"


def test_create_trip_trims_whitespace(client):
    response=client.post("/api/v1/trips",json={
        "destination": "    Cox's Bazar  ",
        "start_date": "  2026-10-20      ",
        "end_date": "  2026-10-23       ",
        "budget": 30000,
        "max_travelers": 5
    })
    trimmed=response.get_json()
    assert response.status_code == 201
    assert trimmed["status"] == "PLANNED"
    assert trimmed["start_date"] == "2026-10-20"
    assert trimmed["end_date"] == "2026-10-23"


def test_create_trip_invalid_date_format(client):
    invalid_date_format=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-200",
            "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert invalid_date_format.status_code == 400
    assert invalid_date_format.get_json()["error"] == "INVALID_DATE_FORMAT"


def test_create_trip_invalid_date(client):
    invalid_date=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-32",
            "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert invalid_date.status_code == 400
    assert invalid_date.get_json()["error"] == "INVALID_DATE"


def test_create_trip_invalid_budget(client):
    invalid_budget=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-12",
            "end_date": "2026-10-23",
            "budget": 0000,
            "max_travelers": 5
        })
        
    assert invalid_budget.status_code == 400
    assert invalid_budget.get_json()["error"] == "NUMBER_NOT_POSITIVE"


def test_create_trip_invalid_max_travelers(client):
    invalid_max_travelers=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-12",
            "end_date": "2026-10-23",
            "budget": 60000,
            "max_travelers": 0
        })
        
    assert invalid_max_travelers.status_code == 400
    assert invalid_max_travelers.get_json()["error"] == "INTEGER_NOT_POSITIVE"


def test_create_trip_start_date_after_end_date(client):
    start_date_after_end_date=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-12",
            "end_date": "2026-10-10",
            "budget": 60000,
            "max_travelers": 6
        })
    assert start_date_after_end_date.status_code == 400
    assert start_date_after_end_date.get_json()["error"] == "INVALID_DATE_RANGE"

def test_create_trip_cannot_set_status(client):
    response=client.post("/api/v1/trips",json={
        "destination": "Cox's Bazar",
        "start_date": "2026-10-20",
        "end_date": "2026-10-23",
        "budget": 30000,
        "max_travelers": 5,
        "status": "ONGOING"
    })
    created=response.get_json()    
    assert created["status"]=="PLANNED"

def test_get_trip_not_existed(client):
    response=client.get("/api/v1/trips/1000")
    assert response.status_code == 404

def test_update_trip_with_empty_body(client):
    response=client.put("/api/v1/trips/1",json={
        "invalid":"nothing"
    })
    assert response.status_code == 400
    assert response.get_json()["error"]=="NO_VALID_UPDATE"

def test_update_trip_cannot_update_status(client):
    response=client.put("/api/v1/trips/1",json={
        "status":"ONGOING"
    })
    assert response.status_code == 400
    assert response.get_json()["error"]=="NO_VALID_UPDATE"

def test_update_trip_time_validation(client):
    response=client.post("/api/v1/trips",json={
        "destination": "Shilong",
        "start_date": "2026-10-20",
        "end_date": "2026-10-23",
        "budget": 30000,
        "max_travelers": 5
    })
    shilong_trip=response.get_json()

    start_date_after_end_date=client.put(f"/api/v1/trips/{shilong_trip["id"]}",json={
        "start_date": "2026-10-25"
    })
    assert start_date_after_end_date.status_code == 400
    assert start_date_after_end_date.get_json()["error"] == "INVALID_DATE_RANGE"
    
    end_date_before_start_date=client.put(f"/api/v1/trips/{shilong_trip["id"]}",json={
        "end_date": "2026-10-15"
    })
    assert end_date_before_start_date.status_code == 400
    assert end_date_before_start_date.get_json()["error"] == "INVALID_DATE_RANGE"

    valid_date_range=client.put(f"/api/v1/trips/{shilong_trip["id"]}",json={
        "start_date":"2026-10-10",
        "end_date": "2026-10-15"
    })
    assert valid_date_range.status_code == 200
    assert valid_date_range.get_json()["start_date"] == "2026-10-10"
    assert valid_date_range.get_json()["end_date"] == "2026-10-15"

