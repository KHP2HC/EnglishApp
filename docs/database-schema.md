# Canonical Database Schema — EnglishCoach Pro

> **Phase 2B** — Canonical PostgreSQL/Supabase schema and migration infrastructure.
> Implemented: 2026-08-31

---

## Overview

This document describes the canonical PostgreSQL/Supabase database schema
for EnglishCoach Pro. The schema is the **source of truth** for all
application data. SQLite remains available as a desktop offline cache
during the transition period.

### Design Principles

| Principle | Description |
|-----------|-------------|
| **UUID primary keys** | All tables use UUID v4 (`gen_random_uuid()`) |
| **Timezone-aware timestamps** | All timestamps use `TIMESTAMPTZ` |
| **Non-destructive migrations** | All migrations are additive (`CREATE IF NOT EXISTS`) |
| **RLS on user data** | Row Level Security on all user-owned tables |
| **Global content separation** | `vocab_cards` is publicly readable, not writable by anon |
| **Soft delete minimal** | Only `writing_submissions` has `deleted_at` |

---

## ER Diagram

```mermaid
erDiagram
    auth_users ||--o| profiles : "1:1"
    profiles ||--o{ vocab_progress : "user_id"
    profiles ||--o{ study_sessions : "user_id"
    profiles ||--o{ error_journal : "user_id"
    profiles ||--o{ study_plans : "user_id"
    profiles ||--o{ writing_submissions : "user_id"
    vocab_cards ||--o{ vocab_progress : "card_id"
    study_sessions ||--o{ error_journal : "session_id"

    profiles {
        uuid id PK "FK → auth.users.id"
        text name
        text avatar_emoji
        text target_exam
        numeric target_score
        numeric current_band
        jsonb skill_bands
        date exam_date
        jsonb free_time
        jsonb daily_schedule
        text session_time
        text theme_mode
        int streak_days
        int total_xp
        timestamptz last_active
        boolean onboarded
        timestamptz created_at
        timestamptz updated_at
    }

    vocab_cards {
        uuid id PK
        text word UK
        text phonetic
        text synonym
        text antonym
        text meaning_en
        text meaning_vi
        text example_sentence
        text audio_url
        text image_url
        text_array exam_type
        text cefr_level
        text category
        timestamptz created_at
    }

    vocab_progress {
        uuid id PK
        uuid user_id FK
        uuid card_id FK
        int interval_days
        numeric easiness
        int repetitions
        timestamptz next_review_at
        int last_quality
        int times_seen
        int times_correct
        timestamptz created_at
        timestamptz updated_at
    }

    study_sessions {
        uuid id PK
        uuid user_id FK
        timestamptz started_at
        timestamptz ended_at
        text session_type
        int xp_earned
        int items_total
        int items_correct
        timestamptz created_at
    }

    error_journal {
        uuid id PK
        uuid user_id FK
        uuid session_id FK
        text error_category
        text skill
        text question_snapshot
        text user_answer
        text correct_answer
        timestamptz created_at
    }

    study_plans {
        uuid id PK
        uuid user_id FK
        date week_start
        jsonb daily_tasks
        timestamptz created_at
        timestamptz updated_at
    }

    content_cache {
        uuid id PK
        text source
        text source_key
        text content_type
        text title
        text body
        jsonb payload
        text cefr_level
        text exam_type
        timestamptz fetched_at
        timestamptz expires_at
    }

    writing_submissions {
        uuid id PK
        uuid user_id FK
        text task_prompt
        text user_essay
        jsonb ai_feedback
        numeric band_estimate
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }

    migration_id_map {
        uuid id PK
        text table_name
        text legacy_id
        uuid canonical_uuid
        timestamptz created_at
    }
```

---

## Table Descriptions

### 1. profiles

