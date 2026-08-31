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
