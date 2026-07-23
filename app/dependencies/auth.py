"""Shared FastAPI dependencies (current user, admin guard)."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ForbiddenError
from app.core.security import decode_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from the Bearer token.

    Raises 401 if the token is missing, malformed, or the user no longer exists.
    """
    if not token:
        raise AuthenticationError("Not authenticated")
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise AuthenticationError("Invalid or expired access token")

    subject = payload.get("sub")
    if subject is None:
        raise AuthenticationError("Invalid token payload")

    user = UserRepository(db).get_by_id(int(subject))
    if user is None:
        raise AuthenticationError("User not found")
    if not user.is_active:
        raise AuthenticationError("Account is deactivated")
    return user


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """Return the current user, ensuring the account is active.

    ``get_current_user`` already checks ``is_active``, so this dependency
    exists as a separately-named guard for endpoints that want to express the
    *active* requirement explicitly in their dependency chain.
    """
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """Require the authenticated user to have the ``admin`` role."""
    if user.role != "admin":
        raise ForbiddenError("Admin privileges required")
    return user
