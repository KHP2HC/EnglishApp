# Database Audit — EnglishCoach Pro

## Overview

EnglishCoach Pro uses **two separate database systems** that represent the same domain model but with different schemas, different ID types, and different table structures.

| Aspect | Desktop | Web |
|--------|---------|-----|
| Database engine | SQLite (file: `data.db`) | Supabase (PostgreSQL) |
| ORM | SQLAlchemy 2.0 | Supabase JS client (direct table access) |
| Migrations | `migrate_schema()` in `data/database.py` | SQL files in `web/supabase/migrations/` |
| ID type | Integer (auto-increment) | UUID |
| Auth | No authentication | Supabase Auth (auth.users) |

---

## 1. SQLite Schema (Desktop)

### Tables

#### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | Auto-increment |
| name | String(50) | Not null |
| avatar_emoji | String(4) | Default "😊" |
| created_at | DateTime | Default utcnow |
| target_exam | Enum(TOEIC/IELTS/TOEFL/VSTEP) | |
| target_score | Float | e.g. 7.5 |
| current_band | Float | From placement test |
| exam_date | Date | |
| daily_free_minutes | JSON | `{"mon": 60, ...}` |
| daily_schedule | JSON | `{"mon": {"morning": 30, ...}}` |
| preferred_session_time | String(10) | MORNING/AFTERNOON/EVENING |
| theme_mode | String(20) | Default "dark" |
| streak_days | Integer | Default 0 |
| total_xp | Integer | Default 0 |
| last_active | DateTime | Default utcnow |

**Missing**: No `password_hash`, no `email`, no `auth_provider`. Single-user, no authentication.

#### `vocabulary_cards`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | Auto-increment |
| word | String(100) | Unique, not null |
| phonetic | String(50) | |
| synonym | String(100) | Added via migration |
| antonym | String(100) | Added via migration |
| meaning_en | Text | |
| meaning_vi | Text | |
| example_sentence | Text | |
| audio_url | String(200) | |
| image_url | String(200) | |
| exam_type | Enum(ExamType) | Single enum, not array |
| difficulty_level | Enum(BandLevel) | A1–C2 |
| category | String(50) | |

**Missing**: No `cefr_level` column (uses `difficulty_level` instead).

#### `user_vocab_progress`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| user_id | Integer FK → users.id | |
| card_id | Integer FK → vocabulary_cards.id | |
| srs_interval | Integer | Default 1 |
| srs_easiness | Float | Default 2.5 |
| srs_repetitions | Integer | Default 0 |
| next_review_date | Date | |
| last_quality | Integer | 0–5 |
| times_seen | Integer | Default 0 |
| times_correct | Integer | Default 0 |

**Missing**: No unique constraint on `(user_id, card_id)`.

#### `study_sessions`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| user_id | Integer FK → users.id | |
| session_type | Enum(SessionType) | |
| started_at | DateTime | |
| ended_at | DateTime | |
| score | Float | |
| xp_earned | Integer | Added via migration |
| items_studied | Integer | Added via migration |
| items_correct | Integer | Added via migration |

#### `error_journal`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| user_id | Integer FK → users.id | |
| session_id | Integer FK → study_sessions.id | |
| error_category | String(100) | |
| question_snapshot | Text | |
| user_answer | Text | |
| correct_answer | Text | |
| content | Text | |
| created_at | DateTime | |

**Missing**: No `skill` column (present in Supabase schema).

#### `study_plans`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| user_id | Integer FK → users.id | |
| week_start | Date | Added via migration |
| daily_tasks | JSON | Added via migration |
| plan | JSON | |
| created_at | DateTime | |

#### `content_cache`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| content_type | String(50) | |
| source_url | String(500) | |
| title | String(300) | |
| body | Text | |
| difficulty_level | String(20) | |
| fetched_at | DateTime | |
| expires_at | DateTime | |

**Missing**: No `exam_type` column (present in Supabase schema).

---

## 2. Supabase Schema (Web)

### Tables

#### `profiles`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK → auth.users.id | Supabase Auth |
| name | text | |
| avatar_emoji | text | |
| target_exam | text | CHECK constraint |
| target_score | numeric(4,1) | |
| current_band | numeric(3,1) | |
| skill_bands | jsonb | **Not in SQLite** |
| exam_date | date | |
| free_time | jsonb | Named `daily_free_minutes` in SQLite |
| session_time | text | Named `preferred_session_time` in SQLite |
| streak_days | int | |
| total_xp | int | |
| last_active | date | DateTime in SQLite |
| onboarded | boolean | **Not in SQLite** |
| created_at | timestamptz | |

**RLS**: Enabled. Policy: `auth.uid() = id`.

