-- ─────────────────────────────────────────────────────────────────────
-- 001_extensions.sql — Enable required PostgreSQL extensions
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
-- Safe: idempotent. These extensions are already available in Supabase.

-- pgcrypto provides gen_random_uuid() (Supabase enables this by default,
-- but we declare it explicitly for local PostgreSQL environments).
create extension if not exists pgcrypto;

-- citext for case-insensitive text comparisons (used by vocab_cards.word)
create extension if not exists citext;
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
-- ─────────────────────────────────────────────────────────────────────
-- 003_vocab_cards.sql — Canonical vocab_cards table (global content)
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- VOCABULARY UNIQUENESS DESIGN DECISION:
--   After inspecting the actual vocabulary dataset (5,000 records in
--   vocab.json, 5,251 in the existing Supabase seed), every word is
--   unique. Each word has exactly:
--     • one meaning_en
--     • one meaning_vi
--     • one exam_type (single value, not array)
--     • one difficulty_level (CEFR A1–C2)
--     • one category
--   No word appears with multiple meanings, parts of speech, or CEFR
--   levels. Therefore a simple UNIQUE(word) constraint is justified.
--
--   The Phase 2A proposal used exam_type text[] (array). However, the
--   actual data has a single exam_type per word. We keep exam_type as
--   text[] for forward compatibility (a word could appear in multiple
--   exams in the future), but the UNIQUE constraint is on (word) alone
--   since the application treats each word as a single canonical entry.
--
--   If multi-meaning words are needed in the future, a separate
--   vocab_card_meanings child table can be introduced without breaking
--   this schema.
--
-- Non-destructive: uses CREATE TABLE IF NOT EXISTS.

create table if not exists vocab_cards (
  id                uuid primary key default gen_random_uuid(),
  word              text not null unique,
  phonetic          text,
  synonym           text,
  antonym           text,
  meaning_en        text not null,
  meaning_vi        text not null,
  example_sentence  text,
  audio_url         text,
  image_url         text,
  exam_type         text[] default '{}',
  cefr_level        text check (cefr_level in ('A1','A2','B1','B2','C1','C2')),
  category          text default 'general',
  created_at        timestamptz not null default now()
);

-- ── Indexes ──────────────────────────────────────────────────────────
-- Primary lookup index for word search
create index if not exists idx_vocab_cards_word on vocab_cards (word);
-- Filter by CEFR level (common query: "give me A1 words")
create index if not exists idx_vocab_cards_cefr on vocab_cards (cefr_level);
-- Filter by category
create index if not exists idx_vocab_cards_category on vocab_cards (category);

-- ── Row Level Security ──────────────────────────────────────────────
-- Global content: publicly readable, but NOT writable by anonymous users.
alter table vocab_cards enable row level security;

-- Public read: vocabulary is shared global content
drop policy if exists "vocab_cards_public_read" on vocab_cards;
create policy "vocab_cards_public_read" on vocab_cards
  for select using (true);

-- No insert/update/delete policies for anon — only service role can
-- manage vocabulary content (via seed scripts or admin tools).
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
-- ─────────────────────────────────────────────────────────────────────
-- 008_content_cache.sql — Canonical content_cache table
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- CONTENT CACHE DESIGN DECISION:
--   The content_cache stores EXTERNAL API results (fetched articles,
--   reading materials, etc.). The application must NOT depend on cached
--   content being permanently available.
--
--   Schema:
--     • source: identifies the external API (e.g. 'bbc', 'voa', 'british_council')
--     • source_key: unique identifier within the source (e.g. article URL hash)
--     • payload: JSONB — stores the full variable external response.
--       JSONB is used here because external API responses have variable
--       structure that doesn't warrant fixed columns.
--     • fetched_at: when the content was retrieved
--     • expires_at: when the cache entry becomes stale
--
--   Cache invalidation semantics:
--     • TTL-based: entries with expires_at < now() are stale.
--     • The application should check expires_at before using cached content.
--     • A periodic cleanup job can DELETE rows where expires_at < now().
--     • No soft delete — expired entries are hard-deleted by cleanup.
--
--   source + source_key together identify a unique cached item:
--     UNIQUE(source, source_key) prevents duplicate cache entries.
--
-- Non-destructive: uses CREATE TABLE IF NOT EXISTS.

create table if not exists content_cache (
  id            uuid primary key default gen_random_uuid(),
  source        text,
  source_key    text,
  content_type  text,
  title         text,
  body          text,
  payload       jsonb,
  cefr_level    text check (cefr_level in ('A1','A2','B1','B2','C1','C2')),
  exam_type     text,
  fetched_at    timestamptz not null default now(),
  expires_at    timestamptz,
  unique (source, source_key)
);

