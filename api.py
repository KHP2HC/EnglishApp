"""EnglishCoach Pro — FastAPI application.

Configures the FastAPI application with:
- Centralized configuration (environment variables)
- Supabase JWT authentication
- Role-based authorization (user / admin)
- Configurable CORS
- Security headers
- Rate limiting
- Structured logging with request IDs
- Consistent error handling
- Input validation via Pydantic
- Domain routers for all Web API endpoints

All new endpoints use /api/v1/ prefix.
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import get_settings
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
from core.web_schemas import HealthResponse as WebHealthResponse

# ── Domain routers ─────────────────────────────────────
from routers import (
    errors as errors_router,
    planner as planner_router,
    profile as profile_router,
    progress as progress_router,
    reviews as reviews_router,
    study_sessions as study_sessions_router,
    vocabulary as vocabulary_router,
    writing as writing_router,
)

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

# ── Include domain routers ─────────────────────────────
app.include_router(profile_router.router)
app.include_router(vocabulary_router.router)
app.include_router(reviews_router.router)
app.include_router(study_sessions_router.router)
app.include_router(progress_router.router)
app.include_router(planner_router.router)
app.include_router(errors_router.router)
app.include_router(writing_router.router)

# ── Health Check ───────────────────────────────────────


@app.get("/api/v1/health", response_model=WebHealthResponse)
def health_check() -> WebHealthResponse:
    """Liveness probe. Returns 200 when the API process is running."""
    return WebHealthResponse(status="healthy")


# ── Reading Tests (public endpoints) ──────────────────


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
