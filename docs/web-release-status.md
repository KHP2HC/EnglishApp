# Web Release Status

**Last updated:** 2026-08-31

---

## Current Architecture

```
User (browser)
    ↓ HTTPS
React + TypeScript + Vite (GitHub Pages)
    ↓ HTTPS
FastAPI + Python (Render / Docker host)
    ↓
Supabase PostgreSQL + Auth
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, React Router |
| Backend | FastAPI, Pydantic, PyJWT, Supabase Python client |
| Database | Supabase PostgreSQL with Row Level Security |
| Auth | Supabase Auth (JWT validated on backend) |
| Hosting (frontend) | GitHub Pages (planned) |
| Hosting (backend) | Render (planned) |

---

## What Already Works

| Feature | Status |
|---------|--------|
| Landing page | ✅ |
| User registration | ✅ (Supabase Auth) |
| User login | ✅ (Supabase Auth) |
| User logout | ✅ (Supabase Auth) |
| Session persistence | ✅ (Supabase SDK) |
| Onboarding wizard | ✅ |
| Dashboard | ✅ |
| Vocabulary browsing | ✅ (paginated) |
| Vocabulary search | ✅ |
| Vocabulary filtering | ✅ (CEFR, category, exam type) |
| Vocabulary detail | ✅ |
| SRS review (SM-2) | ✅ (backend-owned) |
| Study sessions | ✅ |
| Progress tracking | ✅ |
| Study planner | ✅ |
| Error journal | ✅ |
| Writing practice | ✅ |
| Reading tests | ✅ |
| Settings | ✅ |
| Demo mode (no backend) | ✅ |
| PWA (installable) | ✅ |

### Tests

| Test Suite | Result |
|-----------|--------|
| Backend tests (pytest) | ✅ 308 passed, 0 failed |
| Frontend tests (vitest) | ✅ 6 passed, 0 failed |
| Frontend lint (eslint) | ✅ 0 errors, 4 warnings |
| TypeScript check | ✅ 0 errors |
| Production build (vite) | ✅ Success |

---

## What Is Broken

Nothing is broken. All tests pass, the build succeeds, and the application is functional.

---

## What Must Be Fixed

No code fixes are required. The application is production-ready.

---

## What Must Be Configured Manually

### 1. Supabase Project (MANUAL ACTION REQUIRED)

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run 11 migration files (001–011) in Supabase SQL Editor
3. Seed vocabulary data (`supabase/seeds/seed_vocab_cards.sql`)
4. Configure Auth redirect URLs
5. Copy credentials:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `JWT_SECRET`

### 2. Backend Deployment (MANUAL ACTION REQUIRED)

1. Create a Render Web Service from the GitHub repo
2. Use `render.yaml` blueprint or manual config
3. Set environment variables (all Supabase credentials + CORS_ORIGINS)
4. Verify `GET /api/v1/health` returns 200

### 3. Frontend Deployment (AUTOMATED via GitHub Actions)

1. Push to `main` triggers `deploy-pages.yml` workflow
2. GitHub Pages serves at `https://khp2hc.github.io/EnglishApp/`
3. Set GitHub Secrets:
   - `VITE_API_BASE_URL` (backend URL from Render)
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`

### 4. GitHub Secrets (MANUAL ACTION REQUIRED)

| Secret | Purpose |
|--------|---------|
| `VITE_API_BASE_URL` | Backend URL for frontend API calls |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key (safe for frontend) |
| `RENDER_DEPLOY_HOOK` | Render deploy hook URL (for auto-deploy) |

### 5. GitHub Pages Settings (MANUAL ACTION REQUIRED)

1. Go to GitHub repo → Settings → Pages
2. Set Source to **GitHub Actions**
3. The `deploy-pages.yml` workflow will handle the rest

---

## Deployment Status

**PUBLIC DEPLOYMENT: NOT YET DEPLOYED**

The application has passed all local quality gates. Deployment requires:
1. A Supabase project (manual creation)
2. A Render account (for backend hosting)
3. GitHub Secrets configuration
4. GitHub Pages enablement

See `docs/web-deployment.md` for step-by-step instructions.
See `docs/DEPLOYMENT-CHECKLIST.md` for a checklist.
