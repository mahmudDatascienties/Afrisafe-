"""Simple in-memory rate limiting middleware (ready to enable via settings).

When ``RATE_LIMIT_ENABLED`` is true, each client IP is limited to
``RATE_LIMIT_REQUESTS`` requests per ``RATE_LIMIT_WINDOW_SECONDS`` second
window. This is intentionally simple and dependency-free; for production scale
swap the storage for Redis.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger("middleware.ratelimit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token-bucket-ish sliding window rate limiter keyed by client IP."""

    def __init__(self, app) -> None:  # noqa: ANN001
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:  # noqa: ANN001
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        limit = settings.RATE_LIMIT_REQUESTS

        bucket = self._hits[client]
        # Drop timestamps older than the window.
        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= limit:
            logger.warning("Rate limit exceeded for %s", client)
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please slow down.",
                    }
                },
            )

        bucket.append(now)
        return await call_next(request)
