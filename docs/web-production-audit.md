# Web Production Audit

**Date:** 2026-08-31  
**Auditor:** Automated

---

## 1. Current Architecture

| Layer | Technology | Status |
|-------|-----------|--------|
| Frontend | React 18 + TypeScript + Vite + Tailwind | ✅ Working (demo mode) |
| Backend API | FastAPI | ⚠️ Minimal endpoints only |
| Database (Web) | Supabase PostgreSQL | ✅ Migrations exist, not connected to backend |
| Database (Desktop) | SQLite | ✅ Working (desktop only) |
| Auth | Supabase Auth | ⚠️ Frontend uses Supabase directly; backend JWT validation exists but unused |

### Architecture Flow (Current — BROKEN)
```
React → Supabase directly (bypassing FastAPI)
React → FastAPI (only for /health, /vocab/rate, /reading/*)
```

### Architecture Flow (Target)
```
React → FastAPI → Supabase PostgreSQL
React → Supabase Auth (auth only)
```

---

## 2. Current Features

### Frontend Pages (all exist)
- ✅ Landing page
- ✅ Auth (signup/signin via Supabase Auth)
- ✅ Onboarding wizard
- ✅ Dashboard (streaks, XP, daily plan, word of day)
- ✅ Vocabulary (SRS flashcards with SM-2)
- ✅ Grammar (placeholder)
- ✅ Listening (placeholder)
- ✅ Reading (reading tests)
- ✅ Writing (AI feedback via Supabase Functions)
- ✅ Speaking (placeholder)
- ✅ Mock Test (placeholder)
- ✅ Progress (heatmap, charts, error journal)
- ✅ Planner (weekly plan generation)
- ✅ Settings (profile, theme, language)

### Backend Endpoints (current)
- ✅ `GET /api/v1/health` — liveness check
- ✅ `POST /api/v1/vocab/rate` — SRS rate card (auth required)
- ✅ `GET /api/v1/reading/tests` — list reading tests
- ✅ `GET /api/v1/reading/test/{id}` — get reading test
- ✅ `POST /api/v1/reading/test/{id}/grade` — grade reading test
- ✅ Legacy endpoints (no auth, backward compat)

### Missing Backend Endpoints
- ❌ `GET /api/v1/vocabulary` — list/search/filter vocabulary
- ❌ `GET /api/v1/vocabulary/{id}` — vocabulary detail
- ❌ `GET /api/v1/reviews/due` — get due SRS cards
- ❌ `POST /api/v1/reviews/start` — start new card progress
- ❌ `POST /api/v1/reviews/rate` — rate card (exists as /vocab/rate)
- ❌ `GET /api/v1/study-sessions` — list sessions
- ❌ `POST /api/v1/study-sessions` — start session
- ❌ `PATCH /api/v1/study-sessions/{id}` — end session
- ❌ `GET /api/v1/progress` — progress stats
- ❌ `GET /api/v1/progress/activity` — daily activity
- ❌ `GET /api/v1/planner` — get study plan
- ❌ `POST /api/v1/planner` — generate plan
- ❌ `GET /api/v1/errors` — error journal
- ❌ `POST /api/v1/errors` — create error
- ❌ `GET /api/v1/writing` — list submissions
- ❌ `POST /api/v1/writing` — submit essay
- ❌ `GET /api/v1/profile` — get/update profile

---

## 3. Database State

### Supabase Migrations (11 files, well-structured)
| File | Table | RLS | Status |
|------|-------|-----|--------|
| 001_extensions.sql | pgcrypto, citext | N/A | ✅ |
| 002_profiles.sql | profiles | ✅ auth.uid() = id | ✅ |
| 003_vocab_cards.sql | vocab_cards | ✅ public read | ✅ |
| 004_vocab_progress.sql | vocab_progress | ✅ auth.uid() = user_id | ✅ |
| 005_study_sessions.sql | study_sessions | ✅ auth.uid() = user_id | ✅ |
| 006_error_journal.sql | error_journal | ✅ auth.uid() = user_id | ✅ |
| 007_study_plans.sql | study_plans | ✅ auth.uid() = user_id | ✅ |
| 008_content_cache.sql | content_cache | ✅ no user access | ✅ |
| 009_writing_submissions.sql | writing_submissions | ✅ auth.uid() = user_id | ✅ |
| 010_triggers.sql | updated_at + auto-profile | N/A | ✅ |
| 011_migration_id_map.sql | migration_id_map | N/A | ✅ |

### Schema Issues
- Backend uses SQLite models (`data/models.py`) with Integer PKs
- Supabase uses UUID PKs
- Backend `api.py` queries SQLite models, not Supabase
- **Backend must be updated to use Supabase PostgreSQL or a Supabase client**

---

## 4. Authentication State

- ✅ Frontend uses Supabase Auth (signup, signin, signout, session management)
- ✅ Backend has JWT validation infrastructure (`core/security.py`)
- ✅ Backend has Bearer token extraction
- ✅ Backend has role-based authorization (user/admin)
- ⚠️ Backend JWT_SECRET must be set to Supabase JWT secret
- ⚠️ Frontend sends JWT to backend only if API client is configured

---

## 5. API State

- Backend has security infrastructure (CORS, rate limiting, security headers, logging)
- Backend has only 4 functional endpoints (health, vocab/rate, reading tests)
- Frontend bypasses backend entirely for most operations
- Frontend does direct Supabase CRUD for: profiles, vocab_progress, study_sessions, error_journal, study_plans, writing_submissions

---

## 6. Frontend State

- ✅ React Router with protected routes
- ✅ Zustand stores (auth, session, settings)
- ✅ TanStack Query for data fetching
- ✅ Tailwind CSS with dark theme
- ✅ PWA support (vite-plugin-pwa)
- ✅ i18n setup (i18next)
- ⚠️ Direct Supabase calls in hooks (useVocab, useProgress, useStudyPlan)
- ⚠️ Direct Supabase calls in pages (Vocabulary, Dashboard, Settings, Onboarding, Writing)
- ❌ No typed API client layer

---

## 7. Deployment State

- ✅ Dockerfile exists (Python 3.12-slim, uvicorn)
- ✅ docker-compose.yml exists (backend + frontend)
- ⚠️ No GitHub Actions CI/CD
- ⚠️ No frontend Dockerfile
- ❌ Not deployed

---

## 8. Security Risks

| Risk | Severity | Status |
|------|----------|--------|
| Frontend direct DB access | HIGH | Must fix |
| Backend uses SQLite not Supabase | HIGH | Must fix |
| No user isolation in backend | HIGH | Must fix |
| Service role key exposure | LOW | Not in frontend |
| CORS configuration | LOW | Configurable |
| Rate limiting | LOW | Implemented |
| Security headers | LOW | Implemented |

---

## 9. Recommended Implementation Order

1. **Backend: Create Supabase client module** — Replace SQLite with Supabase service client
2. **Backend: Create domain routers** — vocabulary, reviews, sessions, progress, planner, errors, writing, profile
3. **Backend: Update api.py** — Mount all routers
4. **Frontend: Create API client layer** — `src/api/` with typed clients
5. **Frontend: Migrate hooks** — Replace Supabase calls with API client
6. **Frontend: Migrate pages** — Replace direct Supabase calls
7. **Environment: Create .env.example** — Frontend and backend
8. **Docker: Update configs** — Add frontend Dockerfile, fix compose
9. **CI/CD: GitHub Actions** — Test, lint, build, deploy
10. **Tests: Backend + Frontend** — Auth, SRS, vocabulary, sessions, progress
11. **Documentation** — Architecture, deployment, troubleshooting, final report
