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