-- ── Indexes ──────────────────────────────────────────────────────────
-- Query: "get non-expired cache for source X"
create index if not exists idx_content_cache_source_expires
  on content_cache (source, expires_at);

-- Query: "get cache by content type"
create index if not exists idx_content_cache_type
  on content_cache (content_type);

-- ── Row Level Security ──────────────────────────────────────────────
-- Content cache is system-managed (populated by backend/content fetcher).
-- No direct user access — only service role can read/write.
-- RLS enabled but no policies = blocked for anon/authenticated users.
alter table content_cache enable row level security;
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
-- ─────────────────────────────────────────────────────────────────────
-- 010_triggers.sql — Database triggers for timestamp management
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- TIMESTAMP STRATEGY:
--   • created_at: Set by DEFAULT now(). Immutable — never updated by trigger.
--   • updated_at: Updated automatically by trigger on every UPDATE.
--     This prevents clients from arbitrarily manipulating server-controlled
--     timestamps.
--   • deleted_at: Set by application when soft-deleting. Not auto-managed.
--
-- Tables with updated_at:
--   • profiles
--   • vocab_progress
--   • study_plans
--   • writing_submissions
--
-- Tables WITHOUT updated_at (immutable records):
--   • vocab_cards (global content, no updates expected)
--   • study_sessions (immutable historical record)
--   • error_journal (immutable historical record)
--   • content_cache (replaced, not updated)
--
-- Non-destructive: uses CREATE OR REPLACE FUNCTION and DROP TRIGGER IF EXISTS.

-- ── Generic updated_at trigger function ─────────────────────────────
create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ── profiles: updated_at trigger ─────────────────────────────────────
drop trigger if exists trg_profiles_updated_at on profiles;
create trigger trg_profiles_updated_at
  before update on profiles
  for each row execute function set_updated_at();

-- ── vocab_progress: updated_at trigger ───────────────────────────────
drop trigger if exists trg_vocab_progress_updated_at on vocab_progress;
create trigger trg_vocab_progress_updated_at
  before update on vocab_progress
  for each row execute function set_updated_at();

-- ── study_plans: updated_at trigger ──────────────────────────────────
drop trigger if exists trg_study_plans_updated_at on study_plans;
create trigger trg_study_plans_updated_at
  before update on study_plans
  for each row execute function set_updated_at();

-- ── writing_submissions: updated_at trigger ──────────────────────────
drop trigger if exists trg_writing_submissions_updated_at on writing_submissions;
create trigger trg_writing_submissions_updated_at
  before update on writing_submissions
  for each row execute function set_updated_at();

-- ── Auto-create profile on auth signup ──────────────────────────────
-- When a new auth user is created, automatically create their profile.
create or replace function handle_new_user()
returns trigger
language plpgsql
security definer
as $$
begin
  insert into profiles (id, name)
  values (new.id, split_part(new.email, '@', 1));
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();
-- ─────────────────────────────────────────────────────────────────────
-- 011_migration_id_map.sql — UUID migration mapping table
-- ─────────────────────────────────────────────────────────────────────
-- Phase 2B: Canonical PostgreSQL Schema
--
-- UUID MIGRATION INFRASTRUCTURE:
--   SQLite uses INTEGER autoincrement IDs. The canonical schema uses UUID.
--   This temporary table maps legacy integer IDs to canonical UUIDs so
--   that all dependent foreign keys can resolve during data migration
--   (Phase 2C).
--
--   Mapping strategy:
--     legacy entity        legacy ID    canonical entity        canonical UUID
--     ─────────────       ────────     ──────────────         ──────────────
--     users.id             INTEGER      profiles.id             UUID
--     vocabulary_cards.id  INTEGER      vocab_cards.id          UUID
--     user_vocab_progress  INTEGER      vocab_progress.id       UUID
--     study_sessions.id    INTEGER      study_sessions.id       UUID
--     error_journal.id     INTEGER      error_journal.id        UUID
--     study_plans.id       INTEGER      study_plans.id          UUID
--     content_cache.id     INTEGER      content_cache.id        UUID
--
--   For profiles, the SQLite user must be linked to a Supabase auth user.
--   This requires creating auth users for existing desktop users (Phase 2C).
--
--   This table is TEMPORARY — it will be dropped after all data is
--   migrated and validated in Phase 2F.
--
-- Non-destructive: uses CREATE TABLE IF NOT EXISTS.

create table if not exists migration_id_map (
  id          uuid primary key default gen_random_uuid(),
  table_name  text not null,
  legacy_id   text not null,
  canonical_uuid uuid not null default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  unique (table_name, legacy_id)
);

create index if not exists idx_migration_id_map_lookup
  on migration_id_map (table_name, legacy_id);
