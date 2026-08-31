# Database Migration Plan

Non-destructive migration from the current dual-database architecture
(SQLite + Supabase) to a single canonical PostgreSQL/Supabase schema.

> **Phase 2B Implementation Complete** — 2026-08-31
> See `docs/database-schema.md` for the full canonical schema reference.
> Migration files: `supabase/migrations/001–011`
> Seed data: `supabase/seeds/seed_vocab_cards.sql`
> Tests: `tests/database/` (207 tests)

---

## Current State

| Database | Used by | ID type | Schema |
|----------|---------|---------|--------|
| SQLite (`data.db`) | Desktop app, FastAPI | INTEGER autoincrement | `data/models.py` |
| Supabase (PostgreSQL) | React web app | UUID | `web/supabase/migrations/001_initial.sql` |

## Target State

| Database | Role | ID type |
|----------|------|---------|
| PostgreSQL/Supabase | **Source of truth** | UUID |
| SQLite (desktop) | **Offline cache** | UUID (mirrors Supabase) |

---

## Canonical Schema

### ID Strategy: UUID

**Recommendation: UUID v4 (random)**

Rationale:
- Supabase `auth.users.id` is already UUID — profiles must match.
- UUIDs are globally unique — essential for offline sync (desktop can
  generate IDs without collision risk).
- Supabase `gen_random_uuid()` generates UUID v4 by default.
- No need for UUID v7 (time-ordered) since all tables have `created_at`
  timestamps for ordering.

> **Note on UUID v7**: If chronological indexing becomes a performance
> concern in the future, UUID v7 (time-ordered) could be adopted. For
> now, UUID v4 + `created_at` index is sufficient and matches Supabase
> conventions.

### Timestamp Strategy

| Field | Type | Semantics |
|-------|------|-----------|
| `created_at` | `timestamptz` | When the row was created. Set once, never updated. |
| `updated_at` | `timestamptz` | When the row was last modified. Updated via trigger. |
| `deleted_at` | `timestamptz` | When the row was soft-deleted. NULL = not deleted. |

Rules:
- All timestamps are **timezone-aware** (`timestamptz`).
- `created_at` and `updated_at` are present on all user-owned tables.
- `deleted_at` is present only on tables that require soft delete.
- Desktop sync uses `updated_at` to detect changes and resolve conflicts
  (last-write-wins).

### Soft Delete Strategy

| Table | Soft delete? | Reason |
|-------|---------------|--------|
| `profiles` | No | Hard delete via `auth.users` cascade |
| `vocab_cards` | No | Global content — permanent |
| `vocab_progress` | No | User data — cascade delete with user |
| `study_sessions` | No | Immutable historical record |
| `error_journal` | No | Immutable historical record |
| `study_plans` | No | Replaced by new plan (unique constraint) |
| `writing_submissions` | Yes | User may "delete" a submission but keep for analytics |
| `content_cache` | No | Expired rows purged by job |

> Soft delete is minimal. Most user data is either immutable
> (sessions, errors) or cascade-deleted with the user. Only
> `writing_submissions` benefits from soft delete.

---

## Canonical Table Definitions

### profiles

```sql
create table profiles (
  id              uuid primary key references auth.users(id) on delete cascade,
  name            text not null default '',
  avatar_emoji    text default '🧑',
  target_exam     text check (target_exam in ('TOEIC','IELTS','TOEFL','VSTEP')),
  target_score    numeric(4,1),
  current_band    numeric(3,1),
  skill_bands     jsonb default '{}'::jsonb,
  exam_date       date,
  free_time       jsonb default '{"mon":60,"tue":60,"wed":60,"thu":60,"fri":60,"sat":120,"sun":120}'::jsonb,
  daily_schedule  jsonb default '{}'::jsonb,
  session_time    text check (session_time in ('MORNING','AFTERNOON','EVENING')) default 'MORNING',
  theme_mode      text default 'dark',
  streak_days     int default 0,
  total_xp        int default 0,
  last_active     timestamptz,
  onboarded       boolean default false,
  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);
```

Changes from current Supabase:
- `last_active` → `timestamptz` (was `date`)
- Added `daily_schedule` (from SQLite)
- Added `theme_mode` (from SQLite)
- Added `updated_at`

