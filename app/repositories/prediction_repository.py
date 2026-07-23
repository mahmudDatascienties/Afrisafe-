"""Repository for :class:`PredictionHistory` persistence."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.prediction_history import PredictionHistory
from app.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[PredictionHistory]):
    """Data access for prediction history."""

    model = PredictionHistory

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id_: int) -> PredictionHistory | None:  # type: ignore[override]
        return self.db.get(PredictionHistory, id_)

    def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[PredictionHistory]:
        stmt = (
            select(PredictionHistory)
            .where(PredictionHistory.user_id == user_id)
            .order_by(PredictionHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def count_by_user(self, user_id: int) -> int:
        return self.db.scalar(
            select(func.count())
            .select_from(PredictionHistory)
            .where(PredictionHistory.user_id == user_id)
        ) or 0

    def count_by_prediction(self, prediction: str) -> int:
        return self.db.scalar(
            select(func.count())
            .select_from(PredictionHistory)
            .where(PredictionHistory.prediction == prediction)
        ) or 0

    def average_confidence(self) -> float:
        value = self.db.scalar(select(func.avg(PredictionHistory.confidence)))
        return float(value) if value is not None else 0.0
