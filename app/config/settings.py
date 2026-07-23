"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root: app/config/settings.py -> ../../
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Values are read from a local ``.env`` file (or real environment variables).
    Defaults are tuned for local SQLite development and are overridden in
    production via the environment.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "AfriSafe AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True

    # --- Security ---
    SECRET_KEY: str = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET_KEY_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Database ---
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'afrisafe.db'}"

    # --- Machine Learning ---
    MODEL_PATH: Path = BASE_DIR / "Model" / "malaria_model.pkl"
    FEATURE_NAMES_PATH: Path = BASE_DIR / "Model" / "feature_names.pkl"

    # --- CORS ---
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8000",
    ]

    # --- Rate limiting (ready; enforced by middleware when enabled) ---
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # --- Logging ---
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` singleton."""
    return Settings()


settings = get_settings()
