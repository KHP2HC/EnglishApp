-- ─────────────────────────────────────────────────────────────────────
-- 002_profiles.sql — Canonical profiles table
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- Design decisions:
--   • id = auth.users.id (UUID). No duplicate auth credentials here.
--   • All timestamps are TIMESTAMPTZ (timezone-aware).
--   • created_at is immutable (set once by default).
--   • updated_at is maintained by trigger (see 010_triggers.sql).
--   • No soft delete — profiles are hard-deleted via auth.users cascade.
--   • Application-level profile info only (no auth credentials).
--
-- Non-destructive: uses CREATE TABLE IF NOT EXISTS.

create table if not exists profiles (
  id              uuid primary key references auth.users(id) on delete cascade,
  name            text        not null default '',
  avatar_emoji    text        default '🧑',
  target_exam     text        check (target_exam in ('TOEIC','IELTS','TOEFL','VSTEP')),
  target_score    numeric(4,1),
  current_band    numeric(3,1),
  skill_bands     jsonb       default '{}'::jsonb,
  exam_date       date,
  free_time       jsonb       default '{"mon":60,"tue":60,"wed":60,"thu":60,"fri":60,"sat":120,"sun":120}'::jsonb,
  daily_schedule  jsonb       default '{}'::jsonb,
  session_time    text        check (session_time in ('MORNING','AFTERNOON','EVENING')) default 'MORNING',
  theme_mode      text        default 'dark',
  streak_days     int         default 0  check (streak_days >= 0),
  total_xp        int         default 0  check (total_xp >= 0),
  last_active     timestamptz,
  onboarded       boolean     default false,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

-- ── Indexes ──────────────────────────────────────────────────────────
create index if not exists idx_profiles_created_at on profiles (created_at);

-- ── Row Level Security ──────────────────────────────────────────────
alter table profiles enable row level security;

-- Users can read and modify only their own profile
drop policy if exists "profiles_select_own" on profiles;
create policy "profiles_select_own" on profiles
  for select using (auth.uid() = id);

drop policy if exists "profiles_insert_own" on profiles;
create policy "profiles_insert_own" on profiles
  for insert with check (auth.uid() = id);

drop policy if exists "profiles_update_own" on profiles;
create policy "profiles_update_own" on profiles
  for update using (auth.uid() = id);

drop policy if exists "profiles_delete_own" on profiles;
create policy "profiles_delete_own" on profiles
  for delete using (auth.uid() = id);
