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
    