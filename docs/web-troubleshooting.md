# Web Troubleshooting

Common issues and solutions for the EnglishCoach Pro web application.

---

## Frontend Issues

### "Network error — cannot reach the server"

**Cause:** The frontend cannot connect to the FastAPI backend.

**Solutions:**
1. Verify the backend is running: `curl http://localhost:8000/api/v1/health`
2. Check `VITE_API_BASE_URL` in `web/.env.local`
3. Ensure CORS is configured: `CORS_ORIGINS` must include `http://localhost:5173`
4. Check browser console for CORS errors

### "Authentication required" on all API calls

**Cause:** JWT is not being sent or is invalid.

**Solutions:**
1. Verify Supabase is configured: `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
2. Check that you're logged in (the auth store has a session)
3. Verify `JWT_SECRET` on the backend matches your Supabase project's JWT secret
4. Check that the JWT hasn't expired

### App shows demo mode (no real data)

**Cause:** Supabase or API is not configured.

**Solutions:**
1. Set `VITE_API_BASE_URL` in `web/.env.local`
2. Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
3. Restart the dev server: `npm run dev`

### Build fails with TypeScript errors

**Solutions:**
1. Run `npm run build` to see specific errors
2. Check for missing imports or type mismatches
3. Ensure all dependencies are installed: `npm install`

---

## Backend Issues

### "JWT_SECRET is not configured"

**Cause:** The `JWT_SECRET` environment variable is not set.

**Solution:**
1. Set `JWT_SECRET` in your `.env` file
2. Get the value from Supabase Dashboard → Settings → API → JWT Secret
3. Restart the backend

### "Database is not configured"

**Cause:** Supabase credentials are missing.

**Solution:**
1. Set `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` in `.env`
2. Verify the URL format: `https://your-project.supabase.co`
3. Restart the backend

### CORS errors in browser

**Cause:** The frontend origin is not in the allowed CORS origins.

**Solution:**
1. Set `CORS_ORIGINS` to include your frontend URL
2. Example: `CORS_ORIGINS=http://localhost:5173,https://your-app.pages.dev`
3. Restart the backend

### Rate limit (429) errors

**Cause:** Too many requests from the same IP.

**Solutions:**
1. Increase `RATE_LIMIT_DEFAULT_REQUESTS` in `.env`
2. For production, consider Redis-backed rate limiting

---

## Database Issues

### "relation does not exist"

**Cause:** Database migrations haven't been run.

**Solution:**
1. Run all SQL migration files in order (001-011) in the Supabase SQL Editor
2. Or use the Supabase CLI: `supabase db push`

### "permission denied" on table

**Cause:** RLS is blocking access.

**Solutions:**
1. Verify RLS policies are created (migration files 002-009)
2. Ensure the user is authenticated
3. Check that the backend uses the service-role key (bypasses RLS)
4. The backend must always filter by `user_id` from the JWT

### Vocabulary table is empty

**Cause:** Seed data hasn't been loaded.

**Solution:**
1. Run the seed SQL in Supabase SQL Editor
2. Or run: `python data/seed/expand_vocab.py`
3. Verify: `SELECT count(*) FROM vocab_cards;`

---

## Authentication Issues

### "Email not confirmed"

**Cause:** Supabase requires email confirmation.

**Solutions:**
1. Check your email for a confirmation link
2. In development, disable email confirmation in Supabase Dashboard → Authentication → Settings
3. For testing, use the Supabase Dashboard to manually confirm users

### Google OAuth redirect fails

**Cause:** Redirect URL not configured.

**Solution:**
1. In Supabase Dashboard → Authentication → URL Configuration
2. Add your redirect URL: `https://your-app.pages.dev/auth/callback`
3. In Google Cloud Console, add the same redirect URL to your OAuth credentials

### Session expires immediately

**Cause:** JWT secret mismatch or clock skew.

**Solutions:**
1. Verify `JWT_SECRET` matches your Supabase project
2. Check server time is correct
3. Verify `JWT_AUDIENCE` is set to `authenticated`

---

## Deployment Issues

### Docker build fails

**Solutions:**
1. Check `requirements.txt` for missing packages
2. Ensure Python version is 3.12+
3. Try building without cache: `docker build --no-cache .`

### Frontend deploy shows blank page

**Cause:** SPA routing not configured.

**Solutions:**
1. GitHub Pages: the `deploy-pages.yml` workflow handles this automatically
2. For Cloudflare Pages: add a `_redirects` file with `/* /index.html 200`
3. For Nginx: use `try_files $uri $uri/ /index.html;`
4. For Netlify: create a `public/_redirects` file

### GitHub Pages shows 404 on refresh

**Cause:** GitHub Pages doesn't handle SPA routing by default.

**Solutions:**
1. The `deploy-pages.yml` workflow uses `actions/deploy-pages` which handles SPA routing
2. If issues persist, add a `web/public/404.html` that redirects to `index.html`
3. The `BrowserRouter` in `main.tsx` uses `basename={import.meta.env.BASE_URL}` to handle the `/EnglishApp/` subpath

### GitHub Pages build fails in Actions

**Solutions:**
1. Check that GitHub Secrets are set: `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
2. Verify the workflow has `permissions: pages: write, id-token: write`
3. Check that Pages source is set to "GitHub Actions" in repo settings

### Environment variables not working

**Solutions:**
1. For Vite: variables must start with `VITE_`
2. For Docker: use `-e VAR=value` or `--env-file`
3. For Cloudflare Pages: set in dashboard → Settings → Environment variables
4. Restart the server after changing env vars

---

## Getting Help

1. Check the browser console for errors
2. Check the backend logs
3. Verify environment variables are set correctly
4. Consult the [architecture document](web-architecture.md)
5. Consult the [deployment guide](web-deployment.md)
