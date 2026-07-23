"""Tests for authentication flows: register, login, me, refresh, logout."""

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


def test_register_returns_tokens(client):
    response = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email_conflict(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    response = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 409


def test_login_success(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "strongpassword123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_me_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_returns_profile(client):
    reg = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD).json()
    token = reg["access_token"]
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_refresh_token(client):
    reg = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD).json()
    refresh = reg["refresh_token"]
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_logout_revokes_refresh(client):
    reg = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD).json()
    refresh = reg["refresh_token"]
    logout = client.post("/api/v1/auth/logout", json={"refresh_token": refresh})
    assert logout.status_code == 200
    # Refresh should now fail.
    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh}
    )
    assert response.status_code == 401
