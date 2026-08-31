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