User application profile. Linked 1:1 to `auth.users` via UUID.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID PK | No | — | FK → `auth.users(id) ON DELETE CASCADE` |
| `name` | TEXT | No | `''` | Display name |
| `avatar_emoji` | TEXT | Yes | `'🧑'` | |
| `target_exam` | TEXT | Yes | — | CHECK: TOEIC, IELTS, TOEFL, VSTEP |
| `target_score` | NUMERIC(4,1) | Yes | — | e.g. 7.5 for IELTS |
| `current_band` | NUMERIC(3,1) | Yes | — | From placement test |
| `skill_bands` | JSONB | Yes | `'{}'` | Per-skill band scores |
| `exam_date` | DATE | Yes | — | |
| `free_time` | JSONB | Yes | `{"mon":60,...}` | Minutes per day |
| `daily_schedule` | JSONB | Yes | `'{}'` | Granular time slots |
| `session_time` | TEXT | Yes | `'MORNING'` | CHECK: MORNING, AFTERNOON, EVENING |
| `theme_mode` | TEXT | Yes | `'dark'` | dark, light, system |
| `streak_days` | INT | Yes | `0` | CHECK: >= 0 |
| `total_xp` | INT | Yes | `0` | CHECK: >= 0 |
| `last_active` | TIMESTAMPTZ | Yes | — | |
| `onboarded` | BOOLEAN | Yes | `false` | |
| `created_at` | TIMESTAMPTZ | No | `now()` | Immutable |
| `updated_at` | TIMESTAMPTZ | No | `now()` | Trigger-managed |

**RLS**: `auth.uid() = id` (full CRUD for own profile only)

**Soft delete**: No — hard delete via `auth.users` cascade.

### 2. vocab_cards

Global vocabulary content. Shared across all users.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID PK | No | `gen_random_uuid()` | |
| `word` | TEXT | No | — | UNIQUE |
| `phonetic` | TEXT | Yes | — | IPA transcription |
| `synonym` | TEXT | Yes | — | Comma-separated |
| `antonym` | TEXT | Yes | — | Comma-separated |
| `meaning_en` | TEXT | No | — | |
| `meaning_vi` | TEXT | No | — | |
| `example_sentence` | TEXT | Yes | — | |
| `audio_url` | TEXT | Yes | — | |
| `image_url` | TEXT | Yes | — | |
| `exam_type` | TEXT[] | Yes | `'{}'` | Array of exam types |
| `cefr_level` | TEXT | Yes | — | CHECK: A1–C2 |
| `category` | TEXT | Yes | `'general'` | |
| `created_at` | TIMESTAMPTZ | No | `now()` | |

