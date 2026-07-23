"""Admin routes: users, predictions, statistics."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.session import get_db
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.schemas.admin import AdminPredictionOut, AdminUserOut, StatisticsResponse
from app.services.admin_service import AdminService

logger = get_logger("routes.admin")

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users",
    response_model=list[AdminUserOut],
    summary="List all users",
    description="Return all registered users. Requires admin role.",
)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[User]:
    return AdminService(db).list_users(skip=skip, limit=limit)


@router.get(
    "/predictions",
    response_model=list[AdminPredictionOut],
    summary="List all predictions",
    description="Return all prediction records across all users. Requires admin role.",
)
def list_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return AdminService(db).list_predictions(skip=skip, limit=limit)


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Platform statistics",
    description="Aggregate platform metrics: users, predictions, cases, confidence. Requires admin role.",
)
def statistics(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> StatisticsResponse:
    return StatisticsResponse(**AdminService(db).statistics())
