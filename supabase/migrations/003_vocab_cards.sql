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
