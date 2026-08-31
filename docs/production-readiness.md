# Production Readiness — EnglishCoach Pro

## Production Readiness Score: 35/100

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Authentication | 0/10 | 15% | 0 |
| API completeness | 2/10 | 15% | 3 |
| Database integrity | 4/10 | 15% | 6 |
| Security | 3/10 | 15% | 4.5 |
| Testing | 5/10 | 10% | 5 |
| CI/CD | 6/10 | 10% | 6 |
| Deployment config | 5/10 | 10% | 5 |
| Monitoring | 0/10 | 5% | 0 |
| Documentation | 7/10 | 5% | 3.5 |
| **Total** | | **100%** | **33/100** |

---

## 1. What Is Ready

| Item | Status | Notes |
|------|--------|-------|
| Desktop app | ✅ Ready | Works offline, 35 tests passing |
| Web frontend | ✅ Ready (demo mode) | Works without Supabase, full UI |
| FastAPI health endpoint | ✅ Ready | `GET /api/v1/health` |
| CORS configuration | ✅ Ready | Configurable via `CORS_ORIGINS` |
| Dockerfile | ✅ Ready | Fixed CMD, builds correctly |
| docker-compose.yml | ✅ Ready | Backend + frontend services |
| GitHub Actions CI | ✅ Ready | Backend tests + frontend lint/build |
| GitHub Actions Release | ✅ Ready | EXE build on version tags |
| `.gitignore` | ✅ Ready | Comprehensive |
| `.env.example` | ✅ Ready | All variables documented |
| LICENSE | ✅ Ready | MIT |
| CONTRIBUTING.md | ✅ Ready | Full guidelines |
| README.md | ✅ Ready | Full documentation |
| Supabase migrations | ✅ Ready | Schema + seed data |
| Supabase RLS | ✅ Ready | Row-level security on all user tables |
| Offline support (web) | ✅ Ready | IndexedDB cache, PWA |

---

## 2. What Is Missing

### Critical (Blocks Production)

| Item | Impact | Description |
|------|--------|-------------|
| **API authentication** | Critical | No auth on any FastAPI endpoint. Anyone can access/modify data. |
| **API completeness** | Critical | Only 5 endpoints exist. No user, vocab, session, or progress endpoints. |
| **Centralized business logic** | Critical | Logic duplicated across Python and TypeScript with diverging behavior. |
| **Data synchronization** | Critical | Desktop and web data are completely separate. No sync. |
| **Shared user accounts** | Critical | Desktop has no auth. Web uses Supabase. Cannot share accounts. |

### High (Should Fix Before Production)

| Item | Impact | Description |
|------|--------|-------------|
| **Schema unification** | High | SQLite and Supabase have different schemas, ID types, column names. |
| **Direct DB access from frontend** | High | React accesses Supabase directly, bypassing backend. Security risk. |
| **No rate limiting** | High | API can be abused without limits. |
| **No input validation on API** | High | Only basic Pydantic models. No business rule validation. |
| **No error tracking** | High | No Sentry or similar. Errors are silent in production. |
| **No logging** | High | No structured logging. Cannot debug production issues. |
| **writing_submissions RLS** | High | RLS not enabled on `writing_submissions` table. |

### Medium (Should Fix for Scale)

| Item | Impact | Description |
|------|--------|-------------|
| **No database indexes** | Medium | Missing indexes on `user_id`, `next_review`, `updated_at`. |
| **No API documentation** | Medium | No OpenAPI/Swagger UI exposed. |
| **No integration tests** | Medium | Only unit tests. No end-to-end tests. |
| **No load testing** | Medium | Unknown how system performs under load. |
| **No backup strategy** | Medium | No automated database backups. |
| **No custom domain** | Medium | No domain configured for API or frontend. |
| **Supabase free tier limits** | Medium | May hit rate limits, database pauses. |

### Low (Nice to Have)

| Item | Impact | Description |
|------|--------|-------------|
| **No monitoring dashboard** | Low | No Grafana/Datadog. |
| **No CDN** | Low | Static assets served directly. |
| **No caching layer** | Low | No Redis. Every request hits database. |
| **No A/B testing** | Low | No feature flags. |

---

## 3. Required Environment Variables

### Backend (FastAPI)

| Variable | Required | Description |
|----------|----------|-------------|
| `API_PORT` | No | Default: 8000 |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_ANON_KEY` | Yes | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase service role key (server only) |
| `ANTHROPIC_API_KEY` | Yes | Claude API key for writing feedback |
| `DATABASE_URL` | Future | PostgreSQL connection string (when migrating from SQLite) |

### Frontend (Web)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_SUPABASE_URL` | Yes | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Yes | Supabase anon key |
| `VITE_API_BASE_URL` | Future | FastAPI base URL (when frontend uses API) |

### Desktop

