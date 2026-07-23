"""Tests for the database models and repositories."""

from __future__ import annotations

from app.models.prediction_history import PredictionHistory
from app.models.user import User
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.user_repository import UserRepository


def test_create_and_fetch_user(db):
    repo = UserRepository(db)
    user = User(
        email="db@example.com",
        hashed_password="hashed",
        full_name="DB User",
        state="Lagos",
        lga="Ikeja",
        age=30,
        gender="Male",
    )
    created = repo.create(user)
    assert created.id is not None
    fetched = repo.get_by_email("db@example.com")
    assert fetched is not None
    assert fetched.full_name == "DB User"
    assert repo.email_exists("db@example.com") is True


def test_create_and_fetch_prediction(db):
    user_repo = UserRepository(db)
    pred_repo = PredictionRepository(db)

    user = user_repo.create(
        User(
            email="pred@example.com",
            hashed_password="hashed",
            full_name="Pred User",
            state="Kano",
            lga="Nassarawa",
            age=25,
            gender="Male",
        )
    )
    record = pred_repo.create(
        PredictionHistory(
            user_id=user.id,
            prediction="Malaria",
            confidence=87.5,
            risk="High",
            recommendation="See a doctor.",
            advice=["Rest", "Take ACT"],
            symptoms={"fever": True},
        )
    )
    assert record.id is not None
    items = pred_repo.list_by_user(user.id)
    assert len(items) == 1
    assert items[0].prediction == "Malaria"
    assert pred_repo.count_by_user(user.id) == 1
    assert pred_repo.count_by_prediction("Malaria") == 1
    assert pred_repo.average_confidence() == 87.5
