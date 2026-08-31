-- ─────────────────────────────────────────────────────────────────────
-- 005_study_sessions.sql — Canonical study_sessions table
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- Design decisions:
--   • Immutable historical record — no updated_at, no deleted_at.
--   • started_at is set when session begins; ended_at set when it ends.
--   • score is NOT stored — it's a derived value (items_correct / items_total).
--   • session_type uses TEXT CHECK (not enum) for flexibility.
--
-- Non-destructive: uses CREATE TABLE IF NOT EXISTS.

create table if not exists study_sessions (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references profiles(id) on delete cascade,
  started_at    timestamptz not null default now(),
  ended_at      timestamptz,
  session_type  text check (session_type in
                ('VOCABULARY','GRAMMAR','LISTENING','READING','WRITING','SPEAKING','MOCK')),
  xp_earned     int not null default 0 check (xp_earned >= 0),
  items_total   int not null default 0 check (items_total >= 0),
  items_correct int not null default 0 check (items_correct >= 0),
  created_at    timestamptz not null default now()
);

-- ── Indexes ──────────────────────────────────────────────────────────
-- Query: "get sessions for user X ordered by start time"
create index if not exists idx_study_sessions_user_started
  on study_sessions (user_id, started_at);

-- ── Row Level Security ──────────────────────────────────────────────
alter table study_sessions enable row level security;

drop policy if exists "study_sessions_select_own" on study_sessions;
create policy "study_sessions_select_own" on study_sessions
  for select using (auth.uid() = user_id);

drop policy if exists "study_sessions_insert_own" on study_sessions;
create policy "study_sessions_insert_own" on study_sessions
  for insert with check (auth.uid() = user_id);

drop policy if exists "study_sessions_update_own" on study_sessions;
create policy "study_sessions_update_own" on study_sessions
  for update using (auth.uid() = user_id);

drop policy if exists "study_sessions_delete_own" on study_sessions;
create policy "study_sessions_delete_own" on study_sessions
  for delete using (auth.uid() = user_id);
