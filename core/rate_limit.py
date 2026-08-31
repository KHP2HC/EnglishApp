"""In-process rate limiting for EnglishCoach Pro.

Uses a simple sliding-window counter per client IP.

⚠️  LIMITATION: This in-process implementation is NOT sufficient for
    horizontally scaled production deployments. When running multiple
    API instances behind a load balancer, each instance maintains its
    own counter. For production, use Redis-backed rate limiting or
    an API gateway with distributed rate limiting.

For local development and single-instance deployment this is adequate.
"""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from core.config import get_settings


class SlidingWindowRateLimiter:
    """Thread-safe sliding-window rate limiter.

    Tracks request counts per key (typically client IP) within a
    time window. When the window expires, the counter resets.
    """

    def __init__(self) -> None:
        # key -> (count, window_start_timestamp)
        self._counts: dict[str, tuple[int, float]] = defaultdict(
            lambda: (0, time.monotonic())
        )
        self._lock = Lock()

    def check(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> None:
        """Check if the key is within the rate limit.

        Raises HTTPException(429) if the limit is exceeded.
        """
        now = time.monotonic()

        with self._lock:
            count, window_start = self._counts[key]

            # Reset window if expired.
            if now - window_start >= window_seconds:
                count = 0
                window_start = now

            count += 1
            self._counts[key] = (count, window_start)

            if count > max_requests:
                retry_after = int(window_seconds - (now - window_start))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={"Retry-After": str(max(retry_after, 1))},
                )

    def reset(self) -> None:
        """Clear all rate limit counters (useful in tests)."""
        with self._lock:
            self._counts.clear()


# ── Singleton instance ──────────────────────────────────

_limiter = SlidingWindowRateLimiter()


def get_limiter() -> SlidingWindowRateLimiter:
    """Return the shared rate limiter instance."""
    return _limiter


# ── Client IP extraction ───────────────────────────────


def _get_client_ip(request: Request) -> str:
    """Extract the client IP address from the request.

    Checks X-Forwarded-For first (for reverse proxy setups),
    falls back to the direct client address.
    """
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        # Use the first IP in the chain.
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ── Dependency factories ────────────────────────────────


def rate_limit(
    max_requests: int | None = None,
    window_seconds: int | None = None,
):
    """Create a rate-limiting dependency.

    Usage:
        from fastapi import Depends

        @app.post(
            "/api/v1/auth/login",
            dependencies=[Depends(rate_limit(max_requests=10))],
        )
        def login(...):
            ...

    By default uses RATE_LIMIT_DEFAULT_REQUESTS / RATE_LIMIT_DEFAULT_WINDOW_SECONDS
    from configuration.
    """
    settings = get_settings()
    limit = max_requests or settings.RATE_LIMIT_DEFAULT_REQUESTS
    window = window_seconds or settings.RATE_LIMIT_DEFAULT_WINDOW_SECONDS

    def _check(request: Request) -> None:
        ip = _get_client_ip(request)
        _limiter.check(ip, limit, window)

    return _check


def auth_rate_limit():
    """Rate limiter for authentication-sensitive endpoints.

    Uses RATE_LIMIT_AUTH_REQUESTS / RATE_LIMIT_AUTH_WINDOW_SECONDS.
    """
    settings = get_settings()
    return rate_limit(
        max_requests=settings.RATE_LIMIT_AUTH_REQUESTS,
        window_seconds=settings.RATE_LIMIT_AUTH_WINDOW_SECONDS,
    )


# ── Global rate-limit middleware ───────────────────────


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply a global per-IP rate limit to ALL requests.

    This acts as a safety net on top of per-endpoint rate limits.
    Uses RATE_LIMIT_DEFAULT_REQUESTS / RATE_LIMIT_DEFAULT_WINDOW_SECONDS
    from configuration.

    Exempt paths (health checks) use a higher threshold so that
    infrastructure monitoring does not get throttled.
    """

    # Paths exempt from the global limiter (liveness probes).
    _EXEMPT_PATHS = frozenset({"/api/v1/health", "/"})

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        settings = get_settings()

        # Use a higher limit for health-check paths.
        if request.url.path in self._EXEMPT_PATHS:
            limit = settings.RATE_LIMIT_DEFAULT_REQUESTS * 5
        else:
            limit = settings.RATE_LIMIT_DEFAULT_REQUESTS

        ip = _get_client_ip(request)
        try:
            _limiter.check(ip, limit, settings.RATE_LIMIT_DEFAULT_WINDOW_SECONDS)
        except HTTPException as exc:
            from starlette.responses import JSONResponse

            return JSONResponse(
                status_code=exc.status_code,
                content={"error": {"message": exc.detail}},
                headers=exc.headers or {},
            )

        return await call_next(request)
