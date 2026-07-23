"""Tests for the health check endpoint."""

from __future__ import annotations


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert "database_status" in data
    assert "model_loaded" in data
    assert "version" in data


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AfriSafe" in response.json()["message"]
