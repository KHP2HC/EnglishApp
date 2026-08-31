# Local vs Production Web Audit

**Date:** 2026-08-31  
**Repository:** KHP2HC/EnglishApp  
**Local URL:** http://localhost:5173  
**Production URL:** https://khp2hc.github.io/EnglishApp/app

## Summary

The local web application under `web/` is the source of truth. The production
GitHub Pages deployment was previously broken due to absolute path issues that
caused assets and seed data to fail loading under the `/EnglishApp/` subpath.

## Comparison

| Area | Local | GitHub Pages (Before) | GitHub Pages (After) | Required Action |
|------|-------|----------------------|----------------------|-----------------|
| Application shell | AppLayout with Sidebar + TopBar + BottomNav | ✅ Same | ✅ Same | None |
| Navbar / Sidebar | 11 nav items, collapsible, level badge | ✅ Same | ✅ Same | None |
| Dashboard | Greeting, StreakBanner, GoalRing, StatCards, DailyPlan, WordOfDay | ✅ Same | ✅ Same | None |
| Vocabulary | SRS flashcards, SM-2, session timer, quality buttons | ✅ Same | ✅ Same | None |
| Vocabulary search | API-backed with seed data fallback | ✅ Same | ✅ Same | None |
| Vocabulary detail | FlashCard flip, synonyms, antonyms, TTS | ✅ Same | ✅ Same | None |
| SRS | SM-2 algorithm, local localStorage fallback | ✅ Same | ✅ Same | None |
| Study session | Timer, XP tracking, session summary | ✅ Same | ✅ Same | None |
| Progress | Heatmap, SkillRadar, BarChart, ErrorJournal | ✅ Same | ✅ Same | None |
| Planner | AI-generated weekly plan, local fallback | ✅ Same | ✅ Same | None |
| Writing | IELTS writing tasks, AI feedback, timer | ✅ Same | ✅ Same | None |
| Mock test | Full exam simulation (IELTS/TOEIC/TOEFL/VSTEP) | ✅ Same | ✅ Same | None |
| Onboarding | 5-step wizard with exam target, free time | ✅ Same | ✅ Same | None |
| Settings | Profile, appearance, notifications, exam info | ✅ Same | ✅ Same | None |
| Authentication | Supabase Auth with demo mode fallback | ✅ Same | ✅ Same | None |
| Responsive layout | Desktop sidebar + mobile bottom nav | ✅ Same | ✅ Same | None |
| CSS | Tailwind CSS with custom theme | ✅ Same | ✅ Same | None |
| Assets | favicon.svg, icon-192.png, icon-512.png | ✅ Same | ✅ Same | None |
| Routing | React Router with BrowserRouter | ✅ Same | ✅ Same | None |
| API integration | FastAPI via typed API client | ✅ Same | ✅ Same | None |
| Supabase integration | Auth only (no direct CRUD) | ✅ Same | ✅ Same | None |
| **Seed data paths** | `fetch('/data/...')` — works locally | ❌ Broken on GitHub Pages | ✅ Fixed with `BASE_URL` prefix | **FIXED** |
| **Notification icon paths** | `/icon-192.png` — works locally | ❌ Broken on GitHub Pages | ✅ Fixed with `BASE_URL` prefix | **FIXED** |
| **Vite base path** | `/` (default) | ❌ Was `/` | ✅ `/EnglishApp/` | **FIXED** |
| **SPA routing** | BrowserRouter works locally | ❌ 404 on refresh | ✅ 404.html fallback | **FIXED** |
| **index.html asset paths** | Absolute `/src/main.tsx` | ❌ Broken | ✅ Relative `./src/main.tsx` | **FIXED** |
| **manifest.json paths** | Absolute `/icon-192.png` | ❌ Broken | ✅ Relative `./icon-192.png` | **FIXED** |

## Issues Found and Fixed

### 1. Vite Base Path (Critical)
- **Before:** `const base = process.env.VITE_BASE_PATH || '/'`
- **After:** `const base = process.env.VITE_BASE_PATH || '/EnglishApp/'`
- **Impact:** All bundled JS/CSS assets were served from root instead of `/EnglishApp/`

### 2. Seed Data Fetch Paths (Critical)
- **Before:** `fetch('/data/vocab.json')` → resolves to `https://khp2hc.github.io/data/vocab.json`
- **After:** `fetch(`${BASE}data/vocab.json`)` → resolves to `https://khp2hc.github.io/EnglishApp/data/vocab.json`
- **Impact:** Vocabulary, reading, listening, writing, speaking, and question bank data all failed to load

### 3. index.html Asset Paths (Critical)
- **Before:** `href="/favicon.svg"`, `src="/src/main.tsx"`
- **After:** `href="./favicon.svg"`, `src="./src/main.tsx"`
- **Impact:** Favicon and entry point failed to load on GitHub Pages

### 4. manifest.json Paths (Moderate)
- **Before:** `"start_url": "/"`, `"src": "/icon-192.png"`
- **After:** `"start_url": "./"`, `"src": "./icon-192.png"`
- **Impact:** PWA manifest icons failed to load

### 5. Notification Icon Paths (Minor)
- **Before:** `icon: '/icon-192.png'`, `badge: '/favicon.svg'`
- **After:** `icon: `${base}icon-192.png``, `badge: `${base}favicon.svg``
- **Impact:** Notification icons failed to load on GitHub Pages

### 6. SPA Routing Fallback (Critical)
- **Before:** No 404.html — refreshing a client-side route returned GitHub's 404
- **After:** `scripts/copy-404.js` copies `index.html` → `404.html` after build
- **Impact:** Deep links like `/EnglishApp/app/vocabulary` now work correctly

## Architecture

The application architecture is unchanged:

```
React (Vite)
    ↓
BrowserRouter (basename = BASE_URL)
    ↓
App (Auth check → demo mode if no Supabase)
    ↓
AppLayout (Sidebar + TopBar + BottomNav + Outlet)
    ↓
Pages (Dashboard, Vocabulary, Grammar, Reading, Listening, Writing, Speaking, MockTest, Progress, Planner, Settings)
    ↓
API Client (FastAPI backend)
    ↓
Supabase (Auth only)
```

## Environment Variables

| Variable | Scope | Purpose |
|----------|-------|---------|
| `VITE_BASE_PATH` | Public | Vite base path for subpath hosting |
| `VITE_API_BASE_URL` | Public | FastAPI backend URL |
| `VITE_SUPABASE_URL` | Public | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Public | Supabase anon key (safe for frontend) |

No secrets are committed. The app gracefully falls back to demo mode when
Supabase is not configured.
