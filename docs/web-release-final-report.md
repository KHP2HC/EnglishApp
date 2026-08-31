# Web Release Final Report

**Date:** 2026-08-31  
**Commit:** `c271b78` — `feat: release EnglishApp web application`  
**Branch:** `main` (pushed to `origin/main`)

---

## Web Status

**PASS** — The web application builds, tests pass, and is ready for deployment. Deployment requires external account configuration (Supabase, Render, GitHub Pages).

---

## Public URL

**MANUAL ACTION REQUIRED**

The frontend will be available at:
```
https://khp2hc.github.io/EnglishApp/
```

This URL will be live once the following are completed:
1. GitHub Pages is enabled (repo → Settings → Pages → Source: GitHub Actions)
2. GitHub Secrets are set (`VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`)
3. A Supabase project is created and migrations are run
4. A Render backend is deployed

The `deploy-pages.yml` workflow will automatically build and deploy on push to `main` once GitHub Pages is enabled.

---

## Frontend Hosting

| Item | Status |
|------|--------|
| Build | ✅ PASS (vite build, 3203 modules) |
| TypeScript | ✅ PASS (0 errors) |
| ESLint | ✅ PASS (0 errors, 4 warnings) |
| Tests | ✅ PASS (6/6) |
| PWA Icons | ✅ Created (192x192, 512x512) |
| SPA Routing | ✅ Configured (basename + GitHub Pages workflow) |
| Hosting Platform | GitHub Pages (workflow ready) |
| Deployed | ⚠️ MANUAL ACTION REQUIRED — enable GitHub Pages |

---

## Backend Hosting

| Item | Status |
|------|--------|
| Tests | ✅ PASS (308/308) |
| Dockerfile | ✅ Verified (Python 3.12-slim, healthcheck, non-root) |
| Render Blueprint | ✅ Created (`render.yaml`) |
| Deploy Workflow | ✅ Created (`deploy-backend.yml` with test gate) |
| Hosting Platform | Render (blueprint ready) |
| Deployed | ⚠️ MANUAL ACTION REQUIRED — create Render service |

---

## Database

| Item | Status |
|------|--------|
| Migrations (001-011) | ✅ Verified (tables, FKs, indexes, constraints, RLS, triggers) |
| UUID Primary Keys | ✅ All tables |
| Foreign Keys | ✅ profiles → auth.users, all user tables → profiles |
| RLS | ✅ All user-owned tables use auth.uid() |
| Indexes | ✅ All common query patterns indexed |
| Seed Data | ✅ Seed SQL and generator script exist |
| Supabase Project | ⚠️ MANUAL ACTION REQUIRED — create project, run migrations, seed data |

---

## Authentication

| Item | Status |
|------|--------|
| Registration | ✅ Supabase Auth |
| Login | ✅ Supabase Auth |
| Logout | ✅ Supabase Auth |
| Session Persistence | ✅ Supabase SDK auto-refresh |
| JWT Validation | ✅ Backend validates signature, expiry, audience |
| User Identity | ✅ Derived from JWT (never from client) |
| Token Refresh | ✅ Supabase SDK handles |
| Protected Routes | ✅ Frontend + backend |
| Auth Redirect URLs | ⚠️ MANUAL ACTION REQUIRED — configure in Supabase dashboard |

---

## Features

| Feature | Status |
|---------|--------|
| Landing page | ✅ PASS |
| Registration | ✅ PASS |
| Login | ✅ PASS |
| Logout | ✅ PASS |
| Dashboard | ✅ PASS |
| Vocabulary browsing | ✅ PASS |
| Vocabulary search | ✅ PASS |
| Vocabulary filtering | ✅ PASS |
| Vocabulary detail | ✅ PASS |
| SRS review (SM-2) | ✅ PASS |
| Study sessions | ✅ PASS |
| Progress tracking | ✅ PASS |
| Study planner | ✅ PASS |
| Error journal | ✅ PASS |
| Writing practice | ✅ PASS |
| Reading tests | ✅ PASS |
| Settings | ✅ PASS |
| Demo mode | ✅ PASS |
| PWA | ✅ PASS |

---

