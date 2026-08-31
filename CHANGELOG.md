# Changelog

All notable changes to EnglishCoach Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-08-31

### Added — Web MVP
- Complete FastAPI backend with 8 domain routers (profile, vocabulary, reviews, study-sessions, progress, planner, errors, writing)
- Typed API client layer in frontend (`src/api/`) with JWT attachment and error handling
- Supabase PostgreSQL client module for backend database access
- Pydantic web schemas matching the canonical Supabase schema
- Backend SRS engine as the canonical source of truth for spaced repetition
- User isolation: all backend queries scoped by JWT-derived user_id
- Frontend migrated from direct Supabase CRUD to API client layer
- Frontend Dockerfile with Nginx for static hosting
- GitHub Actions CI/CD (ci.yml, deploy-frontend.yml, deploy-backend.yml)
- Backend tests (test_web_api.py) covering auth, SRS, validation, security
- Frontend tests (API client tests with Vitest)
- Comprehensive documentation: web-production-audit.md, web-architecture.md, web-deployment.md, web-troubleshooting.md, web-mvp-final-report.md
- Environment variable templates (.env.example, web/.env.example)
- Docker health check for backend
- Non-root user in backend Dockerfile

### Changed
- Backend now uses Supabase PostgreSQL instead of SQLite for web API
- Frontend hooks (useVocab, useProgress, useStudyPlan) use API client instead of direct Supabase calls
- Frontend pages (Vocabulary, Settings, Onboarding, Writing, MockTest) use API client
- Auth store uses API client for profile refresh with Supabase fallback
- Docker Compose updated with correct build args and health check
- README updated with web-first architecture and deployment instructions

### Security
- All user-owned data protected by RLS (auth.uid() = user_id)
- JWT validation on all protected endpoints
- Service-role key never exposed to frontend
- CORS configurable, never wildcard in production
- Rate limiting, security headers, structured logging
- Error responses never expose stack traces or internals

## [Unreleased]

### Added
- Grammar screen with 6 built-in lessons and MCQ exercises
- Mock test mode with TOEIC, IELTS, TOEFL, and VSTEP simulations
- System tray integration with daily streak reminders and word-of-the-day notifications
- Matplotlib charts on progress screen (bar, radar, line)
- Error journal tab on progress screen with weak-area review
- Streak banner component with 7-day heatmap
- Word card component with flip animation
- GitHub Actions CI/CD pipeline (test + build EXE + release)
- MkDocs Material documentation site
- Pre-commit hooks with Ruff
- i18n hook for Vietnamese UI labels
- Settings screen with Claude API key management
- Dashboard upgraded with streak banner, daily goal ring, quick stats, word of the day

### Changed
- Sidebar now includes grammar and mock test navigation
- App enforces minimum 1280×720 window size
- Dashboard pulls word of the day from database when available

### Fixed
- Navigation routing for grammar and mock test screens