### vocab_cards

```sql
create table vocab_cards (
  id               uuid primary key default gen_random_uuid(),
  word             text not null unique,
  phonetic         text,
  synonym          text,
  antonym          text,
  meaning_en       text not null,
  meaning_vi       text not null,
  example_sentence text,
  audio_url        text,
  image_url        text,
  exam_type        text[] default '{}',
  cefr_level       text check (cefr_level in ('A1','A2','B1','B2','C1','C2')),
  category         text default 'general',
  created_at       timestamptz default now()
);
```

Changes from current Supabase:
- Added `unique` constraint on `word`
- Added `synonym`, `antonym`, `image_url` (from SQLite)

### vocab_progress

```sql
create table vocab_progress (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references profiles(id) on delete cascade,
  card_id        uuid not null references vocab_cards(id),
  interval_days  int default 1,
  easiness       numeric(3,2) default 2.5,
  repetitions    int default 0,
  next_review    date default current_date,
  last_quality   int,
  times_seen     int default 0,
  times_correct  int default 0,
  created_at     timestamptz default now(),
  updated_at     timestamptz default now(),
  unique (user_id, card_id)
);
```

Changes: Added `created_at`, `updated_at`. Field names follow Supabase
convention (`interval_days`, `easiness`, `repetitions`, `next_review`).

### study_sessions

```sql
create table study_sessions (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references profiles(id) on delete cascade,
  started_at    timestamptz default now(),
  ended_at      timestamptz,
  session_type  text check (session_type in
                ('VOCABULARY','GRAMMAR','LISTENING','READING','WRITING','SPEAKING','MOCK')),
  xp_earned     int default 0,
  items_total   int default 0,
  items_correct int default 0,
  created_at    timestamptz default now()
);
```

Changes: Uses `items_total` (Supabase name). Dropped `score` (derived).

### error_journal

```sql
create table error_journal (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null references profiles(id) on delete cascade,
  session_id        uuid references study_sessions(id),
  error_category   text,
  skill             text,
  question_snapshot text,
  user_answer       text,
  correct_answer    text,
  created_at        timestamptz default now()
);
```

Changes: Added `skill` (from Supabase). Dropped `content` (redundant).

### study_plans

```sql
create table study_plans (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references profiles(id) on delete cascade,
  week_start  date not null,
  daily_tasks jsonb not null default '{}'::jsonb,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now(),
  unique (user_id, week_start)
);
```

Changes: Dropped `plan` column (use per-week rows). Added `updated_at`.

### content_cache

```sql
create table content_cache (
  id            uuid primary key default gen_random_uuid(),
  content_type  text,
  source_url    text,
  title         text,
  body          text,
  cefr_level    text,
  exam_type     text,
  fetched_at    timestamptz default now(),
  expires_at    timestamptz default now() + interval '7 days'
);
```

Changes: `difficulty_level` → `cefr_level` (name unified).

### writing_submissions

```sql
create table writing_submissions (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references profiles(id) on delete cascade,
  task_prompt   text,
  user_essay    text,
  ai_feedback   jsonb,
  band_estimate numeric(3,1),
  created_at    timestamptz default now(),
  updated_at    timestamptz default now(),
  deleted_at    timestamptz
);
```

Changes: Added `updated_at`, `deleted_at` (soft delete).

---

## Legacy Mapping

### SQLite → Canonical

| SQLite table | Canonical table | Transformations |
|--------------|-----------------|-----------------|
| `users` | `profiles` | `id` INT→UUID, `daily_free_minutes`→`free_time`, `preferred_session_time`→`session_time`, add `skill_bands`/`onboarded` |
| `vocabulary_cards` | `vocab_cards` | `id` INT→UUID, `difficulty_level`→`cefr_level`, `exam_type` enum→text[], add `created_at` |
| `user_vocab_progress` | `vocab_progress` | `id` INT→UUID, `srs_interval`→`interval_days`, `srs_easiness`→`easiness`, `srs_repetitions`→`repetitions`, `next_review_date`→`next_review` |
| `study_sessions` | `study_sessions` | `id` INT→UUID, `items_studied`→`items_total`, drop `score` |
| `error_journal` | `error_journal` | `id` INT→UUID, add `skill`, drop `content` |
| `study_plans` | `study_plans` | `id` INT→UUID, drop `plan`, add unique `(user_id, week_start)` |
| `content_cache` | `content_cache` | `id` INT→UUID, `difficulty_level`→`cefr_level` |

