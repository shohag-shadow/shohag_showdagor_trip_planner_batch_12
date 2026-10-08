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

    destination_required=client.post("/api/v1/trips",json={
        # "destination": "Cox's Bazar",
        "start_date": "2026-10-20",
        "end_date": "2026-10-23",
        "budget": 30000,
        "max_travelers": 5
    })
    
    assert destination_required.status_code == 400
    assert destination_required.get_json()["error"] == "MISSING_FIELDS"


    start_date_required=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            # "start_date": "2026-10-20",
            "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert start_date_required.status_code == 400
    assert start_date_required.get_json()["error"] == "MISSING_FIELDS"


    end_date_required=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-20",
            # "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert end_date_required.status_code == 400
    assert end_date_required.get_json()["error"] == "MISSING_FIELDS"


    budget_required=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            # "start_date": "2026-10-20",
            "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert budget_required.status_code == 400
    assert budget_required.get_json()["error"] == "MISSING_FIELDS"


    max_travelers_required=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            # "start_date": "2026-10-20",
            "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert max_travelers_required.status_code == 400
    assert max_travelers_required.get_json()["error"] == "MISSING_FIELDS"

    response=client.post("/api/v1/trips",json={
        "destination": "    Cox's Bazar  ",
        "start_date": "  2026-10-20      ",
        "end_date": "  2026-10-23       ",
        "budget": 30000,
        "max_travelers": 5
    })
    trimmed=response.get_json()
    assert response.status_code == 201
    assert created["status"] == "PLANNED"
    assert created["start_date"] == "2026-10-20"
    assert created["end_date"] == "2026-10-23"

    invalid_date_format=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-200",
            "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert invalid_date_format.status_code == 400
    assert invalid_date_format.get_json()["error"] == "INVALID_DATE_FORMAT"

    invalid_date=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-32",
            "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 5
        })
        
    assert invalid_date.status_code == 400
    assert invalid_date.get_json()["error"] == "INVALID_DATE"

    invalid_budget=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-12",
            "end_date": "2026-10-23",
            "budget": 0000,
            "max_travelers": 5
        })
        
    assert invalid_budget.status_code == 400
    assert invalid_budget.get_json()["error"] == "NUMBER_NOT_POSITIVE"

    invalid_max_travelers=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-12",
            "end_date": "2026-10-23",
            "budget": 60000,
            "max_travelers": 0
        })
        
    assert invalid_max_travelers.status_code == 400
    assert invalid_max_travelers.get_json()["error"] == "INTEGER_NOT_POSITIVE"

    start_date_after_end_date=client.post("/api/v1/trips",json={
            "destination": "Cox's Bazar",
            "start_date": "2026-10-12",
            "end_date": "2026-10-10",
            "budget": 60000,
            "max_travelers": 6
        })
    assert start_date_after_end_date.status_code == 400
    assert start_date_after_end_date.get_json()["error"] == "INVALID_DATE_RANGE"