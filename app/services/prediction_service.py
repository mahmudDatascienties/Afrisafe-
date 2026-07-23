"""Prediction service: runs inference, persists results, queries history."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.prediction_history import PredictionHistory
from app.models.user import User
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.prediction import PredictionRequest
from app.services.triage import triage_assessment

logger = get_logger("prediction")


class PredictionService:
    """Handles prediction creation and history management."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PredictionRepository(db)

    def create_prediction(
        self, user: User, payload: PredictionRequest
    ) -> PredictionHistory:
        """Run the ML triage for ``payload`` and persist the result for ``user``."""
        payload_dict = payload.model_dump()
        result = triage_assessment(payload_dict)

        record = PredictionHistory(
            user_id=user.id,
            prediction=result["prediction"],
            confidence=result["confidence"],
            risk=result["risk"],
            recommendation=result["recommendation"],
            advice=result["advice"],
            symptoms=payload_dict,
        )
        record = self.repo.create(record)
        logger.info(
            "Saved prediction id=%s for user id=%s risk=%s",
            record.id, user.id, record.risk,
        )
        return record

    def list_history(self, user: User, skip: int = 0, limit: int = 50) -> tuple[int, list[PredictionHistory]]:
        """Return ``(total, items)`` for the authenticated user."""
        total = self.repo.count_by_user(user.id)
        items = self.repo.list_by_user(user.id, skip=skip, limit=limit)
        return total, items

    def delete_history(self, user: User, prediction_id: int) -> None:
        """Delete a prediction record owned by ``user``."""
        record = self.repo.get_by_id(prediction_id)
        if record is None:
            raise NotFoundError("Prediction not found")
        if record.user_id != user.id and user.role != "admin":
            raise ForbiddenError("You can only delete your own predictions")
        self.repo.delete(record)
        logger.info("Deleted prediction id=%s by user id=%s", prediction_id, user.id)
