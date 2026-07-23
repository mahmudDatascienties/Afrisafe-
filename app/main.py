"""FastAPI application entry point for the AfriSafe AI backend.

Run with::

    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.api.routes import admin_router, auth_router, prediction_router
from app.config.settings import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import get_logger
from app.database.session import init_db
from app.middleware.rate_limit import RateLimitMiddleware
from app.ml.model_service import get_model

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Startup: create tables, load the ML model. Shutdown: log."""
    logger.info("Starting %s v%s (%s)", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
    init_db()
    try:
        get_model()
        logger.info("ML model ready")
    except AppException as exc:
        logger.error("ML model unavailable: %s", exc.detail)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "An AI-powered Malaria Risk Prediction System for Nigeria. "
        "Provides JWT authentication, ML-driven triage, prediction history, "
        "and an admin dashboard."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# --- Middleware ---
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception handlers ---
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(IntegrityError, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# --- Routers ---
api_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(prediction_router, prefix=api_prefix)
app.include_router(admin_router, prefix=api_prefix)


# --- Health & root ---
@app.get("/api/v1/health", tags=["System"], summary="Health check")
def health_check() -> dict[str, str | bool | int]:
    """Report service status and whether the ML model is loaded."""
    from app.ml.model_service import MLModel

    model = MLModel()
    return {
        "status": "ok" if model.loaded else "degraded",
        "model_loaded": model.loaded,
        "feature_names_count": len(model.feature_names),
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["System"], summary="API root")
def root() -> dict[str, str]:
    """Welcome message."""
    return {"message": f"Welcome to {settings.APP_NAME} API. See /docs for documentation."}
