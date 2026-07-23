"""Prediction routes: predict, history, delete."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.prediction import (
    PredictionHistoryItem,
    PredictionHistoryList,
    PredictionRequest,
    PredictionResponse,
)
from app.services.prediction_service import PredictionService

logger = get_logger("routes.prediction")

router = APIRouter(prefix="/prediction", tags=["Prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict malaria risk",
    description=(
        "Accept patient information, symptoms, duration, mosquito exposure, "
        "travel and drug history. Runs the ML model, classifies risk, returns "
        "tailored recommendations, and saves the prediction to the user's history."
    ),
)
def predict(
    payload: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    service = PredictionService(db)
    record = service.create_prediction(current_user, payload)
    return PredictionResponse(
        prediction=record.prediction,
        confidence=record.confidence,
        risk=record.risk,
        recommendation=record.recommendation,
        advice=record.advice,
        symptoms=record.symptoms,
        timestamp=record.created_at if record.created_at.tzinfo else record.created_at.replace(tzinfo=timezone.utc),
    )


@router.get(
    "/history",
    response_model=PredictionHistoryList,
    summary="List prediction history",
    description="Return the authenticated user's prediction history (newest first).",
)
def list_history(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionHistoryList:
    service = PredictionService(db)
    total, items = service.list_history(current_user, skip=skip, limit=limit)
    return PredictionHistoryList(
        total=total,
        items=[PredictionHistoryItem.model_validate(item) for item in items],
    )


@router.delete(
    "/history/{prediction_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a prediction",
    description="Delete a prediction record owned by the authenticated user.",
)
def delete_history(
    prediction_id: int = Path(..., gt=0, description="Prediction record id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service = PredictionService(db)
    service.delete_history(current_user, prediction_id)