| Variable | Required | Description |
|----------|----------|-------------|
| `ENGLISHCOACH_MACHINE_ID` | No | Machine ID override for API key encryption |

---

## 4. Required Secrets (GitHub Actions)

| Secret | Purpose |
|--------|---------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key |
| `ANTHROPIC_API_KEY` | Claude API key |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Pages deployment |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID |

---

## 5. Required CI/CD Changes

| Change | Description |
|--------|-------------|
| Add API integration tests | Test API endpoints with real database |
| Add Supabase migration CI | Run migrations on push to main |
| Add frontend deploy job | Deploy to Cloudflare Pages on merge to main |
| Add backend deploy job | Deploy Docker container on merge to main |
| Add security scanning | Run `safety` (Python) and `npm audit` (Node) |
| Add linting to CI | Run Ruff (Python) and ESLint (TypeScript) |
| Add type checking | Run mypy (Python) and tsc (TypeScript) |

---

## 6. Deployment Architecture

### Current (Ready)

```
GitHub
  ↓
GitHub Actions
  ├── ci.yml → Backend tests + Frontend lint/build (on PR)
  └── build.yml → EXE release + docs (on tag)
```

### Target

```
GitHub
  ↓
GitHub Actions
  ├── ci.yml → Tests + lint + typecheck (on PR)
  ├── deploy-staging.yml → Deploy to staging (on merge to main)
  ├── deploy-production.yml → Deploy to production (on tag)
  └── build.yml → EXE release + docs (on tag)
  
Deployment targets:
  ├── Frontend → Cloudflare Pages (staging + production)
  ├── Backend → Container platform (Railway/Render/Fly.io)
  ├── Database → Supabase (managed PostgreSQL)
  └── Desktop → GitHub Releases (EXE)
```

---

## 7. Security Review

### CRITICAL

| Finding | Description |
|---------|-------------|
| No API authentication | All FastAPI endpoints are public. Anyone can rate cards, fetch tests, or grade. |
| Direct Supabase access from frontend | React uses anon key directly. If key leaks, all user data is accessible. |
| No rate limiting | API can be called unlimited times. DoS risk. |

### HIGH

| Finding | Description |
|---------|-------------|
| CORS allows credentials | `allow_credentials=True` with specific origins. If origins are misconfigured, credentials leak. |
| No input sanitization | User input not sanitized beyond Pydantic types. XSS/injection risk. |
| Anthropic API key in edge function | Key is server-side (good), but edge function has `Access-Control-Allow-Origin: *`. |
| No HTTPS enforcement | API does not enforce HTTPS. Tokens can be intercepted. |
| `writing_submissions` has no RLS | Any authenticated user can read any submission. |

### MEDIUM

| Finding | Description |
|---------|-------------|
| Supabase anon key in frontend bundle | Key is public by design, but enables direct table access. |
| No CSRF protection | API has no CSRF tokens. |
| No security headers | No HSTS, X-Frame-Options, etc. |
| Desktop API key encryption | Uses machine ID as encryption key. Weak if machine ID is predictable. |

### LOW

| Finding | Description |
|---------|-------------|
| No audit log | No record of who did what. |
| No IP allowlisting | API accessible from any IP. |
| No WAF | No web application firewall. |

---

## 8. Performance Review

| Finding | Severity | Description |
|---------|----------|-------------|
| N+1 queries in `useProgressStats` | Medium | 3 separate Supabase queries that could be batched |
| No pagination on vocab cards | Medium | `useDueCards` fetches up to 50 + 20 cards without pagination |
| No database indexes | Medium | Missing indexes on `user_id`, `next_review`, `updated_at` |
| Large frontend bundle | Low | Many Radix UI components, no tree-shaking analysis |
| No API response caching | Low | Every request hits database |
| `loadVocabData` fetches entire JSON | Low | Loads full vocab file into memory |
| No connection pooling | Low | SQLite uses single connection. Supabase uses pool. |
| Content fetcher has no caching headers | Low | Fetched articles not cached at HTTP level |

---

## 9. Highest-Priority Actions

| Priority | Action | Phase |
|----------|--------|-------|
| 1 | Add JWT authentication to FastAPI | Phase 1 |
| 2 | Add missing API endpoints (user, vocab, sessions, progress) | Phase 2 |
| 3 | Move web frontend from direct Supabase to API | Phase 2 |
| 4 | Unify database schema (UUIDs, column names, constraints) | Phase 4 |
| 5 | Implement desktop sync engine | Phase 5 |
| 6 | Add rate limiting and input validation | Phase 1 |
| 7 | Enable RLS on `writing_submissions` | Phase 1 |
| 8 | Add database indexes | Phase 4 |
| 9 | Add structured logging and error tracking | Phase 7 |
| 10 | Set up production deployment pipeline | Phase 6 |
