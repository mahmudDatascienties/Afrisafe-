"""API package."""

from app.api.routes import admin_router, auth_router, prediction_router

__all__ = ["admin_router", "auth_router", "prediction_router"]
