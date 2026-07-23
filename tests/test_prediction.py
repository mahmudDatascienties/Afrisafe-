"""Tests for the prediction endpoint and history management."""

from __future__ import annotations


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


def _auth_headers(client) -> dict[str, str]:
    reg = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD).json()
    return {"Authorization": f"Bearer {reg['access_token']}"}


def test_predict_requires_auth(client):
    response = client.post("/api/v1/prediction/predict", json=PREDICT_PAYLOAD)
    assert response.status_code == 401


def test_predict_success(client):
    headers = _auth_headers(client)
    response = client.post("/api/v1/prediction/predict", json=PREDICT_PAYLOAD, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in ("Malaria", "No Malaria")
    assert 0.0 <= data["confidence"] <= 100.0
    assert data["risk"] in ("Low", "Medium", "High")
    assert isinstance(data["advice"], list) and len(data["advice"]) > 0
    assert "timestamp" in data


def test_predict_invalid_input(client):
    headers = _auth_headers(client)
    bad = dict(PREDICT_PAYLOAD, age=200)
    response = client.post("/api/v1/prediction/predict", json=bad, headers=headers)
    assert response.status_code == 422


def test_history_returns_user_predictions(client):
    headers = _auth_headers(client)
    client.post("/api/v1/prediction/predict", json=PREDICT_PAYLOAD, headers=headers)
    client.post("/api/v1/prediction/predict", json=PREDICT_PAYLOAD, headers=headers)
    response = client.get("/api/v1/prediction/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_history_requires_auth(client):
    response = client.get("/api/v1/prediction/history")
    assert response.status_code == 401


def test_delete_history(client):
    headers = _auth_headers(client)
    client.post("/api/v1/prediction/predict", json=PREDICT_PAYLOAD, headers=headers)
    hist = client.get("/api/v1/prediction/history", headers=headers).json()
    prediction_id = hist["items"][0]["id"]
    response = client.delete(f"/api/v1/prediction/history/{prediction_id}", headers=headers)
    assert response.status_code == 204
    # Confirm deletion.
    hist = client.get("/api/v1/prediction/history", headers=headers).json()
    assert hist["total"] == 0


def test_delete_nonexistent_returns_404(client):
    headers = _auth_headers(client)
    response = client.delete("/api/v1/prediction/history/9999", headers=headers)
    assert response.status_code == 404
