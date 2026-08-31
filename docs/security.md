# Security Architecture — EnglishCoach Pro

## Overview

Phase 1 establishes the security foundation for the FastAPI backend.
This document describes the authentication, authorization, CORS, rate
limiting, security headers, secret management, logging, and error
handling design.

## Authentication Architecture

### JWT Validation

FastAPI validates Supabase-issued JWT access tokens.

**Flow:**

```
Request
  → Extract Bearer token from Authorization header
  → Validate JWT signature, expiry, audience
  → Extract user identity (sub, email, role)
  → Return AuthenticatedUser
  → Route handler receives authenticated user
```

**Key points:**

- The `Authorization: Bearer <access_token>` header is required for
  protected endpoints.
- Tokens are validated using the `JWT_SECRET` configured via
  environment variable.
- The `sub` claim is the canonical user identifier (Supabase user UUID).
- The `email` claim is extracted for convenience.
- The `role` claim is extracted for authorization (see below).
- Internal JWT validation errors are **never** returned to the client.
  All failures return a generic `"Invalid token."` or
  `"Token has expired."` message.

### AuthenticatedUser

The `AuthenticatedUser` dataclass is the safe representation of an
authenticated user:

| Field  | Type           | Source         |
|--------|----------------|----------------|
| `id`   | `str`          | JWT `sub`      |
| `email`| `str \| None`  | JWT `email`    |
| `role` | `str`          | JWT `role`     |

Raw JWT claims are stored in `_claims` for advanced use but are never
exposed to clients.

### Dependencies

| Dependency          | Purpose                                  |
|---------------------|------------------------------------------|
| `get_current_user`  | Require valid JWT, return `AuthenticatedUser` |
| `get_current_user_id` | Require valid JWT, return user ID only  |
| `require_admin`      | Require valid JWT + `admin` role        |
| `require_roles(...)` | Require valid JWT + one of specified roles |
| `get_optional_user`  | Return user if token present, else `None` |

## Authorization

### Role-Based Access Control

Two roles are supported:

| Role    | Description                              |
|---------|------------------------------------------|
| `user`  | Standard authenticated user (default)    |
| `admin` | Administrator with elevated access       |

**Role source:** The `role` claim from the validated Supabase JWT.

**Assumption:** If the Supabase JWT contains a `role` claim (configured
via a database trigger or auth hook), it is trusted for authorization
decisions. If the `role` claim is absent, the user is treated as a
standard `user`.

**Future enhancement:** If more granular role management is needed,
roles should be looked up from a server-side database table rather
than relying solely on JWT claims.

**Security guarantee:** Roles are **never** trusted from request
bodies or client-supplied data. They always come from the validated
JWT.

## CORS Configuration

CORS origins are configurable via the `CORS_ORIGINS` environment
variable (comma-separated).

**Development:**

```
CORS_ORIGINS=http://localhost:5173,http://localhost:4173,http://localhost:8000
```

**Production:**

```
CORS_ORIGINS=https://app.example.com
```

**Rules:**

