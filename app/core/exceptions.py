"""Custom application exceptions and global exception handlers.

These exceptions are raised by services/repositories and translated into
HTTP responses by the handlers registered in :mod:`app.main`.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.responses import Response


class AppException(HTTPException):
    """Base application exception carrying a stable error code."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or "APP_ERROR"


class BadRequestError(AppException):
    def __init__(self, detail: str = "Bad request", error_code: str = "BAD_REQUEST") -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, error_code)


class AuthenticationError(AppException):
    def __init__(self, detail: str = "Could not validate credentials", error_code: str = "AUTH_ERROR") -> None:
        super().__init__(
            status.HTTP_401_UNAUTHORIZED,
            detail,
            error_code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(AppException):
    def __init__(self, detail: str = "Not enough permissions", error_code: str = "FORBIDDEN") -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, error_code)


class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, error_code)


class ConflictError(AppException):
    def __init__(self, detail: str = "Resource already exists", error_code: str = "CONFLICT") -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail, error_code)


def _error_response(status_code: int, detail: str, error_code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": error_code, "message": detail}},
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:  # noqa: ARG001
    """Handle :class:`AppException` subclasses."""
    return _error_response(exc.status_code, exc.detail, exc.error_code)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:  # noqa: ARG001
    """Normalise FastAPI's :class:`HTTPException` into the error envelope."""
    return _error_response(exc.status_code, str(exc.detail), "HTTP_ERROR")


async def validation_exception_handler(
    request: Request, exc: RequestValidationError  # noqa: ARG001
) -> JSONResponse:
    """Convert 422 validation errors into a structured envelope."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": jsonable_encoder(exc.errors()),
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    """Catch-all for unhandled exceptions -> 500 without leaking internals."""
    from app.core.logging import get_logger

    get_logger("exceptions").exception("Unhandled exception: %s", exc)
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Internal server error",
        "INTERNAL_ERROR",
    )


__all__ = [
    "AppException",
    "BadRequestError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "app_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
    "generic_exception_handler",
    "Response",
    "Any",
]
