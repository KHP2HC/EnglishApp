# GitHub Migration Report — EnglishCoach Pro

## 1. Current Architecture

EnglishCoach Pro is a dual-interface English exam preparation platform:

- **Desktop App**: CustomTkinter-based GUI application for Windows, providing vocabulary flashcards (SRS), grammar lessons, reading tests, listening, writing (AI feedback), speaking (Whisper STT), mock tests, progress analytics, study planner, and system tray integration.
- **Web App**: React + TypeScript SPA (Vite) with Supabase backend, providing the same feature set in a browser-based interface.
- **API**: FastAPI backend serving REST endpoints for vocabulary SRS, reading tests, and static frontend hosting.

### Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                  Desktop App                     │
│  (CustomTkinter, Python)                         │
│  ┌─────────────────────────────────────────┐    │
│  │  main.py → app.py → ui/screens/*        │    │
│  │  core/* (SRS, AI tutor, planner, etc.)  │    │
│  │  data/* (SQLAlchemy + SQLite)            │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                  Web App                         │
│  (React + TypeScript + Vite)                     │
│  ┌─────────────────────────────────────────┐    │
│  │  web/src/* (pages, components, stores)  │    │
│  │  Supabase (auth, DB, edge functions)     │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│              FastAPI Backend                     │
│  api.py (vocabulary SRS, reading tests,         │
│         health check, static file serving)        │
│  SQLite database (data.db)                       │
└─────────────────────────────────────────────────┘
```

## 2. Frontend Technology

| Component | Technology |
|-----------|-----------|
| Framework | React 18 + TypeScript |
| Build tool | Vite 5 |
| Styling | Tailwind CSS 3 |
| State management | Zustand + TanStack Query |
| Routing | React Router 6 |
| Forms | React Hook Form + Zod |
| UI components | Radix UI + Lucide icons |
| PWA | vite-plugin-pwa |
| Backend | Supabase (auth, database, edge functions) |

## 3. Backend Technology

| Component | Technology |
|-----------|-----------|
| API framework | FastAPI |
| ASGI server | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (file-based) |
| Validation | Pydantic 2 |
| AI | Anthropic Claude API (claude-sonnet-4-6) |
| TTS | edge-tts |
| STT | openai-whisper |
| Charts | matplotlib |
| Scheduling | APScheduler |
| Desktop UI | CustomTkinter |
| Packaging | PyInstaller |

## 4. Database Technology

- **Desktop**: SQLite (file-based, `data.db`) via SQLAlchemy ORM
- **Web**: Supabase (PostgreSQL) with Row Level Security
- **Migrations**: 
  - Desktop: Auto-migration via `migrate_schema()` in `data/database.py`
  - Web: SQL migration files in `web/supabase/migrations/`

## 5. Existing Environment Variables

| Variable | Scope | Description |
|----------|-------|-------------|
| `API_PORT` | Backend | FastAPI port (default: 8000) |
| `CORS_ORIGINS` | Backend | Comma-separated allowed CORS origins |
| `ENGLISHCOACH_MACHINE_ID` | Desktop | Machine ID override for API key encryption |
| `VITE_SUPABASE_URL` | Frontend | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Frontend | Supabase anonymous key |
| `ANTHROPIC_API_KEY` | Supabase Edge Function | Claude API key (set via Supabase dashboard) |
| `SUPABASE_URL` | Supabase Edge Function | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase Edge Function | Supabase anonymous key |

## 6. Existing Secrets That Must NOT Be Committed

- **Anthropic Claude API key**: Stored encrypted on the user's machine (Fernet encryption with machine-specific key). Never in plaintext files.
- **Supabase URL and anon key**: Set via `web/.env.local` (gitignored).
- **Supabase service role key**: Set via Supabase dashboard secrets.
- **No `.env` files found** in the repository (only `.env.example` templates).

## 7. Existing Build Commands

### Desktop App
```bash
# Install dependencies
pip install -r requirements.txt

# Run desktop app
python main.py

# Build Windows EXE
pyinstaller --onefile --windowed --name EnglishCoachPro main.py
```

### Web Frontend
```bash
cd web
npm install
npm run dev      # Development
npm run build    # Production build
npm run preview  # Preview production build
```

### API Backend
```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Documentation
```bash
pip install mkdocs mkdocs-material
mkdocs serve --config-file docs/mkdocs.yml
```

## 8. Existing Test Commands

```bash
# Backend tests (35 tests across 10 test files)
python -m pytest tests/ -v

# Frontend lint
cd web && npm run lint
```

## 9. Existing Docker Configuration

- `Dockerfile`: Python 3.12-slim, installs requirements, runs `uvicorn api:app`
- `docker-compose.yml`: Two services — backend (FastAPI) and frontend (web)
- `.dockerignore`: Excludes `__pycache__`, `.venv`, `node_modules`, `.env`, `.git`

### Issues Fixed During Migration
- **Dockerfile CMD**: Changed from `web.api:app` (non-existent) to `api:app`
- **docker-compose frontend context**: Changed from `./web/frontend` (non-existent) to `./web`
- **Added healthcheck** to backend service
- **Added environment variables** to backend service

## 10. Existing Deployment Configuration

- **GitHub Actions** (`.github/workflows/`):
  - `ci.yml`: Backend tests + frontend lint/build on push/PR to main
  - `build.yml`: EXE build + release on version tags, docs build
- **Supabase**: Edge functions for AI feedback and keep-alive
- **Pre-commit hooks**: Ruff linting and formatting

## 11. Git Readiness

### Issues Found and Fixed
1. **CRITICAL**: Git remote URL contained an embedded GitHub token → **Fixed**: Removed token from remote URL
2. **`data.db` tracked in Git** → **Fixed**: Added to `.gitignore`, will be untracked
3. **`__pycache__`/`.pyc` files tracked** → **Fixed**: Added to `.gitignore`, will be untracked
4. **`vocab_crash.log` tracked** → **Fixed**: Added `*.log` to `.gitignore`
5. **No root `.gitignore`** → **Fixed**: Created comprehensive `.gitignore`
6. **No LICENSE** → **Fixed**: Created MIT License
7. **No `.env.example` at root** → **Fixed**: Created root `.env.example`

## 12. Files That Should Be Committed

- All Python source files (`*.py`)
- Web frontend source (`web/src/`, `web/*.json`, `web/*.ts`, `web/*.js`)
- Configuration files (`requirements.txt`, `Dockerfile`, `docker-compose.yml`, `.dockerignore`)
- Test files (`tests/*.py`)
- Documentation (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/`)
- CI/CD (`.github/workflows/`)
- Seed data (`data/seed/*.json`, `data/seed/*.py`)
- Supabase migrations (`web/supabase/`)
- `.gitignore`, `.env.example`, `LICENSE`
- `.pre-commit-config.yaml`

## 13. Files That Must Be Ignored

- `data.db` — SQLite database with user data
- `__pycache__/` and `*.pyc` — Python bytecode cache
- `*.log` — Log files
- `.env`, `.env.local` — Environment files with secrets
- `node_modules/` — Node dependencies
- `dist/`, `build/` — Build output
- `.venv/`, `venv/` — Virtual environments
- `.pytest_cache/`, `.ruff_cache/` — Cache directories
- `EnglishCoachPro.exe` — Built binary
- `.understand-anything/` — IDE/tool artifacts

## 14. Recommended GitHub Repository Structure

```
EnglishApp/
├── .github/
│   └── workflows/
│       ├── ci.yml          # Backend tests + frontend lint/build
│       └── build.yml        # EXE release + docs build
├── .gitignore
├── .dockerignore
├── .env.example
├── .pre-commit-config.yaml
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── main.py                 # Desktop app entry point
├── api.py                  # FastAPI backend
├── app.py                  # CustomTkinter root app
├── web_app.py              # Streamlit web app (legacy)
├── run_web.py              # Web launcher
├── run_web.bat             # Windows web launcher
├── generate_input.py       # Code analysis tool
├── EnglishCoachPro.spec    # PyInstaller spec
├── core/                   # Business logic
├── data/                   # Database, models, seed data
├── ui/                     # Desktop UI (screens, components)
├── web/                    # Web frontend (React + TypeScript)
├── tests/                  # Test suite
├── assets/                 # Fonts, icons, audio
└── docs/                   # MkDocs documentation
```

## 15. Recommended CI/CD Architecture

```
GitHub Push/PR
    │
    ├── ci.yml
    │   ├── backend-test (Python 3.12, pytest)
    │   └── frontend-build (Node 20, npm lint + build)
    │
    └── build.yml (on tag v*)
        ├── test (pytest)
        ├── build-windows (PyInstaller EXE → GitHub Release)
        └── build-docs (MkDocs)
```

## 16. Deployment Architecture

### Current
- **Desktop**: Windows EXE via PyInstaller, distributed via GitHub Releases
- **Web Frontend**: Vite build, deployable to Cloudflare Pages / Netlify / Vercel
- **Backend API**: Docker container, deployable to any container platform
- **Database (Web)**: Supabase (managed PostgreSQL)

### Recommended Production
```
GitHub
  ↓
GitHub Actions (CI)
  ↓
Frontend → Cloudflare Pages (Vite build → dist/)
  ↓
Backend → Container platform (Docker → FastAPI)
  ↓
Database → Supabase (managed PostgreSQL free tier)
```

## 17. GitHub Actions Secrets Required

| Secret | Purpose |
|--------|---------|
| `SUPABASE_URL` | Supabase project URL (for edge functions) |
| `SUPABASE_ANON_KEY` | Supabase anonymous key |
| `ANTHROPIC_API_KEY` | Claude API key for AI feedback |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Pages deployment (future) |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID (future) |

## 18. Known Limitations

- Desktop app is Windows-only (CustomTkinter + system tray)
- Whisper STT requires significant CPU resources
- SQLite is not suitable for multi-user production (desktop only)
- Web frontend requires Supabase for full functionality (has demo mode without it)
- No automated frontend deployment yet (manual build + deploy)

## 19. Remaining Manual Steps

1. **Revoke the exposed GitHub token** (was embedded in remote URL — now removed, but the old token should be revoked in GitHub settings)
2. **Set up GitHub repository topics** (english-learning, education, etc.)
3. **Configure GitHub Actions secrets** if deploying web frontend
4. **Set up Supabase project** for web frontend (if using web app)
5. **Configure Cloudflare Pages** for frontend deployment (optional)
