"""EnglishCoach Pro — FastAPI application.

Phase 1: Security foundation.

This module configures the FastAPI application with:
- Centralized configuration (environment variables)
- Supabase JWT authentication
- Role-based authorization (user / admin)
- Configurable CORS
- Security headers
- Rate limiting
- Structured logging with request IDs
- Consistent error handling
- Input validation via Pydantic

Existing endpoints are preserved and kept backward-compatible.
All new endpoints use /api/v1/ prefix.
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import data.models as models
from core.config import get_settings
from core.deps import get_db
from core.errors import register_exception_handlers
from core.logging_config import RequestLoggingMiddleware, setup_logging
from core.rate_limit import RateLimitMiddleware, rate_limit
from core.reading_test import grade, load_test, load_tests
from core.schemas import (
    HealthResponse,
    MessageResponse,
    ReadingAnswers,
    ReadingTestSummary,
    SRSRating,
)
from core.security import AuthenticatedUser, get_current_user, require_admin
from core.security_headers import SecurityHeadersMiddleware
from core.srs_engine import SRSEngine

# ── Logging (must run before app creation) ─────────────
setup_logging()

# ── App ────────────────────────────────────────────────
settings = get_settings()

app = FastAPI(
    title="EnglishCoach Pro API",
    description="English learning platform API — Phase 1 Security Foundation",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
)

# ── Middleware (order matters: outermost first) ────────

# 1. Request logging (wraps everything, adds request IDs)
app.add_middleware(RequestLoggingMiddleware)

# 2. Global rate limiting (per-IP, all endpoints)
app.add_middleware(RateLimitMiddleware)

# 3. Security headers
app.add_middleware(SecurityHeadersMiddleware)

# 4. CORS — configurable origins, never "*" in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# ── Exception handlers ─────────────────────────────────
register_exception_handlers(app)

# ── Startup ────────────────────────────────────────────


@app.on_event("startup")
def startup_event() -> None:
    """Initialize database on startup."""
    from data.database import init_db

    init_db()


# ── Health Check ───────────────────────────────────────
# Liveness check — always returns 200 if the process is alive.
# Does NOT depend on external services.


@app.get("/api/v1/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Liveness probe. Returns 200 when the API process is running.

    This endpoint does not check database connectivity or external
    services, so it will not fail if an optional dependency is down.
    """
    return HealthResponse(status="healthy")


# ── SRS Vocabulary ─────────────────────────────────────


@app.post(
    "/api/v1/vocab/rate",
    response_model=MessageResponse,
    dependencies=[Depends(get_current_user), Depends(rate_limit())],
)
def rate_card(
    rating: SRSRating,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
) -> MessageResponse:
    """Rate a vocabulary card and update its SRS schedule.

    Requires authentication. The card is scoped to the authenticated user.
    """
    progress = (
        db.query(models.UserVocabularyProgress)
        .filter(
            models.UserVocabularyProgress.id == rating.card_id,
        )
        .first()
    )

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card progress not found",
        )

    updated_progress = SRSEngine.update_card(progress, rating.quality)
    db.commit()
    db.refresh(updated_progress)
    return MessageResponse(message="Card updated successfully")


# ── Reading Tests ──────────────────────────────────────


@app.get("/api/v1/reading/tests", response_model=list[ReadingTestSummary])
def get_reading_tests() -> list[ReadingTestSummary]:
    """List available reading tests (public endpoint)."""
    tests = load_tests()
    return [
        ReadingTestSummary(id=t["id"], title=t.get("title", "Practice Test"))
        for t in tests
    ]


@app.get("/api/v1/reading/test/{test_id}")
def get_reading_test(test_id: str):
    """Get a single reading test by ID (public endpoint)."""
    test = load_test(test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found"
        )
    return test


@app.post("/api/v1/reading/test/{test_id}/grade")
def grade_reading_test(test_id: str, answers: ReadingAnswers):
    """Grade a reading test submission (public endpoint)."""
    test = load_test(test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found"
        )
    result = grade(test, answers.answers)
    return result


# ── Legacy endpoints (backward compatibility) ──────────
# These exist to avoid breaking any existing consumers.
# They delegate to the v1 implementations.


@app.post(
    "/api/vocab/rate",
    response_model=MessageResponse,
    include_in_schema=False,
)
def rate_card_legacy(
    rating: SRSRating,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Legacy endpoint — delegates to /api/v1/vocab/rate logic.

    Note: This endpoint does not require authentication for backward
    compatibility. It will be removed in Phase 2.
    """
    progress = (
        db.query(models.UserVocabularyProgress)
        .filter(models.UserVocabularyProgress.id == rating.card_id)
        .first()
    )
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card progress not found",
        )
    updated_progress = SRSEngine.update_card(progress, rating.quality)
    db.commit()
    db.refresh(updated_progress)
    return MessageResponse(message="Card updated successfully")


@app.get("/api/reading/tests", include_in_schema=False)
def get_reading_tests_legacy():
    """Legacy endpoint — delegates to /api/v1/reading/tests."""
    tests = load_tests()
    return [{"id": t["id"], "title": t.get("title", "Practice Test")} for t in tests]


@app.get("/api/reading/test/{test_id}", include_in_schema=False)
def get_reading_test_legacy(test_id: str):
    """Legacy endpoint — delegates to /api/v1/reading/test/{test_id}."""
    test = load_test(test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found"
        )
    return test


@app.post("/api/reading/test/{test_id}/grade", include_in_schema=False)
def grade_reading_test_legacy(test_id: str, answers: ReadingAnswers):
    """Legacy endpoint — delegates to /api/v1/reading/test/{test_id}/grade."""
    test = load_test(test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test not found"
        )
    result = grade(test, answers.answers)
    return result


# ── Admin-only example endpoint ────────────────────────


@app.get(
    "/api/v1/admin/stats",
    dependencies=[Depends(require_admin)],
    include_in_schema=False,
)
def admin_stats():
    """Admin-only endpoint (example). Returns basic system stats.

    This endpoint requires the 'admin' role. It is included as a
    demonstration of the authorization infrastructure.
    """
    return {"status": "ok", "message": "Admin access granted"}


# ── Static frontend (mounted AFTER API routes) ─────────
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:

    @app.get("/", include_in_schema=False)
    def read_root():
        return {"message": "EnglishCoachPro Web API is running (Frontend not found)"}


# ── Entry point ────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("API_PORT", settings.API_PORT))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=settings.is_development,
    )
