-- ─────────────────────────────────────────────────────────────────────
-- 006_error_journal.sql — Canonical error_journal table
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- Design decisions:
--   • Immutable historical record — no updated_at, no deleted_at.
--   • session_id is nullable (errors can be logged outside a session).
--   • skill column added (from Supabase schema) for skill-level tracking.
--   • content column dropped (redundant with question_snapshot).
--
-- Non-destructive: uses CREATE TABLE IF NOT EXISTS.

create table if not exists error_journal (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references profiles(id) on delete cascade,
  session_id        uuid references study_sessions(id) on delete set null,
  error_category    text,
  skill             text,
  question_snapshot text,
  user_answer       text,
  correct_answer    text,
  created_at        timestamptz not null default now()
);

-- ── Indexes ──────────────────────────────────────────────────────────
-- Query: "get recent errors for user X"
create index if not exists idx_error_journal_user_created
  on error_journal (user_id, created_at);

-- ── Row Level Security ──────────────────────────────────────────────
alter table error_journal enable row level security;

drop policy if exists "error_journal_select_own" on error_journal;
create policy "error_journal_select_own" on error_journal
  for select using (auth.uid() = user_id);

drop policy if exists "error_journal_insert_own" on error_journal;
create policy "error_journal_insert_own" on error_journal
  for insert with check (auth.uid() = user_id);

drop policy if exists "error_journal_update_own" on error_journal;
create policy "error_journal_update_own" on error_journal
  for update using (auth.uid() = user_id);

drop policy if exists "error_journal_delete_own" on error_journal;
create policy "error_journal_delete_own" on error_journal
  for delete using (auth.uid() = user_id);
