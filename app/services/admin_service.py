"""Admin service: user/prediction listing and aggregate statistics."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.prediction_history import PredictionHistory
from app.models.user import User
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.user_repository import UserRepository

logger = get_logger("admin")


class AdminService:
    """Read-only administrative queries."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.predictions = PredictionRepository(db)

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.users.get_all(skip=skip, limit=limit)

    def list_predictions(self, skip: int = 0, limit: int = 100) -> list[PredictionHistory]:
        return self.predictions.get_all(skip=skip, limit=limit)

    def statistics(self) -> dict[str, int | float]:
        total_users = self.users.count()
        total_predictions = self.predictions.count()
        positive = self.predictions.count_by_prediction("Malaria")
        negative = self.predictions.count_by_prediction("No Malaria")
        avg_conf = self.predictions.average_confidence()
        stats = {
            "total_users": total_users,
            "total_predictions": total_predictions,
            "positive_cases": positive,
            "negative_cases": negative,
            "average_confidence": round(avg_conf, 2),
        }
        logger.info("Computed statistics: %s", stats)
        return stats
