"""Tests for admin endpoints: users, predictions, statistics."""

from __future__ import annotations

from app.models.user import User


REGISTER_PAYLOAD = {
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "strongpassword123",
    "state": "Lagos",
    "lga": "Ikeja",
    "age": 28,
    "gender": "Female",
    "phone_number": "+2348000000000",
}

PREDICT_PAYLOAD = {
    "age": 25,
    "gender": "Male",
    "state": "Kano",
    "lga": "Nassarawa",
    "symptoms": ["High Fever", "Headache", "Chills"],
    "duration": 3,
    "mosquito_exposure": True,
    "travel_history": False,
    "drug_history": False,
}


def _register(client) -> dict[str, str]:
    reg = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD).json()
    return {"Authorization": f"Bearer {reg['access_token']}"}


def _promote_to_admin(db, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.role = "admin"
        db.commit()


def _admin_headers(client, db) -> dict[str, str]:
    _register(client)
    _promote_to_admin(db, "test@example.com")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "strongpassword123"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_admin_endpoints_require_admin(client):
    headers = _register(client)
    assert client.get("/api/v1/admin/users", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/predictions", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/statistics", headers=headers).status_code == 403


def test_admin_endpoints_require_auth(client):
    assert client.get("/api/v1/admin/users").status_code == 401
    assert client.get("/api/v1/admin/predictions").status_code == 401
    assert client.get("/api/v1/admin/statistics").status_code == 401


def test_admin_list_users(client, db):
    headers = _admin_headers(client, db)
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["email"] == "test@example.com"


def test_admin_list_predictions(client, db):
    headers = _admin_headers(client, db)
    client.post("/api/v1/prediction/predict", json=PREDICT_PAYLOAD, headers=headers)
    response = client.get("/api/v1/admin/predictions", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["prediction"] in ("Malaria", "No Malaria")


def test_admin_statistics(client, db):
    headers = _admin_headers(client, db)
    client.post("/api/v1/prediction/predict", json=PREDICT_PAYLOAD, headers=headers)
    response = client.get("/api/v1/admin/statistics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 1
    assert data["total_predictions"] == 1
    assert data["positive_cases"] + data["negative_cases"] == 1
    assert data["average_confidence"] >= 0.0
