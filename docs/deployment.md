# Deployment Guide

## Overview

EnglishCoach Pro can be deployed in multiple ways depending on your needs.

## Desktop App (Windows)

### Build EXE

```bash
pip install -r requirements.txt pyinstaller
pyinstaller --onefile --windowed --name EnglishCoachPro main.py
```

The EXE will be at `dist/EnglishCoachPro.exe`.

### Distribute via GitHub Releases

1. Tag a release: `git tag v1.0.0 && git push origin v1.0.0`
2. GitHub Actions automatically builds the EXE and creates a release.
3. Users download the EXE from the GitHub Releases page.

## Web Frontend (Cloudflare Pages)

### Build Command
```bash
cd web && npm run build
```

### Output Directory
```
web/dist
```

### Environment Variables (set in Cloudflare Pages dashboard)
| Variable | Description |
|----------|-------------|
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous key |

### SPA Routing
The app uses React Router with `BrowserRouter`. Cloudflare Pages handles SPA routing automatically with a `/*` rewrite to `/index.html`.

### API Base URL
The frontend communicates with the FastAPI backend. Configure the API URL via environment variable or update `web/src/lib/supabase.ts`.

## Backend API (Docker)

### Build and Run
```bash
docker build -t englishcoach-api .
docker run -p 8000:8000 \
  -e CORS_ORIGINS=https://your-frontend-domain.com \
  englishcoach-api
```

### Docker Compose
```bash
docker-compose up -d
```

### Health Check
```bash
curl http://localhost:8000/api/v1/health
# {"status":"healthy"}
```

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `API_PORT` | `8000` | Backend port |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:4173` | Allowed CORS origins |

## Database

### Desktop (SQLite)
- Auto-created on first run at `data.db`
- Schema migrations run automatically via `migrate_schema()` in `data/database.py`
- Seed data loaded on startup via `data/seed/load_seed_data()`

### Web (Supabase)
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run migrations:
   ```bash
   # Via Supabase CLI
   supabase db push

   # Or via Supabase SQL Editor
   # Run web/supabase/migrations/001_initial.sql
   # Run web/supabase/migrations/002_seed_vocab.sql
   ```
3. Set edge function secrets:
   - `ANTHROPIC_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`

## GitHub Actions Secrets

Set these in GitHub → Settings → Secrets and variables → Actions:

| Secret | Required For |
|--------|-------------|
| `SUPABASE_URL` | Edge functions |
| `SUPABASE_ANON_KEY` | Edge functions |
| `ANTHROPIC_API_KEY` | AI feedback edge function |
| `CLOUDFLARE_API_TOKEN` | Frontend deployment (future) |
| `CLOUDFLARE_ACCOUNT_ID` | Frontend deployment (future) |
