"""Tests for the Web API — routers, authentication, and SRS.

Tests cover:
- Health endpoint
- Authentication (missing/invalid/expired JWT)
- Authorization (user vs admin)
- SRS engine (SM-2 algorithm)
- API endpoint structure
- Input validation
- Security (no secrets exposed)
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi.testclient import TestClient

# ── Test JWT helpers ───────────────────────────────────

JWT_SECRET = "test-jwt-secret-for-web-api-tests"
JWT_ALGORITHM = "HS256"
JWT_AUDIENCE = "authenticated"


def _make_jwt(
    sub: str = "user-123",
    email: str = "test@example.com",
    role: str = "user",
    expired: bool = False,
    secret: str = JWT_SECRET,
    audience: str = JWT_AUDIENCE,
) -> str:
    """Create a Supabase-style JWT for testing."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "email": email,
        "role": role,
        "aud": audience,
        "iat": now,
        "exp": now + timedelta(hours=1) if not expired else now - timedelta(hours=1),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


# ── Fixtures ────────────────────────────────────────────


@pytest.fixture()
def client(monkeypatch):
    """Create a test client with JWT_SECRET configured."""
    monkeypatch.setenv("JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("JWT_ALGORITHM", JWT_ALGORITHM)
    monkeypatch.setenv("JWT_AUDIENCE", JWT_AUDIENCE)
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-key")

    from core.config import reload_settings
    reload_settings()

    from api import app

    with TestClient(app) as c:
        yield c

    reload_settings()


@pytest.fixture()
def valid_token():
    return _make_jwt()


@pytest.fixture()
def admin_token():
    return _make_jwt(sub="admin-456", role="admin")


@pytest.fixture()
def expired_token():
    return _make_jwt(expired=True)


@pytest.fixture()
def auth_headers():
    return {"Authorization": f"Bearer {_make_jwt()}"}


@pytest.fixture()
def admin_headers():
    return {"Authorization": f"Bearer {_make_jwt(role='admin')}"}


# ── Health Endpoint ────────────────────────────────────


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_health_returns_healthy_status(self, client):
        resp = client.get("/api/v1/health")
        data = resp.json()
        assert data["status"] == "healthy"

    def test_health_does_not_expose_secrets(self, client):
        resp = client.get("/api/v1/health")
        text = resp.text.lower()
        assert "secret" not in text
        assert "password" not in text
        assert "service_role" not in text


# ── Authentication ─────────────────────────────────────


class TestAuthentication:
    def test_protected_endpoint_without_token_returns_401(self, client):
        """Endpoints requiring auth must reject requests without Authorization header."""
        resp = client.get("/api/v1/profile")
        assert resp.status_code == 401

    def test_malformed_authorization_header_returns_401(self, client):
        """Non-Bearer Authorization headers must be rejected."""
        resp = client.get(
            "/api/v1/profile",
            headers={"Authorization": "Basic abc123"},
        )
        assert resp.status_code == 401

    def test_invalid_jwt_returns_401(self, client):
        """Tokens signed with the wrong secret must be rejected."""
        bad_token = _make_jwt(secret="wrong-secret")
        resp = client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert resp.status_code == 401

    def test_expired_jwt_returns_401(self, client, expired_token):
        """Expired tokens must be rejected."""
        resp = client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == 401

    def test_error_response_does_not_expose_jwt_internals(self, client):
        """Error messages must not contain JWT validation details."""
        resp = client.get(
            "/api/v1/profile",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401
        text = resp.text.lower()
        assert "signature" not in text
        assert "decode" not in text
        assert "algorithm" not in text


# ── Authorization ───────────────────────────────────────


class TestAuthorization:
    def test_normal_user_denied_admin_endpoint(self, client, auth_headers):
        """Non-admin users must get 403 on admin-only endpoints."""
        resp = client.get("/api/v1/admin/stats", headers=auth_headers)
        assert resp.status_code == 403

    def test_admin_user_accesses_admin_endpoint(self, client, admin_headers):
        """Admin users should access admin-only endpoints."""
        resp = client.get("/api/v1/admin/stats", headers=admin_headers)
        assert resp.status_code == 200

    def test_unauthenticated_denied_admin_endpoint(self, client):
        """Unauthenticated requests must get 401 on admin endpoints."""
        resp = client.get("/api/v1/admin/stats")
        assert resp.status_code == 401


# ── CORS ───────────────────────────────────────────────


class TestCORS:
    def test_allowed_origin_gets_cors_headers(self, client):
        resp = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_disallowed_origin_no_cors_header(self, client):
        resp = client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("access-control-allow-origin") != "https://evil.example.com"

    def test_cors_not_wildcard(self, client):
        resp = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("access-control-allow-origin") != "*"


# ── Input Validation ───────────────────────────────────


class TestInputValidation:
    def test_quality_out_of_range_returns_422(self, client, valid_token):
        """SRS quality must be 0-5."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "test-card-id", "quality": 99},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 422

    def test_quality_negative_returns_422(self, client, valid_token):
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "test-card-id", "quality": -1},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 422

    def test_missing_card_id_returns_422(self, client, valid_token):
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"quality": 3},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 422

    def test_invalid_session_type_returns_422(self, client, valid_token):
        resp = client.post(
            "/api/v1/study-sessions",
            json={"session_type": "INVALID_TYPE"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 422


# ── SRS Engine ─────────────────────────────────────────


class TestSRSEngine:
    """Test the SM-2 spaced repetition algorithm."""

    def _make_progress(self, **kwargs):
        """Create a mock progress object for SRS testing."""
        p = MagicMock()
        p.srs_interval = kwargs.get("srs_interval", 1)
        p.srs_easiness = kwargs.get("srs_easiness", 2.5)
        p.srs_repetitions = kwargs.get("srs_repetitions", 0)
        p.next_review_date = kwargs.get("next_review_date", date.today())
        p.last_quality = kwargs.get("last_quality", None)
        p.times_seen = kwargs.get("times_seen", 0)
        p.times_correct = kwargs.get("times_correct", 0)
        return p

    def test_first_review_good_quality(self):
        """First review with quality >= 3 should set interval to 1 day."""
        from core.srs_engine import SRSEngine

        progress = self._make_progress(srs_repetitions=0)
        result = SRSEngine.update_card(progress, 3)

        assert result.srs_interval == 1
        assert result.srs_repetitions == 1
        assert result.times_seen == 1
        assert result.times_correct == 1

    def test_second_review_good_quality(self):
        """Second review with quality >= 3 should set interval to 6 days."""
        from core.srs_engine import SRSEngine

        progress = self._make_progress(srs_repetitions=1, srs_interval=1)
        result = SRSEngine.update_card(progress, 3)

        assert result.srs_interval == 6
        assert result.srs_repetitions == 2

    def test_failed_review_resets_repetitions(self):
        """Quality < 3 should reset repetitions to 0 and interval to 1."""
        from core.srs_engine import SRSEngine

        progress = self._make_progress(srs_repetitions=5, srs_interval=30)
        result = SRSEngine.update_card(progress, 0)

        assert result.srs_interval == 1
        assert result.srs_repetitions == 0
        assert result.times_seen == 1
        assert result.times_correct == 0  # not incremented for quality < 3

    def test_easiness_never_below_1_3(self):
        """Easiness factor must never go below 1.3."""
        from core.srs_engine import SRSEngine

        progress = self._make_progress(srs_easiness=1.3)
        result = SRSEngine.update_card(progress, 0)

        assert result.srs_easiness >= 1.3

    def test_invalid_quality_raises_error(self):
        """Quality outside 0-5 should raise ValueError."""
        from core.srs_engine import SRSEngine

        progress = self._make_progress()
        with pytest.raises(ValueError):
            SRSEngine.update_card(progress, -1)

        with pytest.raises(ValueError):
            SRSEngine.update_card(progress, 6)

    def test_times_correct_only_increments_on_success(self):
        """times_correct should only increment when quality >= 3."""
        from core.srs_engine import SRSEngine

        # Success
        progress = self._make_progress(times_correct=5)
        result = SRSEngine.update_card(progress, 3)
        assert result.times_correct == 6

        # Failure
        progress = self._make_progress(times_correct=5)
        result = SRSEngine.update_card(progress, 0)
        assert result.times_correct == 5

    def test_next_review_date_is_in_future(self):
        """Next review date should be in the future for successful reviews."""
        from core.srs_engine import SRSEngine

        progress = self._make_progress(srs_repetitions=2, srs_interval=6)
        result = SRSEngine.update_card(progress, 5)

        assert result.next_review_date > date.today()


# ── Security Headers ───────────────────────────────────


class TestSecurityHeaders:
    def test_x_content_type_options(self, client):
        resp = client.get("/api/v1/health")
        assert resp.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self, client):
        resp = client.get("/api/v1/health")
        assert resp.headers.get("x-frame-options") == "DENY"

    def test_referrer_policy(self, client):
        resp = client.get("/api/v1/health")
        assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"


# ── API Structure ──────────────────────────────────────


class TestAPIStructure:
    """Verify that all expected endpoints exist."""

    def test_vocabulary_endpoint_exists(self, client):
        """GET /api/v1/vocabulary should be accessible (may return empty)."""
        resp = client.get("/api/v1/vocabulary")
        # 200 (with empty data) or 503 (if Supabase not configured)
        assert resp.status_code in (200, 503)

    def test_reviews_due_requires_auth(self, client):
        """GET /api/v1/reviews/due should require authentication."""
        resp = client.get("/api/v1/reviews/due")
        assert resp.status_code == 401

    def test_study_sessions_requires_auth(self, client):
        """GET /api/v1/study-sessions should require authentication."""
        resp = client.get("/api/v1/study-sessions")
        assert resp.status_code == 401

    def test_progress_requires_auth(self, client):
        """GET /api/v1/progress/stats should require authentication."""
        resp = client.get("/api/v1/progress/stats")
        assert resp.status_code == 401

    def test_planner_requires_auth(self, client):
        """GET /api/v1/planner should require authentication."""
        resp = client.get("/api/v1/planner")
        assert resp.status_code == 401

    def test_errors_requires_auth(self, client):
        """GET /api/v1/errors should require authentication."""
        resp = client.get("/api/v1/errors")
        assert resp.status_code == 401

    def test_writing_requires_auth(self, client):
        """GET /api/v1/writing should require authentication."""
        resp = client.get("/api/v1/writing")
        assert resp.status_code == 401

    def test_profile_requires_auth(self, client):
        """GET /api/v1/profile should require authentication."""
        resp = client.get("/api/v1/profile")
        assert resp.status_code == 401

    def test_reading_tests_public(self, client):
        """GET /api/v1/reading/tests should be public."""
        resp = client.get("/api/v1/reading/tests")
        # 200 or 500 (if seed file missing) — but NOT 401
        assert resp.status_code != 401
