"""SQLAlchemy ORM model for prediction history records."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class PredictionHistory(Base):
    """A single malaria prediction made by a user.

    The full request payload (symptoms, exposure, demographics) is stored in
    ``symptoms`` as JSON, while the model's structured output is split into
    dedicated columns for efficient querying/statistics.
    """

    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    prediction: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    risk: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    recommendation: Mapped[str] = mapped_column(String(500), nullable=False)
    advice: Mapped[list[Any]] = mapped_column(JSON, nullable=False)
    symptoms: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="predictions"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PredictionHistory id={self.id} user_id={self.user_id} risk={self.risk!r}>"
