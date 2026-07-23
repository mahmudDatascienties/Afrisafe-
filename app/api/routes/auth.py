"""Authentication routes: register, login, refresh, logout, me."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    MessageResponse,
    RefreshRequest,
    Token,
    TokenRefreshed,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.services.auth_service import AuthService

logger = get_logger("routes.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return JWT access + refresh tokens.",
)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> Token:
    service = AuthService(db)
    user, access, refresh = service.register(payload)
    return Token(access_token=access, refresh_token=refresh)


@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate with email + password and receive JWT tokens.",
)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    service = AuthService(db)
    user, access, refresh = service.login(payload)
    return Token(access_token=access, refresh_token=refresh)


@router.post(
    "/refresh",
    response_model=TokenRefreshed,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token.",
)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenRefreshed:
    service = AuthService(db)
    access = service.refresh_tokens(payload.refresh_token)
    return TokenRefreshed(access_token=access)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
    description="Revoke the supplied refresh token (stateful logout).",
)
def logout(
    payload: RefreshRequest = Body(...),
    db: Session = Depends(get_db),
) -> MessageResponse:
    service = AuthService(db)
    service.logout(payload.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=UserOut,
    summary="Current user",
    description="Return the authenticated user's profile.",
)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
