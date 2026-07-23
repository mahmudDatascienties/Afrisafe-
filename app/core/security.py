"""Security utilities: password hashing and JWT creation/verification."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh"]


def hash_password(password: str) -> str:
    """Return a bcrypt hash for the given plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    return pwd_context.verify(plain, hashed)


def create_token(
    subject: str | int,
    token_type: TokenType = "access",
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a signed JWT for the given subject.

    ``token_type`` controls the expiration window: ``access`` uses minutes,
    ``refresh`` uses days.
    """
    now = datetime.now(timezone.utc)
    if token_type == "refresh":
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str | int, extra_claims: dict[str, Any] | None = None) -> str:
    """Create an access JWT."""
    return create_token(subject, "access", extra_claims)


def create_refresh_token(subject: str | int) -> str:
    """Create a refresh JWT."""
    return create_token(subject, "refresh")


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode a JWT and return its payload, or ``None`` if invalid/expired."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
