# Database Model Inventory

Complete inventory of every table/entity in the current system, covering
both the SQLite (desktop) and Supabase/PostgreSQL (web) databases.

---

## 1. profiles / users

| Aspect | SQLite (`users`) | Supabase (`profiles`) |
|--------|-------------------|------------------------|
| **Purpose** | Desktop user profile + settings | Web user profile (linked to `auth.users`) |
| **Primary key** | `id` INTEGER autoincrement | `id` UUID (FK → `auth.users.id`) |
| **Consumers** | Desktop app, FastAPI (legacy) | React web app, Supabase Auth |

### Columns

| Canonical concept | SQLite column | Supabase column | Type (SQLite) | Type (Supabase) | Nullable | Notes |
|---|---|---|---|---|---|---|
| User ID | `id` | `id` | INTEGER PK | UUID PK | No | SQLite: autoincrement int; Supabase: auth user UUID |
| Display name | `name` | `name` | VARCHAR(50) | TEXT | No | |
| Avatar | `avatar_emoji` | `avatar_emoji` | VARCHAR(4) | TEXT | Yes | Default: SQLite `😊`, Supabase `🧑` |
| Target exam | `target_exam` | `target_exam` | Enum(TOEIC,IELTS,TOEFL,VSTEP) | TEXT CHECK | Yes | SQLite stores enum name; Supabase stores string |
| Target score | `target_score` | `target_score` | FLOAT | NUMERIC(4,1) | Yes | e.g. 7.5 for IELTS |
| Current band | `current_band` | `current_band` | FLOAT | NUMERIC(3,1) | Yes | From placement test |
| Skill bands | — | `skill_bands` | — | JSONB | Yes | Per-skill band scores (Supabase only) |
| Exam date | `exam_date` | `exam_date` | DATE | DATE | Yes | |
| Free time | `daily_free_minutes` | `free_time` | JSON | JSONB | Yes | `{"mon":60,"tue":60,...}` |
| Daily schedule | `daily_schedule` | — | JSON | — | Yes | Granular slots `{"mon":{"morning":30,...}}` (SQLite only) |
| Preferred time | `preferred_session_time` | `session_time` | VARCHAR(10) | TEXT CHECK | Yes | SQLite: free text; Supabase: CHECK in (MORNING,AFTERNOON,EVENING) |
| Theme | `theme_mode` | — | VARCHAR(20) | — | Yes | dark/light/system (SQLite only) |
| Streak | `streak_days` | `streak_days` | INTEGER | INT | Yes | Default 0 |
| Total XP | `total_xp` | `total_xp` | INTEGER | INT | Yes | Default 0 |
| Last active | `last_active` | `last_active` | DATETIME | DATE | Yes | SQLite: timestamp; Supabase: date only |
| Onboarded | — | `onboarded` | — | BOOLEAN | Yes | Supabase only, default false |
| Created at | `created_at` | `created_at` | DATETIME | TIMESTAMPTZ | Yes | SQLite: `utcnow()`; Supabase: `now()` |

### Relationships

- `users.id` ← `user_vocab_progress.user_id` (1:N)
- `users.id` ← `study_sessions.user_id` (1:N)
- `users.id` ← `error_journal.user_id` (1:N)
- `users.id` ← `study_plans.user_id` (1:N)

### Migration notes

- **ID type change**: INTEGER → UUID (critical)
- `daily_free_minutes` → `free_time` (rename)
- `preferred_session_time` → `session_time` (rename + CHECK constraint)
- `daily_schedule` has no Supabase equivalent (merge into `free_time` or add column)
- `theme_mode` has no Supabase equivalent (add as user preference)
- `skill_bands` has no SQLite equivalent (add column)
- `onboarded` has no SQLite equivalent (add column)
- `last_active` type mismatch: DATETIME → DATE (Supabase) — recommend TIMESTAMPTZ

---

## 2. vocabulary_cards / vocab_cards

| Aspect | SQLite (`vocabulary_cards`) | Supabase (`vocab_cards`) |
|--------|------------------------------|---------------------------|
| **Purpose** | Global vocabulary content (shared) | Global vocabulary content (shared) |
| **Primary key** | `id` INTEGER autoincrement | `id` UUID (`gen_random_uuid()`) |
| **Unique** | `word` | — (no unique constraint on `word`) |
| **Consumers** | Desktop app, FastAPI | React web app |

### Columns

