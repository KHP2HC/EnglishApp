# Web MVP Final Report

**Date:** 2026-08-31  
**Version:** 1.0.0

---

## Architecture

EnglishCoach Pro is a full-stack web application with a clear three-tier architecture:

```
React + TypeScript + Vite  →  FastAPI + Python  →  Supabase PostgreSQL + Auth
```

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, React Router
- **Backend:** FastAPI, Pydantic, Supabase Python client, SM-2 SRS engine
- **Database:** Supabase PostgreSQL with Row Level Security (RLS) on all user-owned tables
- **Auth:** Supabase Auth with JWT validation on the backend

The frontend communicates exclusively through a typed API client layer (`src/api/`). Direct Supabase CRUD operations have been removed from all frontend code. The only direct Supabase calls are for auth operations (signup, signin, signout, session management).

---

## Implemented Features

| Feature | Status | Notes |
|---------|--------|-------|
| User registration | ✅ | Via Supabase Auth |
| User login | ✅ | Via Supabase Auth |
| User logout | ✅ | Via Supabase Auth |
| Session persistence | ✅ | Supabase SDK manages tokens |
| Onboarding wizard | ✅ | 5-step setup flow |
| Dashboard | ✅ | Streaks, XP, daily plan, word of day |
| Vocabulary list | ✅ | Paginated, searchable, filterable |
| SRS vocabulary review | ✅ | SM-2 algorithm, backend-owned |
| Study sessions | ✅ | Start, track, complete |
| Progress tracking | ✅ | Stats, heatmap, skill radar |
| Error journal | ✅ | CRUD with user isolation |
| Study planner | ✅ | Weekly plan generation |
| Writing practice | ✅ | Essay submission + AI feedback |
| Reading tests | ✅ | IELTS-style reading tests |
| Settings | ✅ | Profile, theme, language |
| Protected routes | ✅ | Auth-gated with redirect |
| Demo mode | ✅ | Works without backend (seed data) |

---

