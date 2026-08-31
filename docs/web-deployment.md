# Web Deployment Guide

This document provides exact, step-by-step instructions for deploying EnglishCoach Pro to production.

---

## Prerequisites

- A [Supabase](https://supabase.com) account (free tier works)
- A GitHub account (for CI/CD and source control)
- A backend host (Render, Railway, Fly.io, or any Docker-compatible host)
- A frontend host (Cloudflare Pages, Vercel, or Netlify)

---

## Step 1: Create a Supabase Project

**AUTOMATED BY CODE:** Migrations are in `supabase/migrations/`

**MANUAL USER ACTION REQUIRED:**

1. Go to [https://supabase.com](https://supabase.com) and sign up / log in
2. Click **New Project**
3. Name it `englishcoach-pro`
4. Choose a region close to your users
5. Set a strong database password (save it somewhere safe)
6. Wait for the project to provision (~2 minutes)

### Get your project credentials

Go to **Settings → API** and copy:
- **Project URL** → `SUPABASE_URL`
- **anon public key** → `SUPABASE_ANON_KEY` / `VITE_SUPABASE_ANON_KEY`
- **service_role key** → `SUPABASE_SERVICE_ROLE_KEY` (⚠️ SERVER-SIDE ONLY)
- **JWT Secret** → `JWT_SECRET` (found in Settings → API → JWT Secret)

---

## Step 2: Run Database Migrations

**AUTOMATED BY CODE:** SQL files are in `supabase/migrations/`

**MANUAL USER ACTION REQUIRED:**

1. In your Supabase dashboard, go to **SQL Editor**
2. Run each migration file in order (001 through 011):
   - Copy the contents of `supabase/migrations/001_extensions.sql`
   - Paste into the SQL Editor and click **Run**
   - Repeat for each file (002, 003, ..., 011)

Or use the Supabase CLI:
```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref your-project-ref

# Push migrations
supabase db push
```

---

## Step 3: Seed Vocabulary Data

**MANUAL USER ACTION REQUIRED:**

1. In the Supabase SQL Editor, run the seed SQL:
   - Use `supabase/seeds/` directory contents
   - Or use the Python seed script: `python data/seed/expand_vocab.py`

2. Verify data was inserted:
   ```sql
   SELECT count(*) FROM vocab_cards;
   -- Should return > 0
   ```

---

## Step 4: Configure Supabase Auth

**MANUAL USER ACTION REQUIRED:**

1. In Supabase dashboard, go to **Authentication → Providers**
2. Enable **Email** provider (enabled by default)
3. (Optional) Enable **Google** OAuth provider:
   - You need a Google Cloud project with OAuth credentials
   - Set the redirect URL to: `https://your-frontend-domain/auth/callback`
4. Go to **Authentication → URL Configuration**
5. Set **Site URL** to your frontend URL (e.g., `https://your-app.pages.dev`)
6. Add **Redirect URLs**:
   - `https://your-app.pages.dev/**`
   - `http://localhost:5173/**` (for local development)

---

## Step 5: Configure Backend Environment Variables

**AUTOMATED BY CODE:** `.env.example` exists in the repository

**MANUAL USER ACTION REQUIRED:**

Create a `.env` file in the project root with:

```env
ENVIRONMENT=production
API_PORT=8000
CORS_ORIGINS=https://your-frontend-domain.pages.dev
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_AUDIENCE=authenticated
LOG_LEVEL=INFO
# Optional: for AI writing feedback
# ANTHROPIC_API_KEY=your-key
```

⚠️ **NEVER commit `.env` to Git.** It is in `.gitignore`.

---

## Step 6: Configure Frontend Environment Variables

**AUTOMATED BY CODE:** `web/.env.example` exists in the repository

**MANUAL USER ACTION REQUIRED:**

Create `web/.env.local` (or set in your hosting platform):

```env
VITE_API_BASE_URL=https://your-backend-domain.example
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

⚠️ **NEVER put service-role keys or JWT secrets in frontend env vars.**

---

## Step 7: Deploy FastAPI Backend

### Option A: Render (recommended for free tier)

1. Go to [render.com](https://render.com) and sign up
2. Create a new **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:** Add all from Step 5
5. Deploy

### Option B: Railway

1. Go to [railway.app](https://railway.app) and sign up
2. Create a new project from your GitHub repo
3. Railway auto-detects the Dockerfile
4. Add environment variables from Step 5
5. Deploy

### Option C: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch
fly launch

# Set secrets
fly secrets set JWT_SECRET=your-secret
fly secrets set SUPABASE_URL=your-url
fly secrets set SUPABASE_ANON_KEY=your-key
fly secrets set SUPABASE_SERVICE_ROLE_KEY=your-key
fly secrets set CORS_ORIGINS=https://your-frontend.pages.dev
fly secrets set ENVIRONMENT=production

# Deploy
fly deploy
```

### Option D: Docker (any host)

```bash
docker build -t englishcoach-api .
docker run -p 8000:8000 \
  -e JWT_SECRET=your-secret \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_ANON_KEY=your-key \
  -e SUPABASE_SERVICE_ROLE_KEY=your-key \
  -e CORS_ORIGINS=https://your-frontend.pages.dev \
  -e ENVIRONMENT=production \
  englishcoach-api
```

---

## Step 8: Deploy React Frontend

### Option A: Cloudflare Pages (recommended)

1. Go to [pages.cloudflare.com](https://pages.cloudflare.com)
2. Create a new project from your GitHub repo
3. Configure:
   - **Build command:** `cd web && npm ci && npm run build`
   - **Build output directory:** `web/dist`
   - **Environment variables:**
     - `VITE_API_BASE_URL` = your backend URL
     - `VITE_SUPABASE_URL` = your Supabase URL
     - `VITE_SUPABASE_ANON_KEY` = your Supabase anon key
4. Deploy

### Option B: Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repo
3. Set root directory to `web`
4. Add environment variables
5. Deploy

### Option C: Netlify

1. Go to [netlify.com](https://netlify.com)
2. Create a new site from Git
3. Set base directory to `web`
4. Build command: `npm run build`
5. Publish directory: `dist`
6. Add environment variables
7. Deploy

---

## Step 9: Configure CORS

**AUTOMATED BY CODE:** CORS is configured via `CORS_ORIGINS` env var

**MANUAL USER ACTION REQUIRED:**

1. Set `CORS_ORIGINS` on the backend to your exact frontend URL
   - Example: `https://your-app.pages.dev`
   - Do NOT use `*` in production
2. If using a custom domain, update `CORS_ORIGINS` to include it

---

## Step 10: Configure Auth Redirect URLs

**MANUAL USER ACTION REQUIRED:**

1. In Supabase dashboard → Authentication → URL Configuration
2. Set **Site URL** to your production frontend URL
3. Add redirect URLs:
   - `https://your-app.pages.dev/**`
   - `https://your-app.pages.dev/auth/callback`

---

## Step 11: Verify Health Endpoint

**AUTOMATED BY CODE:** `GET /api/v1/health` endpoint exists

**MANUAL USER ACTION REQUIRED:**

```bash
curl https://your-backend-domain.example/api/v1/health
# Should return: {"status":"healthy"}
```

---

## Step 12: Verify Public Website

**MANUAL USER ACTION REQUIRED:**

1. Open your frontend URL in a browser
2. You should see the landing page
3. Click "Start for free"
4. Register a new account
5. Complete onboarding
6. Verify the dashboard loads
7. Verify vocabulary loads
8. Start a study session
9. Rate a card
10. Check progress page

---

## Rollback Procedure

### Backend Rollback
1. In your hosting platform, redeploy the previous version
2. If database migration caused issues, use Supabase's point-in-time recovery

### Frontend Rollback
1. In Cloudflare Pages (or your host), select a previous deployment
2. Click "Rollback to this deployment"

### Database Rollback
1. Use Supabase's database backup/restore feature
2. Or run a rollback migration (create one that reverses the changes)

---

## Security Checklist

- [ ] `.env` is not committed to Git
- [ ] `SUPABASE_SERVICE_ROLE_KEY` is not in frontend env vars
- [ ] `JWT_SECRET` is not in frontend env vars
- [ ] CORS origins are set to specific domains (not `*`)
- [ ] Supabase Auth redirect URLs are configured
- [ ] RLS is enabled on all user-owned tables
- [ ] Health endpoint returns 200
- [ ] HTTPS is enforced (via hosting platform)
