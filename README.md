# EnglishCoach Pro

**Open-source, non-profit English learning platform for exam preparation**

An AI-powered English exam preparation platform for learners preparing for TOEIC, IELTS, TOEFL, or VSTEP. It functions as a personal AI coach — not just a content library. Available as both a Windows desktop application and a web app.

## Features

| Feature | Description |
|---------|-------------|
| 🧠 SRS Vocabulary | SM-2 spaced repetition with 50,000+ words |
| 📐 Grammar | Interactive lessons with exercises and error tracking |
| 📖 Reading | IELTS-style academic reading tests |
| 👂 Listening | Audio comprehension exercises |
| ✍️ Writing | AI-powered essay evaluation (Claude API) |
| 🗣️ Speaking | Whisper STT + pronunciation scoring |
| 🧪 Mock Tests | Full exam simulation with timer and results |
| 📊 Progress | Heatmaps, charts, and error journal |
| 🗓️ Planner | AI-generated weekly plans from your deadline |
| 🔥 Streaks | Gamified daily study habit builder |
| 📌 System Tray | Daily reminders and word-of-the-day notifications |
| 🌐 Bilingual | English / Vietnamese UI (i18n) |

## Architecture

EnglishCoach Pro has two interfaces sharing the same core logic:

- **Desktop App**: CustomTkinter GUI for Windows with full offline capability
- **Web App**: React + TypeScript SPA with Supabase backend
- **API**: FastAPI backend serving REST endpoints and static files

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Desktop UI | CustomTkinter |
| Web Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend API | FastAPI, Uvicorn |
| Database (Desktop) | SQLite + SQLAlchemy |
| Database (Web) | Supabase (PostgreSQL) |
| AI | Anthropic Claude API (claude-sonnet-4-6) |
| TTS | edge-tts |
| STT | openai-whisper |
| Charts | matplotlib (desktop), Recharts (web) |
| Scheduling | APScheduler |
| Packaging | PyInstaller |

## Requirements

- **Python**: 3.11+ (tested on 3.12)
- **Node.js**: 18+ (for web frontend)
- **npm**: 9+ (for web frontend)
- **OS**: Windows 10/11 (desktop app), any (web app)

## Local Development

### Desktop App

```bash
# Clone the repository
git clone https://github.com/KHP2HC/EnglishApp.git
cd EnglishApp

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the desktop app
python main.py
```

### API Backend

```bash
# Activate virtual environment (see above)
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Health check: `GET http://localhost:8000/api/v1/health`

### Web Frontend

```bash
cd web
npm install
cp .env.example .env.local  # Optional: fill in Supabase credentials
npm run dev
```

The web app runs at `http://localhost:5173`. It works in demo mode without Supabase credentials.

### Full Stack (API + Web)

```bash
# Terminal 1: Backend
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd web && npm run dev
```

### Docker

```bash
docker-compose up -d
# Backend: http://localhost:8000
# Frontend: http://localhost:4173
```

## Environment Variables

1. Copy `.env.example` to `.env` at the project root (backend).
2. Copy `web/.env.example` to `web/.env.local` (frontend).
3. **Never commit `.env` or `.env.local` files.**

### Backend Variables

| Variable | Description |
|----------|-------------|
| `ENVIRONMENT` | `development` / `staging` / `production` |
| `API_PORT` | FastAPI port (default: 8000) |
| `CORS_ORIGINS` | Comma-separated allowed CORS origins |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (⚠️ server-only) |
| `JWT_SECRET` | Supabase JWT secret (for token validation) |
| `JWT_ALGORITHM` | `HS256` (default) |
| `JWT_AUDIENCE` | `authenticated` (default) |
| `LOG_LEVEL` | `INFO` (default) |
| `ANTHROPIC_API_KEY` | Optional — for AI writing feedback |

### Frontend Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | FastAPI backend URL |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous key |