## API

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/health` | No | Liveness check |
| GET | `/api/v1/profile` | Yes | Get user profile |
| PATCH | `/api/v1/profile` | Yes | Update profile |
| GET | `/api/v1/vocabulary` | No | List vocabulary (paginated) |
| GET | `/api/v1/vocabulary/{id}` | No | Vocabulary detail |
| GET | `/api/v1/reviews/due` | Yes | Get due SRS cards |
| POST | `/api/v1/reviews/start` | Yes | Start new card progress |
| POST | `/api/v1/reviews/rate` | Yes | Rate card (SM-2 update) |
| GET | `/api/v1/study-sessions` | Yes | List sessions |
| POST | `/api/v1/study-sessions` | Yes | Start session |
| PATCH | `/api/v1/study-sessions/{id}` | Yes | Update/end session |
| GET | `/api/v1/study-sessions/{id}` | Yes | Get session detail |
| GET | `/api/v1/progress/stats` | Yes | Progress statistics |
| GET | `/api/v1/progress/activity` | Yes | Daily activity heatmap |
| GET | `/api/v1/planner` | Yes | Get study plan |
| POST | `/api/v1/planner` | Yes | Generate plan |
| GET | `/api/v1/errors` | Yes | List error journal |
| POST | `/api/v1/errors` | Yes | Create error entry |
| DELETE | `/api/v1/errors/{id}` | Yes | Delete error entry |
| GET | `/api/v1/writing` | Yes | List submissions |
| POST | `/api/v1/writing` | Yes | Submit essay + AI feedback |
| GET | `/api/v1/reading/tests` | No | List reading tests |
| GET | `/api/v1/reading/test/{id}` | No | Get reading test |
| POST | `/api/v1/reading/test/{id}/grade` | No | Grade reading test |

### Security Features

- JWT validation on all protected endpoints
- User identity derived from JWT (never from request body)
- All database queries scoped by authenticated `user_id`
- CORS with configurable origins (never `*` in production)
- Rate limiting (per-IP sliding window)
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Structured logging (never logs tokens or credentials)
- Error handling (never exposes stack traces or internals)

---

## Database

### Tables (11 migrations)

| # | Table | RLS | Description |
|---|-------|-----|-------------|
| 001 | extensions | N/A | pgcrypto, citext |
| 002 | profiles | ✅ | User profiles (auth.uid() = id) |
| 003 | vocab_cards | ✅ | Global vocabulary (public read) |
| 004 | vocab_progress | ✅ | SRS state (auth.uid() = user_id) |
| 005 | study_sessions | ✅ | Session history |
| 006 | error_journal | ✅ | Error tracking |
| 007 | study_plans | ✅ | Weekly plans |
| 008 | content_cache | ✅ | External content cache |
| 009 | writing_submissions | ✅ | Essay submissions |
| 010 | triggers | N/A | updated_at + auto-profile creation |
| 011 | migration_id_map | N/A | Legacy ID mapping (temporary) |

### Key Design Decisions

- UUID primary keys on all tables
- `profiles.id = auth.users.id` (1:1 relationship)
- `vocab_cards` is globally readable (public content)
- All user-owned tables have RLS with `auth.uid() = user_id`
- `next_review_at` is TIMESTAMPTZ (timezone-aware)
- Triggers auto-create profiles on auth signup
- Triggers auto-update `updated_at` on modifications

---

## Authentication

- **Provider:** Supabase Auth
- **Token:** JWT (HS256, Supabase-issued)
- **Validation:** Backend validates JWT signature using Supabase JWT secret
- **Identity:** `sub` claim = user ID, `email` claim = user email, `role` claim = user/admin
- **Session:** Frontend uses Supabase SDK for session management
- **Token refresh:** Handled by Supabase SDK (auto-refresh)
- **Logout:** Frontend calls `supabase.auth.signOut()`

---

## Security

| Measure | Status |
|---------|--------|
| JWT validation | ✅ All protected endpoints |
| User isolation | ✅ All queries scoped by JWT user_id |
| RLS | ✅ All user-owned tables |
| CORS | ✅ Configurable, never `*` in production |
| Rate limiting | ✅ Per-IP sliding window |
| Security headers | ✅ HSTS, CSP, X-Frame-Options, etc. |
| Input validation | ✅ Pydantic on all endpoints |
| Error sanitization | ✅ Never exposes internals |
| Secret management | ✅ Env vars, never committed |
| Service-role key | ✅ Backend-only, never in frontend |

---

## Frontend

### API Client Layer (`src/api/`)

| File | Domain |
|------|--------|
| `client.ts` | Core HTTP client (JWT, error handling) |
| `profile.ts` | Profile CRUD |
| `vocabulary.ts` | Vocabulary list/search/detail |
| `reviews.ts` | SRS due/start/rate |
| `sessions.ts` | Study session lifecycle |
| `progress.ts` | Stats and activity |
| `planner.ts` | Plan generation |
| `errors.ts` | Error journal |
| `writing.ts` | Writing submissions |
| `health.ts` | Health check |

### Direct Supabase CRUD Audit

✅ **No direct Supabase CRUD calls remain in the frontend.** All application data access goes through the API client. The only `supabase` references are for auth operations:
- `supabase.auth.signUp()`
- `supabase.auth.signInWithPassword()`
- `supabase.auth.signOut()`
- `supabase.auth.getSession()`
- `supabase.auth.onAuthStateChange()`

---

## Testing

### Backend Tests

| Test File | Coverage |
|-----------|----------|
| `tests/test_web_api.py` | Health, auth, authorization, CORS, validation, SRS engine, security headers, API structure |
| `tests/test_phase1_security.py` | Existing security tests (preserved) |

**Test count:** 30+ test cases

### Frontend Tests

| Test File | Coverage |
|-----------|----------|
| `web/src/api/__tests__/client.test.ts` | API client, error handling, domain client exports |

**Test count:** 6+ test cases

### Test Results

- **Backend tests:** ✅ **308 passed, 0 failed** (pytest, 6.25s)
- **Frontend tests:** ✅ **6 passed, 0 failed** (vitest, 1.27s)
- **Frontend lint:** ✅ **0 errors, 4 warnings** (eslint — warnings are react-hooks/exhaustive-deps, non-blocking)
- **TypeScript check:** ✅ **0 errors** (tsc --noEmit)
- **Frontend build:** ✅ **Build succeeded** (vite build, 4.58s, 3203 modules transformed)
- **Docker build:** ⚠️ **DOCKER BUILD NOT VERIFIED** (Docker not available on this machine)

---

## CI/CD

### GitHub Actions Workflows

| Workflow | Trigger | Jobs | Status |
|----------|---------|------|--------|
| `ci.yml` | push/PR to main, develop | Backend tests, Frontend lint + build | ✅ Verified syntax |
| `deploy-frontend.yml` | push to main (web/**) | Build + deploy to Cloudflare Pages | ✅ Verified syntax |
| `deploy-backend.yml` | push to main (api/**) | Build instructions for Docker deployment | ✅ Verified syntax |
| `build.yml` | tag push (v*) | Desktop EXE build + docs build | ✅ Verified syntax |

### CI Configuration

- ✅ CI runs on push (main, develop) and pull requests (main)
- ✅ Backend tests run before any deployment
- ✅ Frontend build runs in CI
- ✅ Secrets referenced through GitHub Secrets (no hard-coded secrets)
- ✅ Deploy workflows use `${{ secrets.* }}` for all credentials

---

## Deployment

### Deployment Status: **NOT YET DEPLOYED**

The application has passed all local quality gates (tests, lint, TypeScript, build). Deployment requires external account configuration (Supabase, hosting providers). See `docs/web-deployment.md` for exact instructions and `docs/DEPLOYMENT-CHECKLIST.md` for a step-by-step checklist.

---

## Performance

| Measure | Status |
|---------|--------|
| Server-side pagination | ✅ Vocabulary list |
| Query invalidation | ✅ TanStack Query |
| Lazy loading | ✅ Route-based code splitting |
| PWA caching | ✅ vite-plugin-pwa |
| Database indexes | ✅ All common queries indexed |
| Rate limiting | ✅ Prevents abuse |

---

## Known Limitations

1. **Not deployed:** Requires manual deployment to hosting providers — PUBLIC DEPLOYMENT: NOT YET DEPLOYED
2. **Supabase project:** Must be created manually; migrations must be run manually
3. **AI writing feedback:** Requires `ANTHROPIC_API_KEY` to be set on the backend (optional)
4. **Rate limiting:** In-process (not distributed); adequate for single-instance deployment
5. **Docker build:** Not verified — Docker is not available on the build machine
6. **Desktop app:** Remains in the repository but is not part of the web MVP

---

## Manual Actions Required

1. **Create a Supabase project** at [supabase.com](https://supabase.com)
2. **Run database migrations** (001-011) in the Supabase SQL Editor
3. **Seed vocabulary data** using the seed scripts or SQL
4. **Set backend environment variables** (`.env`):
   - `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
   - `JWT_SECRET`, `CORS_ORIGINS`, `ENVIRONMENT`
