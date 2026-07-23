"""General-purpose utilities."""

from __future__ import annotations

from typing import Any


def safe_int(value: Any, default: int = 0) -> int:
    """Best-effort int conversion with a default on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