⚠️ **Never put `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET`, or `ANTHROPIC_API_KEY` in frontend env vars.**

## Database

### Web (Supabase PostgreSQL) — Primary

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run SQL migrations from `supabase/migrations/` (files 001-011) in order
3. Seed vocabulary data using scripts in `data/seed/`
4. Configure Supabase Auth redirect URLs

See [docs/web-deployment.md](docs/web-deployment.md) for detailed instructions.

### Desktop (SQLite) — Legacy

- Auto-created on first run at `data.db`
- Schema migrations run automatically on startup
- Seed data (50,000+ vocabulary words) loaded on first run

## Testing

```bash
# Backend tests
python -m pytest tests/ -v

# Frontend tests
cd web && npm test

# Frontend lint
cd web && npm run lint

# Frontend build
cd web && npm run build
```

## Build

### Desktop EXE
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name EnglishCoachPro main.py
```

### Web Frontend
```bash
cd web && npm run build
```

Output is in `web/dist/`, deployable to Cloudflare Pages, Netlify, or Vercel.

## Deployment

See [docs/web-deployment.md](docs/web-deployment.md) for full deployment instructions.

- **Frontend**: Cloudflare Pages, Vercel, or Netlify (static hosting)
- **Backend**: Render, Railway, Fly.io, or any Docker host
- **Database**: Supabase managed PostgreSQL
- **Auth**: Supabase Auth

### Quick Deploy

```bash
# Backend (Docker)
docker build -t englishcoach-api .
docker run -p 8000:8000 \
  -e JWT_SECRET=your-secret \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_ANON_KEY=your-key \
  -e SUPABASE_SERVICE_ROLE_KEY=your-key \
  -e CORS_ORIGINS=https://your-frontend.pages.dev \
  -e ENVIRONMENT=production \
  englishcoach-api

# Frontend
cd web && npm run build
# Deploy web/dist to your static host
```

## Documentation

Full documentation is available in the `docs/` folder. To serve locally:

```bash
pip install mkdocs mkdocs-material
mkdocs serve --config-file docs/mkdocs.yml
```

## Contribution

This is an open-source, non-profit project. Contributions are welcome!

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, branch naming, commit conventions, and pull request guidelines.

## Project Structure

```
EnglishApp/
├── api.py                  # FastAPI backend entry point
├── routers/                # Domain API routers
│   ├── profile.py          # Profile CRUD
│   ├── vocabulary.py       # Vocabulary list/search
│   ├── reviews.py          # SRS reviews
│   ├── study_sessions.py   # Study sessions
│   ├── progress.py         # Progress stats
│   ├── planner.py          # Study planner
│   ├── errors.py           # Error journal
│   └── writing.py          # Writing submissions
├── core/                   # Business logic & infrastructure
│   ├── config.py           # Configuration
│   ├── security.py         # JWT validation
│   ├── supabase_client.py  # Supabase client
│   ├── web_schemas.py      # Pydantic models
│   ├── srs_engine.py       # SM-2 algorithm
│   └── ...
├── data/                   # Database, models, seed data
├── web/                    # Web frontend (React + TypeScript)
│   └── src/
│       ├── api/            # Typed API clients
│       ├── components/     # React components
│       ├── hooks/          # React Query hooks
│       ├── pages/          # Route pages
│       ├── stores/         # Zustand stores
│       └── lib/            # Utilities
├── supabase/               # Database migrations
│   └── migrations/         # SQL migration files
├── tests/                  # Test suite
├── docs/                   # Documentation
├── .github/workflows/      # CI/CD pipelines
├── Dockerfile              # Backend container
├── docker-compose.yml      # Multi-service Docker config
├── requirements.txt        # Python dependencies
├── .env.example            # Backend env template
├── web/.env.example        # Frontend env template
├── LICENSE                 # MIT License
└── CONTRIBUTING.md         # Contribution guidelines
```

## License

[MIT](LICENSE) — Open source, non-profit educational project.