5. **Set frontend environment variables** (`web/.env.local`):
   - `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
6. **Deploy the backend** to a Docker-compatible host
7. **Deploy the frontend** to a static host (Cloudflare Pages recommended)
8. **Configure CORS** on the backend to match the frontend URL
9. **Configure Supabase Auth** redirect URLs
10. **Verify health endpoint:** `GET /api/v1/health` → 200
11. **Run the end-to-end smoke test** (see deployment guide)

---

## Future Improvements

- Desktop integration (not in scope)
- Offline mode with sync (not in scope)
- Mobile native app (not in scope)
- Advanced analytics
- Recommendation engine
- Distributed rate limiting (Redis)
- WebSocket real-time updates
- Multi-language content
- Voice recognition for speaking practice

---

## Summary

The EnglishCoach Pro Web MVP has been architected and implemented with:
- A complete FastAPI backend with 8 domain routers covering all application features
- A typed API client layer in the frontend that replaces all direct Supabase CRUD
- Supabase Auth for authentication with JWT validation on the backend
- Row Level Security on all user-owned database tables
- Security infrastructure (CORS, rate limiting, security headers, structured logging)
- Docker configuration for backend and frontend

---

## Verified Results (2026-08-31)

| Check | Result |
|-------|--------|
| Backend tests | ✅ 308 passed, 0 failed |
| Frontend tests | ✅ 6 passed, 0 failed |
| Frontend lint | ✅ 0 errors, 4 warnings (non-blocking) |
| TypeScript check | ✅ 0 errors |
| Production build | ✅ Build succeeded (3203 modules) |
| Docker build | ⚠️ NOT VERIFIED (Docker not available) |
| Database migrations | ✅ 11 migrations verified (tables, RLS, indexes, FKs, constraints) |
| Security audit | ✅ No secrets in repo; JWT, CORS, CSP, HSTS, rate limiting verified |
| Frontend Supabase CRUD | ✅ Zero direct CRUD operations (auth-only) |
| CI/CD workflows | ✅ 4 workflows verified (ci, deploy-frontend, deploy-backend, build) |
| Public deployment | ⚠️ NOT YET DEPLOYED (requires external account configuration) |
- GitHub Actions CI/CD pipelines
- Comprehensive documentation (architecture, deployment, troubleshooting)
- Backend and frontend tests

The application is ready for deployment pending manual infrastructure setup (Supabase project, hosting accounts, and environment variable configuration).
