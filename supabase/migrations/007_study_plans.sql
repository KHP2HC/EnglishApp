-- ─────────────────────────────────────────────────────────────────────
-- 007_study_plans.sql — Canonical study_plans table
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- Design decisions:
--   • One row per user per week (unique user_id + week_start).
--   • daily_tasks stores the plan as JSONB (flexible structure).
--   • No soft delete — old plans are simply replaced by new ones.
--   • updated_at maintained by trigger for sync conflict resolution.
--
-- Non-destructive: uses CREATE TABLE IF NOT EXISTS.

create table if not exists study_plans (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references profiles(id) on delete cascade,
  week_start  date not null,
  daily_tasks jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (user_id, week_start)
);

-- ── Indexes ──────────────────────────────────────────────────────────
-- Unique constraint (user_id, week_start) already creates an implicit index.
-- Additional index for querying a user's plans ordered by week:
create index if not exists idx_study_plans_user_week
  on study_plans (user_id, week_start);

-- ── Row Level Security ──────────────────────────────────────────────
alter table study_plans enable row level security;

drop policy if exists "study_plans_select_own" on study_plans;
create policy "study_plans_select_own" on study_plans
  for select using (auth.uid() = user_id);

drop policy if exists "study_plans_insert_own" on study_plans;
create policy "study_plans_insert_own" on study_plans
  for insert with check (auth.uid() = user_id);

drop policy if exists "study_plans_update_own" on study_plans;
create policy "study_plans_update_own" on study_plans
  for update using (auth.uid() = user_id);

drop policy if exists "study_plans_delete_own" on study_plans;
create policy "study_plans_delete_own" on study_plans
  for delete using (auth.uid() = user_id);