#### `vocab_cards`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| word | text | |
| phonetic | text | |
| meaning_en | text | |
| meaning_vi | text | |
| example_sentence | text | |
| audio_url | text | |
| exam_type | text[] | **Array** (single enum in SQLite) |
| cefr_level | text | Named `difficulty_level` in SQLite |
| category | text | |
| created_at | timestamptz | |

**Missing**: No `synonym`, `antonym`, `image_url` columns (present in SQLite).

#### `vocab_progress`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → profiles.id | |
| card_id | UUID FK → vocab_cards.id | |
| interval_days | int | Named `srs_interval` in SQLite |
| easiness | numeric(3,2) | Named `srs_easiness` in SQLite |
| repetitions | int | Named `srs_repetitions` in SQLite |
| next_review | date | Named `next_review_date` in SQLite |
| last_quality | int | |
| times_seen | int | |
| times_correct | int | |

**Constraint**: `UNIQUE(user_id, card_id)` — **missing in SQLite**.

**RLS**: Enabled. Policy: `auth.uid() = user_id`.

#### `study_sessions`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → profiles.id | |
| started_at | timestamptz | |
| ended_at | timestamptz | |
| session_type | text | CHECK constraint |
| xp_earned | int | |
| items_total | int | Named `items_studied` in SQLite |
| items_correct | int | |

**RLS**: Enabled. Policy: `auth.uid() = user_id`.

#### `error_journal`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → profiles.id | |
| session_id | UUID FK → study_sessions.id | |
| error_category | text | |
| skill | text | **Not in SQLite** |
| question_snapshot | text | |
| user_answer | text | |
| correct_answer | text | |
| created_at | timestamptz | |

**RLS**: Enabled. Policy: `auth.uid() = user_id`.

#### `study_plans`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → profiles.id | |
| week_start | date | |
| daily_tasks | jsonb | |
| created_at | timestamptz | |

**Constraint**: `UNIQUE(user_id, week_start)` — **missing in SQLite**.

**RLS**: Enabled. Policy: `auth.uid() = user_id`.

#### `content_cache`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| content_type | text | |
| source_url | text | |
| title | text | |
| body | text | |
| cefr_level | text | Named `difficulty_level` in SQLite |
| exam_type | text | **Not in SQLite** |
| fetched_at | timestamptz | |
| expires_at | timestamptz | |

#### `writing_submissions`
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → profiles.id | |
| task_prompt | text | |
| user_essay | text | |
| ai_feedback | jsonb | |
| band_estimate | numeric(3,1) | |
| created_at | timestamptz | |

**RLS**: Not explicitly enabled in migration.

---

## 3. Schema Divergence Summary

| Concept | SQLite (Desktop) | Supabase (Web) | Divergence |
|---------|-----------------|----------------|------------|
| User ID | Integer | UUID | **Critical** |
| User table name | `users` | `profiles` | **Critical** |
| Auth | None | Supabase Auth | **Critical** |
| Exam type (vocab) | Single Enum | Text array | **High** |
| CEFR field name | `difficulty_level` (Enum) | `cefr_level` (text) | **High** |
| Free time field | `daily_free_minutes` | `free_time` | **Medium** |
| Session time field | `preferred_session_time` | `session_time` | **Medium** |
| SRS interval field | `srs_interval` | `interval_days` | **Medium** |
| SRS easiness field | `srs_easiness` | `easiness` | **Medium** |
| SRS repetitions field | `srs_repetitions` | `repetitions` | **Medium** |
| Next review field | `next_review_date` | `next_review` | **Medium** |
| Items studied field | `items_studied` | `items_total` | **Medium** |
| `skill_bands` | Missing | jsonb | **Medium** |
| `onboarded` | Missing | boolean | **Low** |
| `synonym`/`antonym` (vocab) | Present | Missing | **Low** |
| `image_url` (vocab) | Present | Missing | **Low** |
| `skill` (error_journal) | Missing | Present | **Low** |
| `exam_type` (content_cache) | Missing | Present | **Low** |
| `writing_submissions` | Missing | Present | **Medium** |
| Unique constraints | Missing | Present | **High** |
| RLS | N/A | Enabled (except writing_submissions) | **N/A** |

---

## 4. Migration Strategy

### Current State
- `migrate_schema()` in `data/database.py` uses `ALTER TABLE` to add columns incrementally
- Supabase migrations are raw SQL files run manually
- No migration versioning or rollback capability
- No shared schema definition between desktop and web

### Risks
- Schema drift between SQLite and Supabase will worsen over time
- No way to guarantee both databases represent the same domain model
- Desktop users cannot sync with web users
- No migration rollback if a migration breaks something

### Recommendations
1. **Define a canonical domain model** (Phase 2) that both databases derive from
2. **Use Alembic** for SQLite migrations (replacing `migrate_schema()`)
3. **Use Supabase migration files** with proper versioning
4. **Generate TypeScript types** from the canonical model
5. **Add missing constraints** (unique, foreign keys) to SQLite