| Canonical concept | SQLite column | Supabase column | Type (SQLite) | Type (Supabase) | Nullable | Notes |
|---|---|---|---|---|---|---|
| ID | `id` | `id` | INTEGER PK | UUID PK | No | |
| Word | `word` | `word` | VARCHAR(100) UNIQUE | TEXT | No | SQLite enforces uniqueness |
| Phonetic | `phonetic` | `phonetic` | VARCHAR(50) | TEXT | Yes | |
| Synonym | `synonym` | — | VARCHAR(100) | — | Yes | SQLite only (enrichment) |
| Antonym | `antonym` | — | VARCHAR(100) | — | Yes | SQLite only (enrichment) |
| Meaning (EN) | `meaning_en` | `meaning_en` | TEXT | TEXT | No | Supabase: NOT NULL |
| Meaning (VI) | `meaning_vi` | `meaning_vi` | TEXT | TEXT | No | Supabase: NOT NULL |
| Example | `example_sentence` | `example_sentence` | TEXT | TEXT | Yes | |
| Audio URL | `audio_url` | `audio_url` | VARCHAR(200) | TEXT | Yes | |
| Image URL | `image_url` | — | VARCHAR(200) | — | Yes | SQLite only |
| Exam type | `exam_type` | `exam_type` | Enum(ExamType) | TEXT[] | Yes | SQLite: single enum; Supabase: array of strings |
| Difficulty | `difficulty_level` | `cefr_level` | Enum(BandLevel) | TEXT CHECK | Yes | SQLite: A1–C2 enum; Supabase: A1–C2 CHECK |
| Category | `category` | `category` | VARCHAR(50) | TEXT | Yes | Default: SQLite none, Supabase `general` |
| Created at | — | `created_at` | — | TIMESTAMPTZ | Yes | Supabase only |

### Migration notes

- **ID type change**: INTEGER → UUID
- `difficulty_level` → `cefr_level` (rename, same domain)
- `exam_type`: single enum → array (Supabase supports multi-exam)
- `synonym`, `antonym`, `image_url` missing from Supabase (add columns)
- `meaning_en`, `meaning_vi` are NOT NULL in Supabase but nullable in SQLite
- Add unique constraint on `word` in Supabase (currently missing)
- Add `created_at` to SQLite schema

---

## 3. user_vocab_progress / vocab_progress

| Aspect | SQLite (`user_vocab_progress`) | Supabase (`vocab_progress`) |
|--------|----------------------------------|------------------------------|
| **Purpose** | User's SRS state per vocabulary card | User's SRS state per vocabulary card |
| **Primary key** | `id` INTEGER autoincrement | `id` UUID |
| **Unique** | — | `(user_id, card_id)` |
| **Consumers** | Desktop app, FastAPI | React web app |

### Columns

| Canonical concept | SQLite column | Supabase column | Type (SQLite) | Type (Supabase) | Nullable | Notes |
|---|---|---|---|---|---|---|
| ID | `id` | `id` | INTEGER PK | UUID PK | No | |
| User ID | `user_id` | `user_id` | INTEGER FK→users | UUID FK→profiles | No | |
| Card ID | `card_id` | `card_id` | INTEGER FK→vocabulary_cards | UUID FK→vocab_cards | No | |
| SRS interval | `srs_interval` | `interval_days` | INTEGER (days) | INT (days) | No | Default 1. **Name divergence** |
| SRS easiness | `srs_easiness` | `easiness` | FLOAT | NUMERIC(3,2) | No | Default 2.5. **Name divergence** |
| SRS repetitions | `srs_repetitions` | `repetitions` | INTEGER | INT | No | Default 0. **Name divergence** |
| Next review | `next_review_date` | `next_review` | DATE | DATE | Yes | Default: SQLite none, Supabase `current_date`. **Name divergence** |
| Last quality | `last_quality` | `last_quality` | INTEGER | INT | Yes | 0–5 SM-2 quality |
| Times seen | `times_seen` | `times_seen` | INTEGER | INT | No | Default 0 |
| Times correct | `times_correct` | `times_correct` | INTEGER | INT | No | Default 0 |

### Migration notes

- **ID type change**: INTEGER → UUID
- **Field renames**: `srs_interval`→`interval_days`, `srs_easiness`→`easiness`, `srs_repetitions`→`repetitions`, `next_review_date`→`next_review`
- Add unique constraint `(user_id, card_id)` to SQLite (currently missing)
- `easiness` precision: FLOAT → NUMERIC(3,2) (Supabase rounds to 2 decimals)

---

## 4. study_sessions

