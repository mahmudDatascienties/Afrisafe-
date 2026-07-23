"""Authentication service: registration, login, token refresh, logout."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserLogin, UserRegister

logger = get_logger("auth")


# In-memory refresh-token allowlist for logout revocation.
# In production this should be backed by Redis or a DB table.
_revoked_refresh_tokens: set[str] = set()


class AuthService:
    """Handles user registration, login, and token lifecycle."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: UserRegister) -> tuple[User, str, str]:
        """Create a new user and return ``(user, access_token, refresh_token)``."""
        if self.users.email_exists(payload.email):
            logger.warning("Registration conflict for email=%s", payload.email)
            raise ConflictError("A user with this email already exists")

        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            state=payload.state,
            lga=payload.lga,
            age=payload.age,
            gender=payload.gender,
            phone_number=payload.phone_number,
            role="user",
        )
        user = self.users.create(user)
        logger.info("Registered new user id=%s email=%s", user.id, user.email)

        access = create_access_token(
            user.id, extra_claims={"role": user.role, "email": user.email}
        )
        refresh = create_refresh_token(user.id)
        return user, access, refresh

    def login(self, payload: UserLogin) -> tuple[User, str, str]:
        """Authenticate a user and return ``(user, access_token, refresh_token)``."""
        user = self.users.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            logger.warning("Failed login attempt for email=%s", payload.email)
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        access = create_access_token(
            user.id, extra_claims={"role": user.role, "email": user.email}
        )
        refresh = create_refresh_token(user.id)
        logger.info("User id=%s logged in", user.id)
        return user, access, refresh

    def refresh_tokens(self, refresh_token: str) -> str:
        """Validate a refresh token and return a new access token."""
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid or expired refresh token")
        if refresh_token in _revoked_refresh_tokens:
            raise AuthenticationError("Refresh token has been revoked")

        user_id = payload.get("sub")
        user = self.users.get_by_id(int(user_id)) if user_id else None
        if user is None or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        access = create_access_token(
            user.id, extra_claims={"role": user.role, "email": user.email}
        )
        logger.info("Refreshed access token for user id=%s", user.id)
        return access

    def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token (stateful logout)."""
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            return
        _revoked_refresh_tokens.add(refresh_token)
        logger.info("Revoked refresh token for user id=%s", payload.get("sub"))
