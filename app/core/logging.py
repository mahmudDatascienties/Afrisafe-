"""Centralised logging configuration.

Configures a root application logger that writes to both the console and a
rotating file under ``app/logs/``. Importing :func:`get_logger` is the only
entry point needed across the codebase.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config.settings import settings


_LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

_LOGGER_NAME = "afrisafe"
_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
)
_DATEFMT = "%Y-%m-%d %H:%M:%S"

_configured = False


def _configure() -> None:
    global _configured
    if _configured:
        return

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(settings.LOG_LEVEL)
    logger.propagate = False

    formatter = logging.Formatter(_FORMAT, datefmt=_DATEFMT)

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Rotating file handler (1 MB per file, 5 backups)
    file_handler = RotatingFileHandler(
        _LOGS_DIR / "afrisafe.log",
        maxBytes=1_048_576,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _configured = True


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a configured logger under the application namespace."""
    _configure()
    return logging.getLogger(_LOGGER_NAME if name is None else f"{_LOGGER_NAME}.{name}")
