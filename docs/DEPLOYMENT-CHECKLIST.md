# Deployment Checklist — EnglishCoach Pro

Use this checklist to track deployment progress. Each item must be completed before the application is fully operational.

---

## 1. Supabase Setup

- [ ] Supabase project created at [supabase.com](https://supabase.com)
- [ ] Project URL copied from Settings → API
- [ ] Anon key copied from Settings → API
- [ ] Service role key copied from Settings → API (⚠️ SERVER-SIDE ONLY)
- [ ] JWT Secret copied from Settings → API

## 2. Database Migrations

- [ ] `001_extensions.sql` executed
- [ ] `002_profiles.sql` executed
- [ ] `003_vocab_cards.sql` executed
- [ ] `004_vocab_progress.sql` executed
- [ ] `005_study_sessions.sql` executed
- [ ] `006_error_journal.sql` executed
- [ ] `007_study_plans.sql` executed
- [ ] `008_content_cache.sql` executed
- [ ] `009_writing_submissions.sql` executed
- [ ] `010_triggers.sql` executed
- [ ] `011_migration_id_map.sql` executed

## 3. Vocabulary Seeded

- [ ] Seed SQL executed in Supabase SQL Editor
- [ ] `SELECT count(*) FROM vocab_cards;` returns > 0

## 4. Supabase Auth Configured

- [ ] Email provider enabled
- [ ] Site URL set to production frontend URL
- [ ] Redirect URLs added (production + localhost for dev)

## 5. Backend Secrets Configured

- [ ] `SUPABASE_URL` set
- [ ] `SUPABASE_ANON_KEY` set
- [ ] `SUPABASE_SERVICE_ROLE_KEY` set
- [ ] `JWT_SECRET` set
- [ ] `CORS_ORIGINS` set to frontend URL
- [ ] `ENVIRONMENT=production`

## 6. Frontend Environment Configured

- [ ] `VITE_API_BASE_URL` set to backend URL
- [ ] `VITE_SUPABASE_URL` set
- [ ] `VITE_SUPABASE_ANON_KEY` set
- [ ] No service-role keys in frontend env

## 7. Backend Deployed

- [ ] Docker image built (or deployed to Render/Railway/Fly.io)
- [ ] Backend accessible at public URL
- [ ] `GET /api/v1/health` returns `{"status":"healthy"}`

## 8. Frontend Deployed

- [ ] Frontend built with correct env vars
- [ ] Deployed to Cloudflare Pages / Vercel / Netlify
- [ ] Frontend accessible at public URL

## 9. CORS Configured

- [ ] Backend `CORS_ORIGINS` includes frontend URL
- [ ] No wildcard (`*`) in production CORS

## 10. Auth Redirect Configured

- [ ] Supabase Auth redirect URL matches frontend URL
- [ ] OAuth callback works (if using OAuth providers)

## 11. Smoke Test

- [ ] Registration tested
- [ ] Login tested
- [ ] Dashboard loads
- [ ] Vocabulary list loads
- [ ] Vocabulary search works
- [ ] Study session starts
- [ ] SRS card review works
- [ ] Progress page loads
- [ ] Planner page loads
- [ ] Error journal loads
- [ ] Writing submission works (if enabled)
- [ ] Logout works
- [ ] Login again (session persistence)

## 12. Security Verification

- [ ] Cross-user data isolation tested
- [ ] Unauthenticated API requests return 401
- [ ] No secrets in frontend build output
- [ ] HTTPS enforced

---

## GitHub Secrets (for CI/CD)

- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_ANON_KEY`
- [ ] `SUPABASE_SERVICE_ROLE_KEY`
- [ ] `JWT_SECRET`
- [ ] `VITE_API_BASE_URL`
- [ ] `VITE_SUPABASE_URL`
- [ ] `VITE_SUPABASE_ANON_KEY`
- [ ] `CLOUDFLARE_API_TOKEN` (if using Cloudflare Pages)
- [ ] `CLOUDFLARE_ACCOUNT_ID` (if using Cloudflare Pages)
