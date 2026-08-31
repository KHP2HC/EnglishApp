# Target Architecture — EnglishCoach Pro

## 1. Current Architecture

```
┌─────────────────────────┐     ┌─────────────────────────┐
│   Desktop App           │     │   Web App               │
│   (CustomTkinter)        │     │   (React + TypeScript)  │
│                         │     │                         │
│   ┌───────────────────┐ │     │ ┌───────────────────┐   │
│   │ UI (12 screens)   │ │     │ │ UI (14 pages)     │   │
│   ├───────────────────┤ │     │ ├───────────────────┤   │
│   │ Business Logic    │ │     │ │ Business Logic    │   │
│   │ (Python, core/*)  │ │     │ │ (TS, lib/*)       │   │
│   ├───────────────────┤ │     │ ├───────────────────┤   │
│   │ SQLite            │ │     │ │ Supabase Client   │   │
│   │ (SQLAlchemy)      │ │     │ │ (direct access)   │   │
│   └───────────────────┘ │     │ └───────────────────┘   │
└─────────────────────────┘     └───────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │   Supabase (PostgreSQL)   │
                              │   (Auth + DB + Edge Fn)   │
                              └───────────────────────────┘

┌─────────────────────────┐
│   FastAPI (api.py)      │  ← UNUSED by both clients
│   - 5 endpoints         │
│   - No authentication   │
│   - SQLite only         │
└─────────────────────────┘
```

### Problems

1. **Two separate data silos**: Desktop uses SQLite, web uses Supabase. No shared data.
2. **Duplicated business logic**: SRS, planner, CAT, band conversion — all implemented twice in different languages with diverging behavior.
3. **FastAPI is a ghost**: 5 endpoints exist but neither client uses them.
4. **No authentication on desktop**: Single-user, no login, no account sharing.
5. **Direct database access from frontend**: React accesses Supabase directly, bypassing any backend.
6. **Schema divergence**: SQLite and Supabase have different table names, column names, ID types, and constraints.
7. **No sync capability**: Desktop data cannot reach Supabase and vice versa.

---

## 2. Target Architecture

```
┌─────────────────────────┐     ┌─────────────────────────┐
│   Desktop App           │     │   Web App               │
│   (CustomTkinter)       │     │   (React + TypeScript)  │
│                         │     │                         │
│   ┌───────────────────┐ │     │ ┌───────────────────┐   │
│   │ UI (12 screens)   │ │     │ │ UI (14 pages)     │   │
│   ├───────────────────┤ │     │ ├───────────────────┤   │
│   │ Local SQLite      │ │     │ │ API Client         │   │
│   │ (offline cache)   │ │     │ │ (fetch/axios)     │   │
│   ├───────────────────┤ │     │ └───────┬───────────┘   │
│   │ Sync Engine       │ │             │                 │
│   │ (queue + retry)   │ │             │                 │
│   └───────┬───────────┘ │             │                 │
└───────────┼─────────────┘             │                 │
            │                           │                 │
            │   ┌───────────────────────▼─────────────┐    │
            └──►│   FastAPI Backend                   │◄───┘
                │                                    │
                │   ┌──────────────────────────────┐  │
                │   │ Authentication (JWT/Supabase) │  │
                │   ├──────────────────────────────┤  │
                │   │ Business Logic (single source)│  │
                │   │ - SRS Engine                 │  │
                │   │ - Study Planner              │  │
                │   │ - CAT Engine                 │  │
                │   │ - Analytics                  │  │
                │   │ - AI Tutor (proxy)           │  │
                │   │ - Content Fetcher            │  │
                │   │ - Sync Engine                │  │
                │   └──────────────────────────────┘  │
                │   ┌──────────────────────────────┐  │
                │   │ Data Access Layer            │  │
                │   │ (SQLAlchemy → PostgreSQL)    │  │
                │   └──────────────────────────────┘  │
                └───────────────┬────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  PostgreSQL / Supabase │
                    │  (source of truth)     │
                    └───────────────────────┘
```

### Key Principles

| Principle | Description |
|-----------|-------------|
| **API-first** | All data access goes through FastAPI. No direct DB access from clients. |
| **Single source of truth** | PostgreSQL/Supabase is authoritative. SQLite is a local cache. |
| **Shared business logic** | All business logic lives in FastAPI. Clients are thin. |
| **Centralized auth** | Supabase Auth with JWT validation in FastAPI. |
| **Offline-capable desktop** | SQLite + sync queue for offline desktop use. |
| **Online-only web** | Web always goes through API. No local database. |

---

## 3. Migration Roadmap

### Phase 1: Current System Stabilization

**Goal**: Fix critical issues without changing architecture.

| Item | Description |
|------|-------------|
| Add authentication to FastAPI | Validate Supabase JWT on all endpoints |
| Add missing API endpoints | User profile, vocab, sessions, progress |
| Add input validation | Pydantic models for all request/response bodies |
| Add rate limiting | Prevent abuse on public API |
| Add error handling | Consistent error responses |
| Add OpenAPI docs | Auto-generated from FastAPI |

**Files affected**: `api.py`, new `api/` package structure
**Risks**: Low — additive changes only
**Tests required**: API endpoint tests with auth
**Rollback**: Revert to current `api.py`

---

### Phase 2: Centralize Backend API

**Goal**: Move all business logic to FastAPI. Both clients call the API.

