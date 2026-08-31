# EnglishCoach Pro — Web App

AI-Powered English Exam Preparation PWA for TOEIC, IELTS, TOEFL, and VSTEP.

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit .env.local with your Supabase URL and anon key

# Run dev server
npm run dev
```

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **UI**: shadcn/ui (Radix primitives)
- **State**: Zustand (global) + TanStack Query (server)
- **Backend**: Supabase (PostgreSQL + Auth + Edge Functions)
- **Charts**: Recharts
- **PWA**: vite-plugin-pwa
- **Animations**: Framer Motion

## Project Structure

```
src/
├── lib/          # Core logic (srs, planner, cat, offline, supabase)
├── stores/       # Zustand stores (auth, session, settings)
├── hooks/        # React hooks (useVocab, useStudyPlan, useProgress, useSpeech)
├── pages/        # 13 route pages
├── components/
│   ├── layout/   # Sidebar, TopBar, BottomNav, AppLayout
│   ├── ui/       # shadcn/ui base components
│   ├── dashboard/# StreakBanner, GoalRing, DailyPlan, WordOfDay
│   ├── vocab/    # FlashCard, QualityButtons, SessionSummary
│   └── progress/ # Heatmap, SkillRadar, BandLine, ErrorJournal
└── App.tsx       # Router + Auth provider
```

## Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Run `supabase/migrations/001_initial.sql` in the SQL Editor
3. Run `supabase/migrations/002_seed_vocab.sql` to seed vocabulary
4. Deploy Edge Functions:
   ```bash
   supabase functions deploy ai-feedback
   supabase functions deploy fetch-content
   supabase functions deploy keep-alive
   ```
5. Set the Anthropic API key:
   ```bash
   supabase secrets set ANTHROPIC_API_KEY=sk-ant-...
   ```
6. Schedule the keep-alive cron in Supabase Dashboard (every 5 days)

## Deploy to Vercel

1. Push to GitHub
2. Connect repo in Vercel
3. Set environment variables: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
4. Deploy

## Features

- 🧠 SRS Vocabulary (SM-2 algorithm, offline support via IndexedDB)
- 📐 Grammar lessons with exercises
- 📖 Reading practice with comprehension questions
- 🎧 Listening with browser TTS
- ✍️ AI writing feedback (Claude via Edge Function)
- 🗣️ Pronunciation coach (Web Speech API)
- 🧪 Mock tests (TOEIC, IELTS, TOEFL, VSTEP)
- 📊 Progress tracking (heatmap, charts, error journal)
- 🗓️ AI study planner
- 📌 PWA installable, works offline for vocabulary

## License

MIT
