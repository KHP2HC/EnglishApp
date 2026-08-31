# API Security — EnglishCoach Pro

## API Versioning

All new endpoints use the `/api/v1/` prefix.

Legacy endpoints (without `/v1/`) are preserved for backward
compatibility and are marked `include_in_schema=False`. They will be
removed in Phase 2.

## Endpoint Security Matrix

| Endpoint                              | Auth Required | Rate Limited | Admin Only |
|---------------------------------------|---------------|--------------|------------|
| `GET /api/v1/health`                  | ❌            | ✅ (5x limit) | ❌         |
| `POST /api/v1/vocab/rate`             | ✅            | ✅            | ❌         |
| `GET /api/v1/reading/tests`           | ❌            | ✅            | ❌         |
| `GET /api/v1/reading/test/{id}`       | ❌            | ✅            | ❌         |
| `POST /api/v1/reading/test/{id}/grade`| ❌            | ✅            | ❌         |
| `GET /api/v1/admin/stats`             | ✅            | ✅            | ✅         |
| `POST /api/vocab/rate` (legacy)       | ❌            | ✅            | ❌         |
| `GET /api/reading/tests` (legacy)     | ❌            | ✅            | ❌         |
| `GET /api/reading/test/{id}` (legacy) | ❌            | ✅            | ❌         |
| `POST /api/reading/test/{id}/grade` (legacy) | ❌     | ✅            | ❌         |

## Authentication

### How to Authenticate

Include a valid Supabase JWT in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Error Responses

| Status | When                                      | Message                        |
|--------|-------------------------------------------|--------------------------------|
| 401    | Missing Authorization header              | `Authentication required.`     |
| 401    | Malformed Authorization header           | `Authentication required.`     |
| 401    | Invalid JWT (bad signature, wrong secret) | `Invalid token.`               |
| 401    | Expired JWT                               | `Token has expired.`           |
| 401    | JWT_SECRET not configured                 | `Authentication is not properly configured.` |
| 403    | Authenticated but insufficient role       | `Insufficient permissions.`    |

### Security Guarantees

- JWT validation errors are **never** exposed to the client.
- The `WWW-Authenticate: Bearer` header is included in 401 responses.
- Token values are **never** logged.
- The authenticated user identity **always** comes from the validated
  JWT, never from request bodies.

## Authorization

### Role-Based Access

```python
from core.security import require_admin, require_roles

# Admin-only endpoint
@app.get("/api/v1/admin/stats", dependencies=[Depends(require_admin)])
def admin_stats(): ...

# Multiple roles
@app.get(
    "/api/v1/manager-only",
    dependencies=[Depends(require_roles("admin", "manager"))],
)
def manager_endpoint(): ...
```

### Role Source

Roles come from the `role` claim in the validated Supabase JWT.

**Assumption:** The `role` claim is trusted when configured via a
Supabase database trigger or auth hook. If absent, the user is
treated as `user`.

**Future:** For more granular control, implement a server-side role
lookup table.

## Input Validation

All API inputs are validated with Pydantic:

| Field        | Type   | Constraints                          |
|--------------|--------|--------------------------------------|
| `card_id`    | `int`  | `ge=1` (must be positive)            |
| `quality`    | `int`  | `ge=0, le=5` (SM-2 quality scale)    |
| `answers`    | `dict` | `max_length=200` keys                |

Validation errors return `422` with:

```json
{
  "error": {
    "message": "Invalid request data.",
    "code": "VALIDATION_ERROR"
  }
}
```

## Rate Limiting

### Global Middleware

All requests pass through `RateLimitMiddleware` which enforces a
per-IP sliding-window limit.

| Configuration                    | Default | Scope           |
|----------------------------------|---------|-----------------|
| `RATE_LIMIT_DEFAULT_REQUESTS`   | 100     | All endpoints   |
| `RATE_LIMIT_DEFAULT_WINDOW_SECONDS` | 60   | All endpoints   |
| `RATE_LIMIT_AUTH_REQUESTS`       | 10      | Auth endpoints  |
| `RATE_LIMIT_AUTH_WINDOW_SECONDS` | 60      | Auth endpoints  |

Health-check paths (`/api/v1/health`, `/`) use a 5x higher limit.

### Rate Limit Response

```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

```json
{
  "error": {
    "message": "Rate limit exceeded. Please try again later."
  }
}
```

## CORS

See [security.md](./security.md#cors-configuration) for full CORS
configuration.

## Security Headers

See [security.md](./security.md#security-headers) for full header
configuration.

## Error Response Format

All errors follow a consistent shape:

```json
{
  "error": {
    "message": "...",
    "code": "..."
  }
}
```

| Status | Code                | When                          |
|--------|---------------------|-------------------------------|
| 401    | —                   | Authentication failure        |
| 403    | —                   | Authorization failure          |
| 404    | —                   | Resource not found             |
| 422    | `VALIDATION_ERROR`  | Input validation failure      |
| 429    | —                   | Rate limit exceeded            |
| 500    | `INTERNAL_ERROR`    | Unhandled exception            |

## Request IDs

Every response includes an `X-Request-ID` header. If the client
provides one in the request, it is used; otherwise a new UUID is
generated.

```
X-Request-ID: a1b2c3d4e5f6...
```
