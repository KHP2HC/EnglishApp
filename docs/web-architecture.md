# Web Architecture

## Overview

EnglishCoach Pro is a web application for learning English, built with a React + TypeScript frontend, a FastAPI backend, and Supabase PostgreSQL database with Supabase Auth.

```
                     INTERNET
                        │
                        ▼
              ┌──────────────────┐
              │ React + Vite     │
              │ TypeScript       │
              │ Tailwind CSS    │
              └────────┬─────────┘
                       │ HTTPS
                       │ JWT (Bearer)
                       ▼
              ┌──────────────────┐
              │ FastAPI          │
              │ REST API         │
              │ Business Logic   │
              │ Validation       │
              │ Security         │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Supabase         │
              │ PostgreSQL       │
              │ Supabase Auth    │
              └──────────────────┘
```

## Layers

### Frontend (React + TypeScript + Vite)

- **Routing:** React Router v6 with protected routes
- **State:** Zustand stores (auth, session, settings)
- **Data fetching:** TanStack Query (React Query)
- **API client:** `src/api/` — typed HTTP clients that attach JWT and handle errors
- **Auth:** Supabase Auth (signup, signin, signout, session management)
- **Styling:** Tailwind CSS with dark theme
- **PWA:** vite-plugin-pwa for offline vocabulary

**Key rule:** The frontend NEVER does direct CRUD against application tables. All data access goes through the FastAPI backend via the API client layer. The only direct Supabase calls are for auth operations.

### Backend (FastAPI + Python)

- **API:** FastAPI with Pydantic validation
- **Auth:** JWT validation (Supabase-issued tokens)
- **Security:** CORS, rate limiting, security headers, structured logging
- **Database:** Supabase PostgreSQL via service-role client
- **SRS:** SM-2 algorithm (backend owns all state changes)

**Routers:**

| Router | Prefix | Auth | Description |
|--------|--------|------|-------------|
| profile | `/api/v1/profile` | Required | User profile CRUD |
| vocabulary | `/api/v1/vocabulary` | Public | List, search, filter, detail |
| reviews | `/api/v1/reviews` | Required | SRS due cards, start, rate |
| study-sessions | `/api/v1/study-sessions` | Required | Session lifecycle |
| progress | `/api/v1/progress` | Required | Stats, activity heatmap |
| planner | `/api/v1/planner` | Required | Study plan generation |
| errors | `/api/v1/errors` | Required | Error journal CRUD |
| writing | `/api/v1/writing` | Required | Writing submissions + AI feedback |
| health | `/api/v1/health` | Public | Liveness check |
| reading | `/api/v1/reading/*` | Public | Reading tests |

### Database (Supabase PostgreSQL)

**Tables:**

| Table | PK | RLS | Description |
|-------|-----|-----|-------------|
| profiles | UUID (auth.users.id) | auth.uid() = id | User profile |
| vocab_cards | UUID | Public read | Global vocabulary |
| vocab_progress | UUID | auth.uid() = user_id | SRS state per user |
| study_sessions | UUID | auth.uid() = user_id | Study session history |
| error_journal | UUID | auth.uid() = user_id | Error tracking |
| study_plans | UUID | auth.uid() = user_id | Weekly plans |
| content_cache | UUID | No user access | External content cache |
| writing_submissions | UUID | auth.uid() = user_id | Essay submissions |

### Authentication Flow

```
1. User signs up/in via Supabase Auth (frontend)
2. Supabase returns JWT access token
3. Frontend stores session (Supabase SDK)
4. Frontend sends JWT in Authorization: Bearer header to FastAPI
5. FastAPI validates JWT signature using Supabase JWT secret
6. FastAPI extracts user identity (sub, email, role)
7. FastAPI scopes all database queries to authenticated user_id
```

### Security Architecture

- **JWT validation:** Backend validates every Supabase JWT using the project's JWT secret
- **User isolation:** All user-owned data is scoped by `user_id` derived from JWT
- **RLS:** Supabase Row Level Security provides defense-in-depth
- **CORS:** Configurable origins, never `*` in production
- **Rate limiting:** Per-IP sliding window
- **Security headers:** HSTS, CSP, X-Frame-Options, etc.
- **Error handling:** Never exposes stack traces, SQL errors, or secrets
- **Logging:** Structured, never logs tokens or credentials

### SRS (Spaced Repetition)

The backend owns all SRS state changes using the SM-2 algorithm:

1. Frontend requests due cards: `GET /api/v1/reviews/due`
2. User rates a card: `POST /api/v1/reviews/rate`
3. Backend applies SM-2 update and persists to database
4. Backend returns updated state + XP earned
5. Frontend displays result

The frontend NEVER independently calculates SRS state when the API is available.

### File Structure

```
EnglishApp/
├── api.py                    # FastAPI app entry point
├── routers/                  # Domain API routers
│   ├── profile.py
│   ├── vocabulary.py
│   ├── reviews.py
│   ├── study_sessions.py
│   ├── progress.py
│   ├── planner.py
│   ├── errors.py
│   └── writing.py
├── core/                     # Shared infrastructure
│   ├── config.py             # Environment configuration
│   ├── security.py           # JWT validation
│   ├── supabase_client.py    # Supabase service client
│   ├── web_schemas.py        # Pydantic models
│   ├── srs_engine.py         # SM-2 algorithm
│   ├── rate_limit.py         # Rate limiting
│   ├── errors.py             # Error handling
│   ├── security_headers.py   # Security headers
│   └── logging_config.py    # Structured logging
├── web/                      # React frontend
│   └── src/
│       ├── api/              # Typed API clients
│       ├── components/       # React components
│       ├── hooks/            # React Query hooks
│       ├── pages/            # Route pages
│       ├── stores/           # Zustand stores
│       └── lib/              # Utilities
├── supabase/                 # Database migrations
│   └── migrations/
├── tests/                    # Backend tests
├── Dockerfile                # Backend Docker
├── docker-compose.yml        # Full-stack Docker
└── .github/workflows/        # CI/CD
```