### Supabase → Canonical

| Supabase table | Canonical table | Transformations |
|----------------|-----------------|-----------------|
| `profiles` | `profiles` | `last_active` date→timestamptz, add `daily_schedule`/`theme_mode`/`updated_at` |
| `vocab_cards` | `vocab_cards` | add `unique(word)`, add `synonym`/`antonym`/`image_url` |
| `vocab_progress` | `vocab_progress` | add `created_at`/`updated_at` |
| `study_sessions` | `study_sessions` | add `created_at` |
| `error_journal` | `error_journal` | none (already matches) |
| `study_plans` | `study_plans` | add `updated_at` |
| `content_cache` | `content_cache` | `cefr_level` already correct |
| `writing_submissions` | `writing_submissions` | add `updated_at`/`deleted_at` |

### Column Name Mapping (critical)

| SQLite name | Supabase name | Canonical name | Reason |
|--------------|----------------|----------------|--------|
| `daily_free_minutes` | `free_time` | `free_time` | Supabase name is cleaner |
| `preferred_session_time` | `session_time` | `session_time` | Supabase name is cleaner |
| `difficulty_level` | `cefr_level` | `cefr_level` | CEFR is the standard term |
| `srs_interval` | `interval_days` | `interval_days` | Supabase name is clearer |
| `srs_easiness` | `easiness` | `easiness` | Drop redundant prefix |
| `srs_repetitions` | `repetitions` | `repetitions` | Drop redundant prefix |
| `next_review_date` | `next_review` | `next_review_at` | TIMESTAMPTZ for timezone awareness |
| `items_studied` | `items_total` | `items_total` | "total" is more precise |

---

## Migration Strategy

```
Phase 2A (complete): Design only — no changes to databases
         │
Phase 2B (COMPLETE): Create canonical schema in Supabase (additive only)
         │  ✅ 11 migration files (001–011) in supabase/migrations/
         │  ✅ 8 canonical tables + migration_id_map
         │  ✅ RLS policies on all user-owned tables
         │  ✅ updated_at triggers on mutable tables
         │  ✅ Idempotent seed data (5,000 vocab cards)
         │  ✅ 207 database tests (schema, RLS, data validation)
         │  ✅ Existing 64 tests still pass (64/64)
         │  ✅ Documentation: docs/database-schema.md
         │
Phase 2C (next): Migrate SQLite data → Supabase
         │  - Read SQLite rows
         │  - Transform (rename columns, convert IDs)
         │  - Generate UUIDs for SQLite records (maintain mapping table)
         │  - Insert into canonical Supabase tables
         │  - Validate (row counts, FK integrity)
         │
Phase 2D: Dual-read period
         │  - FastAPI reads from Supabase (canonical)
         │  - Desktop reads from SQLite (cache) with fallback to API
         │  - React reads from FastAPI
         │
Phase 2E: Migrate clients to FastAPI
         │  - React → FastAPI (remove direct Supabase calls)
         │  - Desktop → FastAPI (remove direct SQLite access)
         │
Phase 2F: Remove legacy access
            - Drop legacy columns from Supabase
            - SQLite becomes read-only cache (sync from API)
```

### ID Migration

SQLite uses INTEGER autoincrement. Supabase uses UUID. A mapping table
is needed during migration:

```sql
-- Implemented in supabase/migrations/011_migration_id_map.sql
create table if not exists migration_id_map (
  id              uuid primary key default gen_random_uuid(),
  table_name      text not null,
  legacy_id       text not null,
  canonical_uuid  uuid not null default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  unique (table_name, legacy_id)
);
```

For `profiles`, the SQLite user must be linked to a Supabase auth user.
Options:
1. Create auth users for existing desktop users (requires email).
2. Use a service-role migration script to create auth users.

---

