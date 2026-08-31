-- ─────────────────────────────────────────────────────────────────────
-- 004_vocab_progress.sql — Canonical vocab_progress table (user SRS state)
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- SRS TIMESTAMP DESIGN DECISION:
--   The Phase 2A proposal used `next_review DATE`. After reviewing the
--   actual application behavior:
--     • Python SRS engine: uses datetime.date.today() (DATE)
--     • React SRS: uses toISOString().split('T')[0] (DATE string)
--     • Supabase queries: .lte('next_review', today) (DATE comparison)
--
--   We choose `next_review_at TIMESTAMPTZ` because:
--     1. Timezone-aware users: A user in UTC+7 hitting "review" at
--        11pm local time would get a different "today" than a UTC user.
--        TIMESTAMPTZ stores the exact intended review moment.
--     2. Future reminder functionality: Push notifications need an
--        exact time, not just a date.
--     3. Desktop offline operation: When syncing from offline, the
--        exact timestamp matters for conflict resolution.
--     4. Synchronization: LWW conflict resolution uses timestamps.
--
--   The application can still query by date using date_trunc('day', ...)
--   or cast to date for backward-compatible "due today" queries.
--
--   last_quality CHECK: SM-2 algorithm uses 0, 2, 3, 5.
--   We allow 0–5 for flexibility (standard SM-2 range).
--
-- Non-destructive: uses CREATE TABLE IF NOT EXISTS.

create table if not exists vocab_progress (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references profiles(id) on delete cascade,
  card_id         uuid not null references vocab_cards(id) on delete cascade,
  interval_days   int  not null default 1   check (interval_days >= 0),
  easiness        numeric(3,2) not null default 2.50 check (easiness >= 1.30),
  repetitions     int  not null default 0   check (repetitions >= 0),
  next_review_at  timestamptz,
  last_quality    int  check (last_quality >= 0 and last_quality <= 5),
  times_seen      int  not null default 0   check (times_seen >= 0),
  times_correct   int  not null default 0   check (times_correct >= 0),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  unique (user_id, card_id)
);

-- ── Indexes ──────────────────────────────────────────────────────────
-- Primary query: "get due cards for user X" — filter by user + next_review_at
create index if not exists idx_vocab_progress_user_review
  on vocab_progress (user_id, next_review_at);

-- Unique constraint index (user_id, card_id) — already created by UNIQUE,
-- but we document it here for clarity:
--   unique (user_id, card_id) → implicit index: idx_vocab_progress_user_card

-- ── Row Level Security ──────────────────────────────────────────────
alter table vocab_progress enable row level security;

drop policy if exists "vocab_progress_select_own" on vocab_progress;
create policy "vocab_progress_select_own" on vocab_progress
  for select using (auth.uid() = user_id);

drop policy if exists "vocab_progress_insert_own" on vocab_progress;
create policy "vocab_progress_insert_own" on vocab_progress
  for insert with check (auth.uid() = user_id);

drop policy if exists "vocab_progress_update_own" on vocab_progress;
create policy "vocab_progress_update_own" on vocab_progress
  for update using (auth.uid() = user_id);

drop policy if exists "vocab_progress_delete_own" on vocab_progress;
create policy "vocab_progress_delete_own" on vocab_progress
  for delete using (auth.uid() = user_id);
