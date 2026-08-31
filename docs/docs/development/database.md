# Database Schema

All tables are managed by SQLAlchemy ORM and stored in `data/data.db` (SQLite).

## User

| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| name | String(50) | User's name |
| avatar_emoji | String(4) | Avatar emoji |
| target_exam | Enum | TOEIC, IELTS, TOEFL, VSTEP |
| target_score | Float | Target score |
| current_band | Float | From placement test |
| exam_date | Date | Target exam date |
| daily_free_minutes | JSON | `{"mon": 60, "tue": 90, ...}` |
| daily_schedule | JSON | `{"mon": {"morning": 30, ...}}` |
| preferred_session_time | String | MORNING, AFTERNOON, EVENING |
| theme_mode | String | dark, light, system |
| streak_days | Integer | Current streak |
| total_xp | Integer | Total XP earned |
| last_active | DateTime | Last activity timestamp |

## VocabularyCard

| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| word | String(100) | Unique word |
| phonetic | String(50) | IPA transcription |
| synonym | String(100) | Synonym |
| antonym | String(100) | Antonym |
| meaning_en | Text | English definition |
| meaning_vi | Text | Vietnamese meaning |
| example_sentence | Text | Example usage |
| exam_type | Enum | Which exam |
| difficulty_level | Enum | A1–C2 |
| category | String(50) | Topic category |

## UserVocabularyProgress

| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| user_id | FK → users | |
| card_id | FK → vocabulary_cards | |
| srs_interval | Integer | Days until next review |
| srs_easiness | Float | SM-2 E-factor |
| srs_repetitions | Integer | Consecutive correct |
| next_review_date | Date | When to review next |
| last_quality | Integer | 0–5 quality score |
| times_seen | Integer | Total reviews |
| times_correct | Integer | Correct reviews |

## StudySession

| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | Auto-increment |
| user_id | FK → users | |
| session_type | Enum | VOCAB, GRAMMAR, etc. |
| started_at | DateTime | |
| ended_at | DateTime | |
| score | Float | Accuracy ratio |
| xp_earned | Integer | XP from session |
| items_studied | Integer | |
| items_correct | Integer | |

## ErrorJournalEntry

| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | |
| user_id | FK → users | |
| session_id | FK → study_sessions | |
| error_category | String | e.g. "grammar:conditionals" |
| question_snapshot | Text | |
| user_answer | Text | |
| correct_answer | Text | |
| content | Text | Explanation |
| created_at | DateTime | |

## StudyPlan

| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | |
| user_id | FK → users | |
| week_start | Date | |
| daily_tasks | JSON | Generated plan |
| plan | JSON | Full plan structure |
| created_at | DateTime | |

## ContentCache

| Column | Type | Description |
|--------|------|-------------|
| id | Integer PK | |
| content_type | String | e.g. "reading" |
| source_url | String | |
| title | String | |
| body | Text | |
| difficulty_level | String | |
| fetched_at | DateTime | |
| expires_at | DateTime | |