## Non-Destructive Principles

1. **Never DROP tables** during migration.
2. **Never DELETE rows** from the source database.
3. **Never rename columns** in-place — add new column, backfill, then
   drop old column only after all clients are migrated.
4. **Always use `IF NOT EXISTS`** for new tables and columns.
5. **Always backup** before running migrations.
6. **Validate after each step** (see `database-validation-plan.md`).

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ID collision during migration | High | Use UUID mapping table; validate no duplicates |
| Data loss from column rename | High | Additive migration; never rename in-place |
| Sync conflicts (offline desktop) | Medium | Last-write-wins on `updated_at`; conflict resolution in Phase 2F |
| Divergent business logic | Medium | Unify in FastAPI before migrating clients (see `business-logic-migration.md`) |
| RLS misconfiguration | High | Test RLS policies before enabling; use service-role for migration only |
| Large vocab_cards table (5,251 rows) | Low | Batch insert; idempotent with `ON CONFLICT DO NOTHING` |

---

## Estimated Complexity

| Phase | Complexity | Estimated effort |
|-------|------------|-----------------|
| 2A (design) | Low | Done |
| 2B (schema) | Medium | Done (2026-08-31) |
| 2C (data migration) | High | 2–3 days |
| 2D (dual-read) | Medium | 2–3 days |
| 2E (client migration) | High | 5–7 days |
| 2F (cleanup) | Low | 1 day |

---

## Phase 2B Implementation Details

### Files Created

| File | Description |
|------|-------------|
| `supabase/migrations/001_extensions.sql` | pgcrypto + citext extensions |
| `supabase/migrations/002_profiles.sql` | profiles table + RLS |
| `supabase/migrations/003_vocab_cards.sql` | vocab_cards table + RLS |
| `supabase/migrations/004_vocab_progress.sql` | vocab_progress table + RLS |
| `supabase/migrations/005_study_sessions.sql` | study_sessions table + RLS |
| `supabase/migrations/006_error_journal.sql` | error_journal table + RLS |
| `supabase/migrations/007_study_plans.sql` | study_plans table + RLS |
| `supabase/migrations/008_content_cache.sql` | content_cache table + RLS |
| `supabase/migrations/009_writing_submissions.sql` | writing_submissions table + RLS |
| `supabase/migrations/010_triggers.sql` | updated_at + auth signup triggers |
| `supabase/migrations/011_migration_id_map.sql` | UUID migration mapping table |
| `supabase/seeds/generate_seed.py` | Seed SQL generator |
| `supabase/seeds/seed_vocab_cards.sql` | 5,000 idempotent vocab seed |
| `supabase/run_migrations.py` | Local migration runner |
| `tests/database/__init__.py` | Test package |
| `tests/database/test_schema_migrations.py` | Schema migration tests |
| `tests/database/test_rls_security.py` | RLS security tests |
| `tests/database/test_data_validation.py` | Data validation tests |
| `docs/database-schema.md` | Full schema documentation |

### Design Decisions Implemented

1. **Vocabulary uniqueness**: `UNIQUE(word)` — justified by data analysis
   (all 5,000 words are unique, each with single meaning/exam/level)
2. **SRS timestamp**: `next_review_at TIMESTAMPTZ` (not `DATE`) — for
   timezone awareness, future reminders, and sync conflict resolution
3. **Content cache**: `source`, `source_key`, `payload` (JSONB),
   `fetched_at`, `expires_at` — TTL-based invalidation
4. **Soft delete**: Only `writing_submissions` has `deleted_at`
5. **UUID primary keys**: All tables use `gen_random_uuid()`
6. **Timestamps**: All `TIMESTAMPTZ`, `updated_at` managed by triggers
7. **RLS**: All user-owned tables use `auth.uid() = user_id`;
   `vocab_cards` is public read only; `content_cache` is service-role only

### Test Results

| Test suite | Count | Status |
|------------|-------|--------|
| Existing tests | 64 | ✅ All pass |
| New schema migration tests | 96 | ✅ All pass |
| New RLS security tests | 30 | ✅ All pass |
| New data validation tests | 81 | ✅ All pass |
| **Total** | **271** | ✅ All pass |