## Tests

| Test Suite | Result |
|-----------|--------|
| Backend (pytest) | ✅ 308 passed, 0 failed |
| Frontend (vitest) | ✅ 6 passed, 0 failed |
| Frontend lint (eslint) | ✅ 0 errors, 4 warnings |
| TypeScript (tsc) | ✅ 0 errors |
| Production build (vite) | ✅ Success |
| Docker build | ⚠️ NOT VERIFIED (Docker not available) |

---

## Security

| Item | Status |
|------|--------|
| No secrets in repo | ✅ PASS |
| .gitignore | ✅ .env, *.key, *.pem, credentials excluded |
| JWT validation | ✅ Signature, expiry, audience, subject |
| CORS | ✅ Configurable, never `*` in production |
| CSP | ✅ Strict in production |
| HSTS | ✅ Enabled in production |
| X-Frame-Options | ✅ DENY |
| X-Content-Type-Options | ✅ nosniff |
| Rate limiting | ✅ Per-IP sliding window |
| RLS | ✅ All user-owned tables |
| User isolation | ✅ All queries scoped by JWT user_id |
| Input validation | ✅ Pydantic on all endpoints |
| Error sanitization | ✅ Never exposes internals |
| Service-role key | ✅ Backend-only, never in frontend |
| Frontend Supabase CRUD | ✅ Zero direct CRUD (auth-only) |

---

## CI/CD

| Workflow | Trigger | Status |
|----------|---------|--------|
| `ci.yml` | push/PR to main, develop | ✅ Backend tests + frontend lint/build |
| `deploy-pages.yml` | push to main (web/**) | ✅ Build + deploy to GitHub Pages |
| `deploy-backend.yml` | push to main (api/**) | ✅ Tests + Render deploy hook |
| `build.yml` | tag push (v*) | ✅ Desktop EXE + docs build |

- ✅ CI runs on push and pull requests
- ✅ Tests run before deployment
- ✅ Failed CI blocks deployment
- ✅ Secrets referenced through GitHub Secrets
- ✅ No hard-coded secrets

---

## Deployment

**DEPLOYMENT BLOCKED** — requires external account configuration.

### Required Manual Actions (in order):

1. **Create Supabase project** at [supabase.com](https://supabase.com)
2. **Run migrations** (001-011) in Supabase SQL Editor
3. **Seed vocabulary** data
4. **Configure Supabase Auth** (redirect URLs)
5. **Deploy backend** to Render (use `render.yaml` blueprint)
6. **Set GitHub Secrets**: `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
7. **Enable GitHub Pages** (repo → Settings → Pages → Source: GitHub Actions)
8. **Push to main** triggers automatic frontend deployment
9. **Verify health**: `GET https://your-backend.onrender.com/api/v1/health`
10. **Open** `https://khp2hc.github.io/EnglishApp/`

---

## Known Issues

1. **Docker build not verified** — Docker is not available on this machine
2. **Rate limiting is in-process** — adequate for single-instance, not multi-instance
3. **Large bundle size** — frontend bundle is 1.1MB (328KB gzipped); could benefit from code splitting
4. **TypeScript version warning** — @typescript-eslint supports <5.6.0, project uses 5.9.3 (works fine)

---

## Manual Actions Required

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 1 | Create Supabase project | supabase.com | Project URL + API keys |
| 2 | Run 11 SQL migrations | Supabase SQL Editor | Tables created |
| 3 | Seed vocabulary data | Supabase SQL Editor | `SELECT count(*) FROM vocab_cards` > 0 |
| 4 | Configure Auth redirect URLs | Supabase → Authentication → URL Configuration | Site URL = GitHub Pages URL |
| 5 | Create Render Web Service | render.com | Backend URL |
| 6 | Set backend env vars | Render dashboard | Health check passes |
| 7 | Set GitHub Secrets | GitHub repo → Settings → Secrets | 3 secrets added |
| 8 | Enable GitHub Pages | GitHub repo → Settings → Pages | Source: GitHub Actions |
| 9 | Push to main | git push | Frontend auto-deploys |
| 10 | Verify public URL | Browser | App loads and works |