| Aspect | SQLite (`study_sessions`) | Supabase (`study_sessions`) |
|--------|---------------------------|------------------------------|
| **Purpose** | Record of a study session | Record of a study session |
| **Primary key** | `id` INTEGER | `id` UUID |
| **Consumers** | Desktop app, FastAPI | React web app |

### Columns

| Canonical concept | SQLite column | Supabase column | Type (SQLite) | Type (Supabase) | Nullable | Notes |
|---|---|---|---|---|---|---|
| ID | `id` | `id` | INTEGER PK | UUID PK | No | |
| User ID | `user_id` | `user_id` | INTEGER FK→users | UUID FK→profiles | No | |
| Started at | `started_at` | `started_at` | DATETIME | TIMESTAMPTZ | No | |
| Ended at | `ended_at` | `ended_at` | DATETIME | TIMESTAMPTZ | Yes | |
| Session type | `session_type` | `session_type` | Enum(SessionType) | TEXT CHECK | Yes | Same domain, different storage |
| Score | `score` | — | FLOAT | — | Yes | SQLite only (derived: correct/studied) |
| XP earned | `xp_earned` | `xp_earned` | INTEGER | INT | No | Default 0 |
| Items studied | `items_studied` | `items_total` | INTEGER | INT | No | **Name divergence** |
| Items correct | `items_correct` | `items_correct` | INTEGER | INT | No | Default 0 |

### Migration notes

- **ID type change**: INTEGER → UUID
- `items_studied` → `items_total` (name divergence)
- `score` missing from Supabase (derived value — recommend NOT adding; compute on read)
- `session_type`: enum → TEXT CHECK (same domain)

---

## 5. error_journal

| Aspect | SQLite (`error_journal`) | Supabase (`error_journal`) |
|--------|--------------------------|------------------------------|
| **Purpose** | Log of user errors during study | Log of user errors during study |
| **Primary key** | `id` INTEGER | `id` UUID |
| **Consumers** | Desktop app, FastAPI | React web app |

### Columns

| Canonical concept | SQLite column | Supabase column | Type (SQLite) | Type (Supabase) | Nullable | Notes |
|---|---|---|---|---|---|---|
| ID | `id` | `id` | INTEGER PK | UUID PK | No | |
| User ID | `user_id` | `user_id` | INTEGER FK→users | UUID FK→profiles | No | |
| Session ID | `session_id` | `session_id` | INTEGER FK→study_sessions | UUID FK→study_sessions | Yes | |
| Error category | `error_category` | `error_category` | VARCHAR(100) | TEXT | Yes | |
| Skill | — | `skill` | — | TEXT | Yes | Supabase only |
| Question snapshot | `question_snapshot` | `question_snapshot` | TEXT | TEXT | Yes | |
| User answer | `user_answer` | `user_answer` | TEXT | TEXT | Yes | |
| Correct answer | `correct_answer` | `correct_answer` | TEXT | TEXT | Yes | |
| Content | `content` | — | TEXT | — | Yes | SQLite only |
| Created at | `created_at` | `created_at` | DATETIME | TIMESTAMPTZ | Yes | |

### Migration notes

- **ID type change**: INTEGER → UUID
- `skill` missing from SQLite (add column)
- `content` missing from Supabase (add column or drop — appears redundant with `question_snapshot`)

---

## 6. study_plans

| Aspect | SQLite (`study_plans`) | Supabase (`study_plans`) |
|--------|------------------------|--------------------------|
| **Purpose** | Weekly study plan | Weekly study plan |
| **Primary key** | `id` INTEGER | `id` UUID |
| **Unique** | — | `(user_id, week_start)` |
| **Consumers** | Desktop app, FastAPI | React web app |

### Columns

| Canonical concept | SQLite column | Supabase column | Type (SQLite) | Type (Supabase) | Nullable | Notes |
|---|---|---|---|---|---|---|
| ID | `id` | `id` | INTEGER PK | UUID PK | No | |
| User ID | `user_id` | `user_id` | INTEGER FK→users | UUID FK→profiles | No | |
| Week start | `week_start` | `week_start` | DATE | DATE | Yes (SQLite) / No (Supabase) | Supabase: NOT NULL |
| Daily tasks | `daily_tasks` | `daily_tasks` | JSON | JSONB | Yes | Supabase: NOT NULL, default `{}` |
| Plan | `plan` | — | JSON | — | Yes | SQLite only (full multi-week plan) |
| Created at | `created_at` | `created_at` | DATETIME | TIMESTAMPTZ | Yes | |

