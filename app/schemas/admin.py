"""Pydantic v2 schemas for admin endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AdminUserOut(BaseModel):
    """Admin view of a user."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    state: str
    lga: str
    age: int
    gender: str
    phone_number: str | None
    role: str
    is_active: bool
    created_at: datetime


class AdminPredictionOut(BaseModel):
    """Admin view of a prediction record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    prediction: str
    confidence: float
    risk: str
    recommendation: str
    advice: list[Any]
    symptoms: dict[str, Any]
    created_at: datetime


class StatisticsResponse(BaseModel):
    """Aggregate platform statistics."""

    total_users: int
    total_predictions: int
    positive_cases: int
    negative_cases: int
    average_confidence: float
