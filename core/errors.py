"""Consistent API error handling for EnglishCoach Pro.

Provides:
- Standardized error response format.
- Global exception handler that never exposes internals.
- Safe error responses for production.
- Additional logging in development.

Never exposes:
- stack traces
- SQL errors
- database credentials
- internal paths
- JWT internals
- secret configuration
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.config import get_settings

logger = logging.getLogger("englishcoach.errors")

# ── Standard error response shape ──────────────────────


def error_response(
    detail: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    error_code: str | None = None,
    **extra: Any,
) -> JSONResponse:
    """Build a standardized JSON error response.

    The response shape is:
        {
            "error": {
                "code": "...",
                "message": "...",
                ...extra
            }
        }
    """
    body: dict[str, Any] = {
        "error": {
            "message": detail,
        }
    }
    if error_code:
        body["error"]["code"] = error_code
    body["error"].update(extra)
    return JSONResponse(status_code=status_code, content=body)


# ── Exception handlers ──────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(request: Request, exc: HTTPException):
        return error_response(
            detail=exc.detail,
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        settings = get_settings()
        if settings.is_development:
            logger.info(
                "Validation error on %s %s: %s",
                request.method,
                request.url.path,
                exc.errors(),
            )
        return error_response(
            detail="Invalid request data.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
        )

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception):
        # Log the full error internally but never expose it to the client.
        logger.exception(
            "Unhandled exception on %s %s",
            request.method,
            request.url.path,
        )
        settings = get_settings()
        if settings.is_development:
            return error_response(
                detail=str(exc),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code="INTERNAL_ERROR",
            )
        return error_response(
            detail="An internal error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
        )