- `allow_origins=["*"]` is **never** used for authenticated APIs.
- Only explicitly configured origins are allowed.
- `allow_credentials=True` is set (required for cookie-based auth).
- Allowed methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`.
- Allowed headers: `Authorization`, `Content-Type`, `X-Request-ID`.

## Rate Limiting

### Implementation

An in-process sliding-window rate limiter is used.

| Scope             | Config                              | Default |
|-------------------|-------------------------------------|---------|
| Global (all endpoints) | `RATE_LIMIT_DEFAULT_REQUESTS` / `RATE_LIMIT_DEFAULT_WINDOW_SECONDS` | 100 / 60s |
| Auth-sensitive    | `RATE_LIMIT_AUTH_REQUESTS` / `RATE_LIMIT_AUTH_WINDOW_SECONDS` | 10 / 60s |

**Health-check paths** (`/api/v1/health`, `/`) use a 5x higher limit so
infrastructure monitoring is not throttled.

### Limitation

> ⚠️ This in-process implementation is **not sufficient** for
> horizontally scaled production deployments. Each API instance
> maintains its own counter. For production with multiple instances,
> use Redis-backed rate limiting or an API gateway with distributed
> rate limiting.

## Security Headers

### Always-On Headers

| Header                   | Value                            |
|--------------------------|----------------------------------|
| `X-Content-Type-Options` | `nosniff`                        |
| `X-Frame-Options`        | `DENY`                           |
| `Referrer-Policy`        | `strict-origin-when-cross-origin` |
| `X-XSS-Protection`       | `1; mode=block`                  |

### Production-Only Headers

| Header                       | Value                                      |
|------------------------------|--------------------------------------------|
| `Strict-Transport-Security`  | `max-age=31536000; includeSubDomains; preload` |
| `Content-Security-Policy`    | Strict CSP (see below)                     |

**Production CSP:**

```
default-src 'self';
script-src 'self';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
font-src 'self';
connect-src 'self';
frame-ancestors 'none';
base-uri 'self';
form-action 'self'
```

### Development CSP

Development uses a relaxed CSP to allow Swagger/OpenAPI UI and Vite
HMR:

```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
font-src 'self' data:;
connect-src 'self' ws: wss: http: https:;
frame-ancestors 'none'
```

## Secret Management

### Environment Variables

All secrets are sourced from environment variables. No credentials
are hard-coded, printed, or committed.

| Variable                    | Scope         | Exposed to frontend? |
|-----------------------------|---------------|----------------------|
| `SUPABASE_URL`              | Public        | ✅ Yes               |
| `SUPABASE_ANON_KEY`         | Public        | ✅ Yes (subject to RLS) |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-only   | ❌ **Never**          |
| `JWT_SECRET`                | Server-only   | ❌ **Never**          |

### Rules

- `SUPABASE_SERVICE_ROLE_KEY` must **never** appear in:
  - React code
  - Vite environment variables exposed to browser
  - HTML
  - API responses
  - Git
  - Logs
- `.env.example` contains **placeholders only**.
- `.env` is gitignored and must never be committed.

### Frontend Verification

The web frontend (`web/`) was audited:

- ✅ No service role key references found.
- ✅ Supabase client uses only `VITE_SUPABASE_URL` and
  `VITE_SUPABASE_ANON_KEY`.
- ✅ No hard-coded JWT tokens or API keys in `web/src/`.
- ✅ Edge functions read secrets from `Deno.env` at runtime.

## Logging Policy

### What Is Logged

| Field          | Example                              |
|----------------|--------------------------------------|
| Request method | `GET`                                |
| Request path   | `/api/v1/health`                     |
| Status code    | `200`                                |
| Duration       | `12.34ms`                            |
| Request ID     | `a1b2c3d4...`                       |
| Error category | `Unhandled exception on GET /path`   |

### What Is Never Logged

- Passwords
- JWT tokens
- API keys
- Authorization headers (redacted if they appear in messages)
- Supabase service role key
- Private user data unnecessarily

### Log Format

- **Production:** JSON-structured (`{"time":..., "level":..., ...}`)
- **Development:** Human-readable (`timestamp | LEVEL | logger | message`)

### Request IDs

Each request is assigned a unique ID (UUID hex). The ID is:
1. Attached to `request.state.request_id`.
2. Added to the response header `X-Request-ID`.
3. Included in all log messages for that request.

## Error Handling

### Standard Error Response Shape

```json
{
  "error": {
    "message": "Human-readable message",
    "code": "ERROR_CODE"
  }
}
```

### What Is Never Exposed

- Stack traces
- SQL errors
- Database credentials
- Internal paths
- JWT internals
- Secret configuration

### Environment Differences

- **Development:** Unhandled exceptions return `str(exc)` for debugging.
- **Production:** Unhandled exceptions return `"An internal error occurred."`.

## Database Security

### Current Access Strategy

The application currently uses **SQLAlchemy with SQLite** for local
development. The database URL is configurable via `DATABASE_URL`.

**Future:** Migration to PostgreSQL via Supabase is planned for a
later phase.

### Rules

- Database credentials come from environment variables.
- Service-role credentials are **never** sent to the frontend.
- Service-role credentials are **never** returned by APIs.
- Database errors are caught by global exception handlers and
  replaced with safe error messages.

## Health Endpoint

```
GET /api/v1/health
```

**Response:**

```json
{
  "status": "healthy"
}
```

- Liveness probe only — does not check database or external services.
- Always returns 200 if the process is alive.
- Does not expose infrastructure details.