| Item | Description |
|------|-------------|
| Move SRS engine to API | `/api/v1/vocab/rate` with auth |
| Move study planner to API | `/api/v1/planner/generate` with auth |
| Move analytics to API | `/api/v1/analytics/*` with auth |
| Move content fetcher to API | `/api/v1/content/*` with auth |
| Move AI tutor to API | `/api/v1/writing/feedback` (proxy to Claude) |
| Move reading tests to API | `/api/v1/reading/*` with auth |
| Add user management endpoints | CRUD for user profile |
| Add session management endpoints | Start/end/list study sessions |
| Add error journal endpoints | CRUD for error entries |

**Files affected**: `api.py` → `api/` package, `core/*` (refactored as services)
**Risks**: Medium — web frontend must switch from Supabase direct to API
**Tests required**: Full API test suite, integration tests for both clients
**Rollback**: Web frontend can fall back to Supabase direct access

---

### Phase 3: Centralize Authentication

**Goal**: Single authentication system for both clients.

| Item | Description |
|------|-------------|
| Desktop login flow | Email/password via Supabase Auth (embedded) |
| FastAPI JWT validation | Verify Supabase JWT on every request |
| Web auth unchanged | Already uses Supabase Auth |
| Shared user identity | Same `user_id` (UUID) across desktop and web |
| Token refresh | Desktop stores refresh token securely |

**Files affected**: `main.py`, `api.py`, new `core/auth.py`
**Risks**: Medium — desktop users must create accounts
**Tests required**: Auth flow tests, token validation tests
**Rollback**: Desktop can operate without auth (current behavior)

---

### Phase 4: Centralize Learning Data

**Goal**: PostgreSQL/Supabase becomes the source of truth for all learning data.

| Item | Description |
|------|-------------|
| Unify schema | Single canonical schema for both SQLite and PostgreSQL |
| Add `client_id` (UUID) to all entities | For sync and idempotency |
| Add `updated_at` to all entities | For conflict resolution |
| Add `deleted_at` to all entities | For soft deletes |
| Add unique constraints | `(user_id, card_id)` on vocab_progress, etc. |
| Add database indexes | On `user_id`, `next_review`, `updated_at` |
| Migrate SQLite to use UUIDs | Replace integer IDs with UUIDs |
| Add Alembic migrations | Replace `migrate_schema()` |

**Files affected**: `data/models.py`, `data/database.py`, new `alembic/` directory
**Risks**: High — requires SQLite schema migration, potential data loss
**Tests required**: Migration tests, data integrity tests
**Rollback**: Backup SQLite before migration, restore if needed

---

### Phase 5: Desktop Synchronization

**Goal**: Desktop app syncs with PostgreSQL when online, works offline.

| Item | Description |
|------|-------------|
| Add `sync_queue` table to SQLite | Track pending changes |
| Add sync worker | Background thread, runs every 30s when online |
| Add sync API endpoints | `/api/v1/sync/push`, `/api/v1/sync/pull` |
| Implement conflict resolution | LWW with `updated_at` |
| Implement retry mechanism | Exponential backoff, max 6 retries |
| Add sync status UI | Show sync state in settings/dashboard |
| Add manual sync trigger | "Sync now" button |

**Files affected**: new `core/sync.py`, `data/models.py` (sync_queue), `ui/screens/settings.py`
**Risks**: High — complex distributed systems concerns
**Tests required**: Sync integration tests, conflict resolution tests, offline tests
**Rollback**: Disable sync, revert to SQLite-only mode

---

### Phase 6: Production Deployment

**Goal**: Deploy the system for public use.

| Item | Description |
|------|-------------|
| Deploy FastAPI to container platform | Docker container on Railway/Render/Fly.io |
| Deploy web frontend to Cloudflare Pages | Vite build → static hosting |
| Configure Supabase production project | Production database, auth, edge functions |
| Set up GitHub Actions secrets | API keys, Supabase keys, deploy tokens |
| Configure custom domains | API domain + frontend domain |
| Set up monitoring | Uptime monitoring, error tracking |
| Set up backups | Daily PostgreSQL backups |
| Load testing | Verify API handles expected traffic |

**Files affected**: `Dockerfile`, `docker-compose.yml`, `.github/workflows/`, `.env.example`
**Risks**: Medium — infrastructure configuration
**Tests required**: End-to-end deployment test, smoke tests
**Rollback**: Redeploy previous container image

---

### Phase 7: Monitoring and Maintenance

**Goal**: Keep the system healthy in production.

| Item | Description |
|------|-------------|
| Add structured logging | JSON logs with request IDs |
| Add health monitoring | `/api/v1/health` with DB connectivity check |
| Add metrics | Request count, latency, error rate |
| Add alerting | Email/webhook on errors, downtime |
| Add user feedback channel | In-app feedback form |
| Set up CI/CD pipeline | Auto-deploy on merge to main |
| Dependency updates | Monthly dependency review |
| Security audits | Quarterly security review |

**Files affected**: `api.py` (logging middleware), new `monitoring/` config
**Risks**: Low — observability improvements
**Tests required**: Monitoring integration tests
**Rollback**: Disable monitoring features

---

## 4. Migration Phase Summary

| Phase | Goal | Duration (est.) | Risk |
|-------|------|-----------------|------|
| 1. Stabilization | Auth + validation + docs | 1–2 weeks | Low |
| 2. Centralize API | Move all logic to FastAPI | 3–4 weeks | Medium |
| 3. Centralize Auth | Shared accounts | 1–2 weeks | Medium |
| 4. Centralize Data | Unify schema, UUIDs | 2–3 weeks | High |
| 5. Desktop Sync | Offline + sync | 3–4 weeks | High |
| 6. Production Deploy | Public launch | 1–2 weeks | Medium |
| 7. Monitoring | Long-term health | Ongoing | Low |

**Total estimated timeline: 12–18 weeks**