**Vocabulary uniqueness**: `UNIQUE(word)`. See [Vocabulary Uniqueness Strategy](#vocabulary-uniqueness-strategy).

**RLS**: Public read (`USING (true)`). No anon write policies.

**Soft delete**: No — global content is permanent.

### 3. vocab_progress

User's SRS (Spaced Repetition System) state per vocabulary card.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID PK | No | `gen_random_uuid()` | |
| `user_id` | UUID | No | — | FK → `profiles(id) ON DELETE CASCADE` |
| `card_id` | UUID | No | — | FK → `vocab_cards(id) ON DELETE CASCADE` |
| `interval_days` | INT | No | `1` | CHECK: >= 0 |
| `easiness` | NUMERIC(3,2) | No | `2.50` | CHECK: >= 1.30 |
| `repetitions` | INT | No | `0` | CHECK: >= 0 |
| `next_review_at` | TIMESTAMPTZ | Yes | — | See [SRS Timestamp Strategy](#srs-timestamp-strategy) |
| `last_quality` | INT | Yes | — | CHECK: 0–5 (SM-2 quality) |
| `times_seen` | INT | No | `0` | CHECK: >= 0 |
| `times_correct` | INT | No | `0` | CHECK: >= 0 |
| `created_at` | TIMESTAMPTZ | No | `now()` | Immutable |
| `updated_at` | TIMESTAMPTZ | No | `now()` | Trigger-managed |

**Unique constraint**: `(user_id, card_id)` — one progress row per user per card.

**RLS**: `auth.uid() = user_id` (full CRUD for own progress only).

**Soft delete**: No — cascade delete with user.

### 4. study_sessions

Immutable record of a study session.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID PK | No | `gen_random_uuid()` | |
| `user_id` | UUID | No | — | FK → `profiles(id) ON DELETE CASCADE` |
| `started_at` | TIMESTAMPTZ | No | `now()` | |
| `ended_at` | TIMESTAMPTZ | Yes | — | |
| `session_type` | TEXT | Yes | — | CHECK: VOCABULARY, GRAMMAR, LISTENING, READING, WRITING, SPEAKING, MOCK |
| `xp_earned` | INT | No | `0` | CHECK: >= 0 |
| `items_total` | INT | No | `0` | CHECK: >= 0 |
| `items_correct` | INT | No | `0` | CHECK: >= 0 |
| `created_at` | TIMESTAMPTZ | No | `now()` | Immutable |

**RLS**: `auth.uid() = user_id` (full CRUD for own sessions only).

**Soft delete**: No — immutable historical record. No `updated_at`.

### 5. error_journal

Log of user errors during study sessions.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID PK | No | `gen_random_uuid()` | |
| `user_id` | UUID | No | — | FK → `profiles(id) ON DELETE CASCADE` |
| `session_id` | UUID | Yes | — | FK → `study_sessions(id) ON DELETE SET NULL` |
| `error_category` | TEXT | Yes | — | |
| `skill` | TEXT | Yes | — | |
| `question_snapshot` | TEXT | Yes | — | |
| `user_answer` | TEXT | Yes | — | |
| `correct_answer` | TEXT | Yes | — | |
| `created_at` | TIMESTAMPTZ | No | `now()` | Immutable |

**RLS**: `auth.uid() = user_id` (full CRUD for own errors only).

**Soft delete**: No — immutable historical record. No `updated_at`.

### 6. study_plans

Weekly study plan. One row per user per week.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID PK | No | `gen_random_uuid()` | |
| `user_id` | UUID | No | — | FK → `profiles(id) ON DELETE CASCADE` |
| `week_start` | DATE | No | — | |
| `daily_tasks` | JSONB | No | `'{}'` | |
| `created_at` | TIMESTAMPTZ | No | `now()` | Immutable |
| `updated_at` | TIMESTAMPTZ | No | `now()` | Trigger-managed |

**Unique constraint**: `(user_id, week_start)` — one plan per user per week.

**RLS**: `auth.uid() = user_id` (full CRUD for own plans only).

**Soft delete**: No — old plans replaced by new ones (unique constraint).

### 7. content_cache

Cache for external API results (articles, reading materials).

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID PK | No | `gen_random_uuid()` | |
| `source` | TEXT | Yes | — | External API identifier |
| `source_key` | TEXT | Yes | — | Unique within source |
| `content_type` | TEXT | Yes | — | |
| `title` | TEXT | Yes | — | |
| `body` | TEXT | Yes | — | |
| `payload` | JSONB | Yes | — | Variable external response |
| `cefr_level` | TEXT | Yes | — | CHECK: A1–C2 |
| `exam_type` | TEXT | Yes | — | |
| `fetched_at` | TIMESTAMPTZ | No | `now()` | |
| `expires_at` | TIMESTAMPTZ | Yes | — | TTL-based invalidation |

**Unique constraint**: `(source, source_key)` — no duplicate cache entries.

**RLS**: Enabled, no policies — service-role only (backend content fetcher).

**Soft delete**: No — expired entries hard-deleted by cleanup job.

**Cache invalidation**: TTL-based. Entries with `expires_at < now()` are stale.
Application checks `expires_at` before using cached content. Periodic
cleanup job deletes stale rows.

### 8. writing_submissions

User's writing task submissions with AI feedback.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID PK | No | `gen_random_uuid()` | |
| `user_id` | UUID | No | — | FK → `profiles(id) ON DELETE CASCADE` |
| `task_prompt` | TEXT | Yes | — | |
| `user_essay` | TEXT | Yes | — | |
| `ai_feedback` | JSONB | Yes | — | |
| `band_estimate` | NUMERIC(3,1) | Yes | — | |
| `created_at` | TIMESTAMPTZ | No | `now()` | Immutable |
| `updated_at` | TIMESTAMPTZ | No | `now()` | Trigger-managed |
| `deleted_at` | TIMESTAMPTZ | Yes | — | Soft delete |

**RLS**: `auth.uid() = user_id` (full CRUD for own submissions only).

**Soft delete**: Yes — user can "delete" but data retained for analytics.

### 9. migration_id_map (temporary)

Maps legacy SQLite integer IDs to canonical UUIDs during migration.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID PK | No | `gen_random_uuid()` | |
| `table_name` | TEXT | No | — | Legacy table name |
| `legacy_id` | TEXT | No | — | Legacy integer ID (as text) |
| `canonical_uuid` | UUID | No | `gen_random_uuid()` | Canonical UUID |
| `created_at` | TIMESTAMPTZ | No | `now()` | |

**Unique constraint**: `(table_name, legacy_id)`.

**Dropped after migration is complete (Phase 2F).**

---

## Design Decisions

### Vocabulary Uniqueness Strategy

**Decision**: `UNIQUE(word)` — simple unique constraint on the `word` column.

**Rationale**: After inspecting the actual vocabulary dataset:
- 5,000 records in `vocab.json`, 5,251 in existing Supabase seed
- All words are unique (0 duplicates)
- Each word has exactly one `meaning_en`, one `meaning_vi`, one `exam_type`,
  one `difficulty_level` (CEFR), and one `category`
- No word appears with multiple meanings, parts of speech, or CEFR levels

A simple `UNIQUE(word)` constraint is justified by the actual data.
If multi-meaning words are needed in the future, a separate
`vocab_card_meanings` child table can be introduced without breaking
this schema.

The `exam_type` column is `TEXT[]` (array) for forward compatibility — a
word could appear in multiple exams in the future — but the unique
constraint is on `word` alone.

### SRS Timestamp Strategy

**Decision**: `next_review_at TIMESTAMPTZ` (not `next_review DATE`).

**Rationale**:
1. **Timezone-aware users**: A user in UTC+7 hitting "review" at 11pm
   local time would get a different "today" than a UTC user. TIMESTAMPTZ
   stores the exact intended review moment.
2. **Future reminder functionality**: Push notifications need an exact
   time, not just a date.
3. **Desktop offline operation**: When syncing from offline, the exact
   timestamp matters for conflict resolution.
4. **Synchronization**: LWW conflict resolution uses timestamps.

The application can still query by date using:
```sql
WHERE date_trunc('day', next_review_at) <= current_date
```

### Timestamp Semantics

| Field | Type | Semantics |
|-------|------|-----------|
| `created_at` | TIMESTAMPTZ | When the row was created. Set once by `DEFAULT now()`. Never updated. |
| `updated_at` | TIMESTAMPTZ | When the row was last modified. Updated by trigger (`set_updated_at()`). Clients cannot set this directly. |
| `deleted_at` | TIMESTAMPTZ | When the row was soft-deleted. NULL = not deleted. Set by application. |

**Tables with `updated_at`** (mutable): `profiles`, `vocab_progress`, `study_plans`, `writing_submissions`

**Tables without `updated_at`** (immutable): `vocab_cards`, `study_sessions`, `error_journal`, `content_cache`

### Soft Delete Semantics

| Table | Soft delete? | Reason |
|-------|---------------|--------|
| `profiles` | No | Hard delete via `auth.users` cascade |
| `vocab_cards` | No | Global content — permanent |
| `vocab_progress` | No | Cascade delete with user |
| `study_sessions` | No | Immutable historical record |
| `error_journal` | No | Immutable historical record |
| `study_plans` | No | Replaced by new plan (unique constraint) |
| `content_cache` | No | Expired rows purged by job |
| `writing_submissions` | **Yes** | User may "delete" but retain for analytics |

### UUID Strategy

All canonical tables use UUID v4 (`gen_random_uuid()`).

**`profiles.id`** = `auth.users.id` (linked 1:1 to Supabase Auth).

**Legacy SQLite → UUID mapping**: The `migration_id_map` table maps legacy
integer IDs to canonical UUIDs during Phase 2C data migration:

| Legacy entity | Legacy ID | Canonical entity | Canonical UUID |
|---------------|-----------|------------------|----------------|
| `users.id` | INTEGER | `profiles.id` | UUID |
| `vocabulary_cards.id` | INTEGER | `vocab_cards.id` | UUID |
| `user_vocab_progress.id` | INTEGER | `vocab_progress.id` | UUID |
| `study_sessions.id` | INTEGER | `study_sessions.id` | UUID |
| `error_journal.id` | INTEGER | `error_journal.id` | UUID |
| `study_plans.id` | INTEGER | `study_plans.id` | UUID |
| `content_cache.id` | INTEGER | `content_cache.id` | UUID |

### Cache Strategy

`content_cache` stores external API results. The application must NOT
depend on cached content being permanently available.

- **`source`**: Identifies the external API (e.g. `bbc`, `voa`)
- **`source_key`**: Unique identifier within the source (e.g. article URL hash)
- **`payload`**: JSONB — stores the full variable external response
- **`fetched_at`**: When the content was retrieved
- **`expires_at`**: When the cache entry becomes stale

**Invalidation**: TTL-based. `expires_at < now()` = stale. Periodic cleanup
job deletes stale rows. No soft delete — expired entries are hard-deleted.

---

## Constraints Summary

| Table | Constraint | Type |
|-------|-----------|------|
| `profiles` | `target_exam IN ('TOEIC','IELTS','TOEFL','VSTEP')` | CHECK |
| `profiles` | `session_time IN ('MORNING','AFTERNOON','EVENING')` | CHECK |
| `profiles` | `streak_days >= 0` | CHECK |
| `profiles` | `total_xp >= 0` | CHECK |
| `vocab_cards` | `word` | UNIQUE |
| `vocab_cards` | `cefr_level IN ('A1','A2','B1','B2','C1','C2')` | CHECK |
| `vocab_progress` | `(user_id, card_id)` | UNIQUE |
| `vocab_progress` | `interval_days >= 0` | CHECK |
| `vocab_progress` | `easiness >= 1.30` | CHECK |
| `vocab_progress` | `repetitions >= 0` | CHECK |
| `vocab_progress` | `last_quality >= 0 AND last_quality <= 5` | CHECK |
| `vocab_progress` | `times_seen >= 0` | CHECK |
| `vocab_progress` | `times_correct >= 0` | CHECK |
| `study_sessions` | `session_type IN (...)` | CHECK |
| `study_sessions` | `xp_earned >= 0` | CHECK |
| `study_sessions` | `items_total >= 0` | CHECK |
| `study_sessions` | `items_correct >= 0` | CHECK |
| `study_plans` | `(user_id, week_start)` | UNIQUE |
| `content_cache` | `(source, source_key)` | UNIQUE |
| `content_cache` | `cefr_level IN ('A1','A2','B1','B2','C1','C2')` | CHECK |
| `migration_id_map` | `(table_name, legacy_id)` | UNIQUE |

## Foreign Keys Summary

| Child table | Column | Parent table | ON DELETE |
|-------------|--------|--------------|-----------|
| `profiles` | `id` | `auth.users(id)` | CASCADE |
| `vocab_progress` | `user_id` | `profiles(id)` | CASCADE |
| `vocab_progress` | `card_id` | `vocab_cards(id)` | CASCADE |
| `study_sessions` | `user_id` | `profiles(id)` | CASCADE |
| `error_journal` | `user_id` | `profiles(id)` | CASCADE |
| `error_journal` | `session_id` | `study_sessions(id)` | SET NULL |
| `study_plans` | `user_id` | `profiles(id)` | CASCADE |
| `writing_submissions` | `user_id` | `profiles(id)` | CASCADE |

## Indexes Summary

| Index | Table | Columns | Purpose |
|-------|-------|---------|---------|
| `idx_profiles_created_at` | `profiles` | `created_at` | Sort by creation time |
| `idx_vocab_cards_word` | `vocab_cards` | `word` | Word search |
| `idx_vocab_cards_cefr` | `vocab_cards` | `cefr_level` | Filter by CEFR |
| `idx_vocab_cards_category` | `vocab_cards` | `category` | Filter by category |
| `idx_vocab_progress_user_review` | `vocab_progress` | `user_id, next_review_at` | Get due cards for user |
| `idx_study_sessions_user_started` | `study_sessions` | `user_id, started_at` | List sessions by date |
| `idx_error_journal_user_created` | `error_journal` | `user_id, created_at` | List recent errors |
| `idx_study_plans_user_week` | `study_plans` | `user_id, week_start` | Get plan for week |
| `idx_writing_submissions_user_created` | `writing_submissions` | `user_id, created_at` | List submissions |
| `idx_content_cache_source_expires` | `content_cache` | `source, expires_at` | Cache lookup + cleanup |
| `idx_content_cache_type` | `content_cache` | `content_type` | Filter by type |
| `idx_migration_id_map_lookup` | `migration_id_map` | `table_name, legacy_id` | ID mapping lookup |

## RLS Policies Summary

| Table | RLS | SELECT | INSERT | UPDATE | DELETE |
|-------|-----|--------|--------|--------|--------|
| `profiles` | ✅ | `auth.uid() = id` | `auth.uid() = id` | `auth.uid() = id` | `auth.uid() = id` |
| `vocab_cards` | ✅ | Public (`true`) | ❌ | ❌ | ❌ |
| `vocab_progress` | ✅ | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` |
| `study_sessions` | ✅ | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` |
| `error_journal` | ✅ | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` |
| `study_plans` | ✅ | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` |
| `content_cache` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `writing_submissions` | ✅ | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` |

> ❌ = no policy (blocked for non-service-role users)

---

## Migration Framework

### Approach

SQL migration files in `supabase/migrations/`, compatible with Supabase CLI
(`supabase db push`) and standalone PostgreSQL.

### Migration Order

| # | File | Description |
|---|------|-------------|
| 001 | `001_extensions.sql` | Enable pgcrypto, citext extensions |
| 002 | `002_profiles.sql` | profiles table + RLS |
| 003 | `003_vocab_cards.sql` | vocab_cards table + RLS |
| 004 | `004_vocab_progress.sql` | vocab_progress table + RLS |
| 005 | `005_study_sessions.sql` | study_sessions table + RLS |
| 006 | `006_error_journal.sql` | error_journal table + RLS |
| 007 | `007_study_plans.sql` | study_plans table + RLS |
| 008 | `008_content_cache.sql` | content_cache table + RLS |
| 009 | `009_writing_submissions.sql` | writing_submissions table + RLS |
| 010 | `010_triggers.sql` | updated_at triggers + auth signup trigger |
| 011 | `011_migration_id_map.sql` | UUID migration mapping table |

### Seed Data

| File | Description |
|------|-------------|
| `supabase/seeds/seed_vocab_cards.sql` | 5,000 vocabulary cards (idempotent) |
| `supabase/seeds/generate_seed.py` | Generator script (from `vocab_enriched.json`) |

Seed uses `ON CONFLICT (word) DO NOTHING` — safe to run multiple times.

### Running Migrations

```bash
# Local PostgreSQL
python supabase/run_migrations.py --database-url "postgresql://user:pass@localhost:5432/db"

# With seeds
python supabase/run_migrations.py --database-url "..." --with-seeds

# Supabase CLI
supabase db push
```

---

## SRS Storage Model

The schema stores the canonical SRS state as described in Phase 2A:

| SRS concept | Column | Type | Notes |
|-------------|--------|------|-------|
| Interval (days) | `interval_days` | INT | CHECK >= 0, default 1 |
| Easiness factor | `easiness` | NUMERIC(3,2) | CHECK >= 1.30, default 2.50 |
| Repetitions | `repetitions` | INT | CHECK >= 0, default 0 |
| Next review time | `next_review_at` | TIMESTAMPTZ | Timezone-aware |
| Last quality | `last_quality` | INT | CHECK 0–5 (SM-2) |
| Times seen | `times_seen` | INT | CHECK >= 0 |
| Times correct | `times_correct` | INT | CHECK >= 0 |

Business logic (SM-2 algorithm) lives in `core/srs_engine.py` (Python)
and `web/src/lib/srs.ts` (TypeScript). It is NOT duplicated in SQL.
The schema only stores the state; the application computes updates.
