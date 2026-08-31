"""Tests for Phase 1 security foundation.

Covers:
- Authentication (missing/malformed/invalid/expired/valid JWT)
- Authorization (user vs admin)
- CORS (allowed/disallowed origins)
- Input validation (invalid/oversized/missing input)
- Security (secrets not in responses, auth headers not logged,
  service-role key never exposed)
- Rate limiting
- Health endpoint
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from fastapi.testclient import TestClient

# ── Fixtures ────────────────────────────────────────────

JWT_SECRET = "test-jwt-secret-for-phase1-tests-only"
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


@pytest.fixture()
def client(monkeypatch):
    """Create a test client with JWT_SECRET configured."""
    # Patch settings to use our test JWT secret.
    monkeypatch.setenv("JWT_SECRET", JWT_SECRET)
    monkeypatch.setenv("JWT_ALGORITHM", JWT_ALGORITHM)
    monkeypatch.setenv("JWT_AUDIENCE", JWT_AUDIENCE)
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")

    # Force reload settings cache.
    from core.config import reload_settings

    reload_settings()

    # Import after settings are patched.
    from api import app

    with TestClient(app) as c:
        yield c

    # Clean up.
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
    def test_missing_authorization_header_returns_401(self, client):
        """Endpoint requiring auth must reject requests without Authorization header."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "card-1", "quality": 3},
        )
        assert resp.status_code == 401

    def test_malformed_authorization_header_returns_401(self, client):
        """Non-Bearer Authorization headers must be rejected."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "card-1", "quality": 3},
            headers={"Authorization": "Basic abc123"},
        )
        assert resp.status_code == 401

    def test_invalid_jwt_returns_401(self, client):
        """Tokens signed with the wrong secret must be rejected."""
        bad_token = _make_jwt(secret="wrong-secret")
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "card-1", "quality": 3},
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert resp.status_code == 401

    def test_expired_jwt_returns_401(self, client, expired_token):
        """Expired tokens must be rejected."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "card-1", "quality": 3},
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == 401

    def test_valid_jwt_passes_authentication(self, client, valid_token):
        """Valid JWTs should pass authentication (may 404/503 if card doesn't exist)."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "nonexistent-card", "quality": 3},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        # Should NOT be 401 — auth passed, just card not found or DB not configured.
        assert resp.status_code != 401

    def test_error_response_does_not_expose_jwt_internals(self, client):
        """Error messages must not contain JWT validation details."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "card-1", "quality": 3},
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
        """Requests from allowed origins should get CORS headers."""
        resp = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert (
            resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
        )

    def test_disallowed_origin_no_cors_header(self, client):
        """Requests from disallowed origins should NOT get CORS headers."""
        resp = client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS middleware should not add the allow-origin header for
        # disallowed origins.
        allow_origin = resp.headers.get("access-control-allow-origin")
        assert allow_origin != "https://evil.example.com"

    def test_cors_not_wildcard(self, client):
        """CORS must never return '*' for authenticated APIs."""
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
    def test_missing_required_field_returns_422(self, client):
        """Missing required fields must return 422."""
        resp = client.post(
            "/api/v1/reading/test/nonexistent/grade",
            json={},
        )
        assert resp.status_code == 422

    def test_quality_out_of_range_returns_422(self, client, valid_token):
        """SRS quality must be 0-5."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "card-1", "quality": 99},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 422

    def test_quality_negative_returns_422(self, client, valid_token):
        """Negative quality values must be rejected."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "card-1", "quality": -1},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 422

    def test_missing_card_id_returns_422(self, client, valid_token):
        """Missing card_id must be rejected."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"quality": 3},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert resp.status_code == 422

    def test_oversized_answers_dict_rejected(self, client):
        """Excessively large answer dicts must be rejected."""
        huge_answers = {str(i): "x" * 100 for i in range(300)}
        resp = client.post(
            "/api/v1/reading/test/nonexistent/grade",
            json={"answers": huge_answers},
        )
        assert resp.status_code == 422


# ── Security ───────────────────────────────────────────


class TestSecurity:
    def test_service_role_key_not_in_responses(self, client):
        """No API response should contain the service role key."""
        # Set a known service role key in the environment.
        with patch.dict(
            "os.environ",
            {"SUPABASE_SERVICE_ROLE_KEY": "super-secret-key-12345"},
        ):
            from core.config import reload_settings

            reload_settings()
            resp = client.get("/api/v1/health")
            assert "super-secret-key-12345" not in resp.text
            assert resp.status_code == 200

    def test_authorization_header_not_logged(self, client, caplog):
        """Authorization headers must not appear in log output."""
        import logging

        token = _make_jwt()
        with caplog.at_level(logging.DEBUG):
            client.get(
                "/api/v1/health",
                headers={"Authorization": f"Bearer {token}"},
            )

        for record in caplog.records:
            assert token not in record.getMessage()
            assert "Bearer " not in record.getMessage()

    def test_error_responses_are_safe(self, client):
        """Error responses must not expose stack traces or internals."""
        resp = client.post(
            "/api/v1/reviews/rate",
            json={"card_id": "card-1", "quality": 3},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        text = resp.text.lower()
        assert "traceback" not in text
        assert "sql" not in text
        assert "database" not in text
        assert "path" not in text or "path" not in (
            resp.json().get("error", {}).get("message", "").lower()
        )

    def test_security_headers_present(self, client):
        """Security headers should be present on responses."""
        resp = client.get("/api/v1/health")
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "DENY"
        assert "strict-origin-when-cross-origin" in resp.headers.get(
            "referrer-policy", ""
        )

    def test_request_id_in_response(self, client):
        """Responses should include a request ID header."""
        resp = client.get("/api/v1/health")
        assert "x-request-id" in resp.headers


# ── Rate Limiting ──────────────────────────────────────


class TestRateLimiting:
    def test_rate_limit_blocks_excessive_requests(self, client, monkeypatch):
        """Exceeding the rate limit should return 429."""
        from core.rate_limit import get_limiter

        # Reset limiter before test.
        get_limiter().reset()

        # Set a low limit for testing.
        monkeypatch.setenv("RATE_LIMIT_DEFAULT_REQUESTS", "3")
        monkeypatch.setenv("RATE_LIMIT_DEFAULT_WINDOW_SECONDS", "60")
        from core.config import reload_settings

        reload_settings()

        # Use a non-exempt endpoint (reading tests) so the global
        # middleware applies the configured limit directly.
        responses = []
        for _ in range(5):
            resp = client.get("/api/v1/reading/tests")
            responses.append(resp.status_code)

        # At least one should be 429 (rate limited).
        assert 429 in responses

        # Clean up.
        get_limiter().reset()
        reload_settings()


# ── Legacy Endpoint Compatibility ──────────────────────


class TestLegacyEndpoints:
    def test_legacy_health_still_works(self, client):
        """The original /api/v1/health endpoint must still work."""
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_legacy_reading_tests_endpoint(self, client):
        """The legacy /api/reading/tests endpoint must still work."""
        resp = client.get("/api/reading/tests")
        assert resp.status_code == 200

    def test_legacy_reading_test_detail(self, client):
        """The legacy /api/reading/test/{id} endpoint must still work."""
        resp = client.get("/api/reading/tests")
        if resp.json():
            test_id = resp.json()[0]["id"]
            detail = client.get(f"/api/reading/test/{test_id}")
            assert detail.status_code == 200
