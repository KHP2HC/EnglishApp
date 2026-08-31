"""Structured application logging for EnglishCoach Pro.

Provides:
- JSON-structured log output in production, human-readable in development.
- Request ID generation and propagation.
- Request/response logging middleware.
- Safe logging that never exposes secrets.

NEVER log:
- passwords
- JWT tokens
- API keys
- Authorization headers
- Supabase service role key
- private user data unnecessarily
"""

from __future__ import annotations

import logging
import sys
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import get_settings

# ── Sensitive header names that must never be logged ──
_SENSITIVE_HEADERS = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "x-supabase-key",
        "x-service-role-key",
    }
)

# ── Logger configuration ───────────────────────────────


class SafeFormatter(logging.Formatter):
    """Logging formatter that redacts known sensitive patterns."""

    # Patterns to redact from log messages.
    _REDACT_PLACEHOLDER = "[REDACTED]"

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        # Redact Authorization header values if they slip into messages.
        # This is a safety net — code should avoid logging them directly.
        if "bearer " in msg.lower():
            import re

            msg = re.sub(
                r"[Bb]earer\s+\S+",
                "Bearer [REDACTED]",
                msg,
            )
        return msg


def setup_logging() -> None:
    """Configure application-wide logging.

    - Production: JSON-like structured output at INFO level.
    - Development: Human-readable output at the configured level.
    """
    settings = get_settings()
    level = getattr(logging, settings.LOG_LEVEL, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicate output.
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if settings.is_production:
        fmt = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    handler.setFormatter(SafeFormatter(fmt))
    root_logger.addHandler(handler)

    # Reduce noise from libraries.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# ── Request ID ─────────────────────────────────────────


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return uuid.uuid4().hex


# ── Request/Response Logging Middleware ────────────────


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log each request with method, path, status code, and duration.

    Never logs request bodies, Authorization headers, or cookies.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or generate_request_id()

        # Attach request_id to request state for downstream use.
        request.state.request_id = request_id

        start_time = time.perf_counter()

        # Log the incoming request (safe fields only).
        logger = logging.getLogger("englishcoach.requests")
        logger.info(
            "request_start method=%s path=%s request_id=%s",
            request.method,
            request.url.path,
            request_id,
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_error method=%s path=%s request_id=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                request_id,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log the response.
        logger.info(
            "request_end method=%s path=%s status=%d duration_ms=%.2f request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        # Add request ID to response headers.
        response.headers["X-Request-ID"] = request_id
        return response


def get_safe_headers(headers) -> dict:
    """Return a dict of headers with sensitive values redacted.

    Utility function for safe debug logging if needed.
    """
    safe = {}
    for key, value in headers.items():
        if key.lower() in _SENSITIVE_HEADERS:
            safe[key] = "[REDACTED]"
        else:
            safe[key] = value
    return safe
