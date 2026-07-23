"""Routes package aggregating all routers."""

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.prediction import router as prediction_router

__all__ = ["admin_router", "auth_router", "prediction_router"]