### Migration notes

- **ID type change**: INTEGER → UUID
- `plan` column (full multi-week plan) missing from Supabase — decide: store per-week rows only, or add column
- Add unique constraint `(user_id, week_start)` to SQLite
- `week_start` should be NOT NULL in both

---

## 7. content_cache

| Aspect | SQLite (`content_cache`) | Supabase (`content_cache`) |
|--------|--------------------------|------------------------------|
| **Purpose** | Cache fetched external content | Cache fetched external content |
| **Primary key** | `id` INTEGER | `id` UUID |
| **Consumers** | Desktop app (content_fetcher) | React web app (future) |

### Columns

| Canonical concept | SQLite column | Supabase column | Type (SQLite) | Type (Supabase) | Nullable | Notes |
|---|---|---|---|---|---|---|
| ID | `id` | `id` | INTEGER PK | UUID PK | No | |
| Content type | `content_type` | `content_type` | VARCHAR(50) | TEXT | Yes | |
| Source URL | `source_url` | `source_url` | VARCHAR(500) | TEXT | Yes | |
| Title | `title` | `title` | VARCHAR(300) | TEXT | Yes | |
| Body | `body` | `body` | TEXT | TEXT | Yes | |
| Difficulty | `difficulty_level` | `cefr_level` | VARCHAR(20) | TEXT | Yes | **Name divergence** |
| Exam type | — | `exam_type` | — | TEXT | Yes | Supabase only |
| Fetched at | `fetched_at` | `fetched_at` | DATETIME | TIMESTAMPTZ | Yes | |
| Expires at | `expires_at` | `expires_at` | DATETIME | TIMESTAMPTZ | Yes | Supabase: default `now() + 7 days` |

### Migration notes

- **ID type change**: INTEGER → UUID
- `difficulty_level` → `cefr_level` (name divergence)
- `exam_type` missing from SQLite (add column)

---

## 8. writing_submissions

| Aspect | SQLite | Supabase (`writing_submissions`) |
|--------|--------|-----------------------------------|
| **Purpose** | — | User's writing task submissions with AI feedback |
| **Primary key** | — | `id` UUID |
| **Consumers** | — | React web app |

> ⚠️ This table exists **only in Supabase**. There is no SQLite equivalent.

### Columns (Supabase only)

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| `id` | UUID PK | No | `gen_random_uuid()` |
| `user_id` | UUID FK→profiles | No | |
| `task_prompt` | TEXT | Yes | |
| `user_essay` | TEXT | Yes | |
| `ai_feedback` | JSONB | Yes | |
| `band_estimate` | NUMERIC(3,1) | Yes | |
| `created_at` | TIMESTAMPTZ | Yes | Default `now()` |

### Migration notes

- No SQLite equivalent — create table in canonical schema
- RLS enabled: `auth.uid() = user_id`

---

## Entity Relationship Summary

```
profiles (UUID PK)
├── vocab_progress (UUID PK, FK user_id, FK card_id)
│   └── vocab_cards (UUID PK, shared content)
├── study_sessions (UUID PK, FK user_id)
│   └── error_journal (UUID PK, FK user_id, FK session_id)
├── study_plans (UUID PK, FK user_id)
└── writing_submissions (UUID PK, FK user_id)

content_cache (UUID PK, no user ownership)
```

---

## Tables Missing from One Database

| Table | SQLite | Supabase | Action |
|-------|--------|----------|--------|
| `writing_submissions` | ❌ | ✅ | Add to canonical schema |
| `skill_bands` (column) | ❌ | ✅ (in profiles) | Add to canonical profiles |
| `onboarded` (column) | ❌ | ✅ (in profiles) | Add to canonical profiles |
| `synonym`, `antonym` (columns) | ✅ | ❌ (in vocab_cards) | Add to canonical vocab_cards |
| `image_url` (column) | ✅ | ❌ (in vocab_cards) | Add to canonical vocab_cards |
| `daily_schedule` (column) | ✅ | ❌ (in profiles) | Evaluate: merge into free_time or add column |
| `theme_mode` (column) | ✅ | ❌ (in profiles) | Add to canonical profiles |
| `score` (column) | ✅ | ❌ (in study_sessions) | Drop — derived value |
| `plan` (column) | ✅ | ❌ (in study_plans) | Drop — use per-week rows |
| `content` (column) | ✅ | ❌ (in error_journal) | Drop — redundant with question_snapshot |
