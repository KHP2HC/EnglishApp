-- ─────────────────────────────────────────────────────────────────────
-- 009_writing_submissions.sql — Canonical writing_submissions table
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- SOFT DELETE DESIGN DECISION:
--   writing_submissions is the ONLY table with soft delete (deleted_at).
--   Rationale:
--     • A user may "delete" a submission from their dashboard, but the
--       data should be retained for analytics and audit purposes.
--     • AI feedback is expensive to generate — deleting and re-submitting
--       would waste resources.
--     • Future feature: "restore deleted submissions".
--   Other tables do NOT have soft delete:
--     • profiles: hard delete via auth.users cascade
--     • vocab_cards: global content, permanent
--     • vocab_progress: cascade delete with user
--     • study_sessions: immutable historical record
--     • error_journal: immutable historical record
--     • study_plans: replaced by new plan (unique constraint)
--     • content_cache: expired rows purged by job
--
-- Non-destructive: uses CREATE TABLE IF NOT EXISTS.

create table if not exists writing_submissions (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references profiles(id) on delete cascade,
  task_prompt   text,
  user_essay    text,
  ai_feedback   jsonb,
  band_estimate numeric(3,1),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  deleted_at    timestamptz
);

-- ── Indexes ──────────────────────────────────────────────────────────
-- Query: "get submissions for user X (excluding deleted)"
create index if not exists idx_writing_submissions_user_created
  on writing_submissions (user_id, created_at);

-- ── Row Level Security ──────────────────────────────────────────────
alter table writing_submissions enable row level security;

drop policy if exists "writing_submissions_select_own" on writing_submissions;
create policy "writing_submissions_select_own" on writing_submissions
  for select using (auth.uid() = user_id);

drop policy if exists "writing_submissions_insert_own" on writing_submissions;
create policy "writing_submissions_insert_own" on writing_submissions
  for insert with check (auth.uid() = user_id);

drop policy if exists "writing_submissions_update_own" on writing_submissions;
create policy "writing_submissions_update_own" on writing_submissions
  for update using (auth.uid() = user_id);

drop policy if exists "writing_submissions_delete_own" on writing_submissions;
create policy "writing_submissions_delete_own" on writing_submissions
  for delete using (auth.uid() = user_id);
