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
