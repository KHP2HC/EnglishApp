# Target API Surface

Minimum API endpoints required for the canonical data model.
**Not implemented in this phase** — design only.

All endpoints use `/api/v1/` prefix. Authentication via Bearer JWT.

---

## Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/validate` | Required | Validate current token, return user identity |

> Note: Login/registration/logout are handled by Supabase Auth directly.
> FastAPI only validates tokens. A `/validate` endpoint lets clients
> verify their token and get the canonical user representation.

---

## Profiles

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/profile` | Required | own | — | `Profile` | profiles |
| PUT | `/api/v1/profile` | Required | own | `ProfileUpdate` | `Profile` | profiles |

### Profile

```json
{
  "id": "uuid",
  "name": "string",
  "avatar_emoji": "string",
  "target_exam": "IELTS|TOEIC|TOEFL|VSTEP|null",
  "target_score": "number|null",
  "current_band": "number|null",
  "skill_bands": {"reading": 6.5, "listening": 7.0},
  "exam_date": "date|null",
  "free_time": {"mon": 60, "tue": 60},
  "daily_schedule": {"mon": {"morning": 30}},
  "session_time": "MORNING|AFTERNOON|EVENING",
  "theme_mode": "dark|light|system",
  "streak_days": 0,
  "total_xp": 0,
  "last_active": "timestamp|null",
  "onboarded": false,
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### ProfileUpdate

All fields optional (partial update):

```json
{
  "name": "string",
  "avatar_emoji": "string",
  "target_exam": "IELTS",
  "target_score": 7.5,
  "current_band": 6.0,
  "skill_bands": {},
  "exam_date": "2026-12-01",
  "free_time": {},
  "daily_schedule": {},
  "session_time": "MORNING",
  "theme_mode": "dark",
  "onboarded": true
}
```

> `streak_days`, `total_xp`, `last_active` are server-managed — not
> settable by the client directly.

---

## Vocabulary

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/vocabulary` | Required | — | query: `?page=1&limit=50&cefr=B1&category=verbs` | `VocabCard[]` (paginated) | vocab_cards |
| GET | `/api/v1/vocabulary/{card_id}` | Required | — | — | `VocabCard` | vocab_cards |
| GET | `/api/v1/vocabulary/due` | Required | own | — | `VocabCard[]` | vocab_cards, vocab_progress |
| POST | `/api/v1/vocabulary/search` | Required | — | `{"query": "string", "limit": 20}` | `VocabCard[]` | vocab_cards |

### VocabCard

```json
{
  "id": "uuid",
  "word": "string",
  "phonetic": "string|null",
  "synonym": "string|null",
  "antonym": "string|null",
  "meaning_en": "string",
  "meaning_vi": "string",
  "example_sentence": "string|null",
  "audio_url": "string|null",
  "image_url": "string|null",
  "exam_type": ["IELTS"],
  "cefr_level": "B1|null",
  "category": "general",
  "created_at": "timestamp"
}
```

---

## Reviews (SRS)

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/reviews/due` | Required | own | query: `?limit=50` | `ReviewItem[]` | vocab_progress, vocab_cards |
| POST | `/api/v1/reviews/{card_id}` | Required | own | `ReviewRequest` | `ReviewResult` | vocab_progress |

### ReviewRequest

```json
{
  "quality": 0  // 0=Again, 2=Hard, 3=Good, 5=Easy
}
```

### ReviewResult

```json
{
  "card_id": "uuid",
  "next_review": "date",
  "interval_days": 6,
  "easiness": 2.6,
  "repetitions": 2,
  "times_seen": 5,
  "times_correct": 4,
  "xp_earned": 8
}
```

---

## Study Sessions

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/study-sessions` | Required | own | query: `?page=1&limit=20&type=vocabulary` | `StudySession[]` | study_sessions |
| POST | `/api/v1/study-sessions` | Required | own | `SessionStart` | `StudySession` | study_sessions |
| PATCH | `/api/v1/study-sessions/{id}` | Required | own | `SessionEnd` | `StudySession` | study_sessions |

### SessionStart

```json
{
  "session_type": "VOCABULARY"
}
```

### SessionEnd

```json
{
  "ended_at": "timestamp",
  "xp_earned": 40,
  "items_total": 20,
  "items_correct": 15
}
```

### StudySession

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "started_at": "timestamp",
  "ended_at": "timestamp|null",
  "session_type": "VOCABULARY",
  "xp_earned": 40,
  "items_total": 20,
  "items_correct": 15,
  "created_at": "timestamp"
}
```

---

## Progress

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/progress/summary` | Required | own | — | `ProgressSummary` | profiles, study_sessions, vocab_progress |
| GET | `/api/v1/progress/daily` | Required | own | query: `?days=30` | `DailyActivity[]` | study_sessions |
| GET | `/api/v1/progress/weekly` | Required | own | query: `?weeks=8` | `WeeklyAggregate[]` | study_sessions |
| GET | `/api/v1/progress/streak` | Required | own | — | `StreakInfo` | profiles |

### ProgressSummary

```json
{
  "total_xp": 1250,
  "streak_days": 7,
  "level": {"name": "B1 Builder", "emoji": "🏗️", "current": 1500, "next": 3000},
  "words_learned": 145,
  "words_due": 12,
  "accuracy": 0.78
}
```

### DailyActivity

```json
{
  "date": "2026-08-31",
  "minutes": 45
}
```

---

## Quizzes / Tests

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/tests/reading` | Required | — | — | `ReadingTestSummary[]` | (static content) |
| GET | `/api/v1/tests/reading/{id}` | Required | — | — | `ReadingTest` | (static content) |
| POST | `/api/v1/tests/reading/{id}/grade` | Required | own | `ReadingAnswers` | `TestResult` | study_sessions, error_journal |
| GET | `/api/v1/tests/listening` | Required | — | — | `ListeningTestSummary[]` | (static content) |
| GET | `/api/v1/tests/listening/{id}` | Required | — | — | `ListeningTest` | (static content) |
| POST | `/api/v1/tests/listening/{id}/grade` | Required | own | `ListeningAnswers` | `TestResult` | study_sessions, error_journal |
| GET | `/api/v1/tests/writing` | Required | — | — | `WritingTask[]` | (static content) |
| POST | `/api/v1/tests/writing/submit` | Required | own | `WritingSubmission` | `WritingResult` | writing_submissions, study_sessions |
| GET | `/api/v1/tests/adaptive` | Required | own | query: `?skill=vocabulary` | `CATQuestion` | (static content) |
| POST | `/api/v1/tests/adaptive/answer` | Required | own | `CATAnswer` | `CATResult` | (in-memory) |

### TestResult

```json
{
  "session_id": "uuid",
  "score": 0.75,
  "band": 6.5,
  "xp_earned": 50,
  "items_total": 40,
  "items_correct": 30,
  "errors": [{"category": "reading", "question": "...", "answer": "..."}]
}
```

---

## Planner

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/planner/current` | Required | own | — | `StudyPlan` | study_plans |
| POST | `/api/v1/planner/generate` | Required | own | `PlanRequest` | `StudyPlan` | study_plans |
| PUT | `/api/v1/planner/{week_start}` | Required | own | `PlanUpdate` | `StudyPlan` | study_plans |

### PlanRequest

```json
{
  "exam_date": "2026-12-01",
  "free_time": {"mon": 60},
  "current_band": 5.5
}
```

### StudyPlan

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "week_start": "2026-08-31",
  "daily_tasks": {
    "mon": [{"type": "VOCABULARY", "minutes": 30, "label": "Vocab Review"}],
    "tue": [{"type": "READING", "minutes": 25, "label": "Reading Practice"}]
  },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

## Error Journal

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/errors` | Required | own | query: `?page=1&limit=20&category=reading` | `ErrorEntry[]` | error_journal |
| GET | `/api/v1/errors/{id}` | Required | own | — | `ErrorEntry` | error_journal |

### ErrorEntry

```json
{
  "id": "uuid",
  "session_id": "uuid|null",
  "error_category": "reading",
  "skill": "vocabulary",
  "question_snapshot": "string",
  "user_answer": "string",
  "correct_answer": "string",
  "created_at": "timestamp"
}
```

---

## Writing Submissions

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/writing/submissions` | Required | own | query: `?page=1&limit=20` | `WritingSubmission[]` | writing_submissions |
| GET | `/api/v1/writing/submissions/{id}` | Required | own | — | `WritingSubmission` | writing_submissions |
| DELETE | `/api/v1/writing/submissions/{id}` | Required | own | — | `MessageResponse` | writing_submissions (soft delete) |

---

## Admin

| Method | Path | Auth | Authorization | Request | Response | Entities |
|--------|------|------|----------------|---------|----------|----------|
| GET | `/api/v1/admin/stats` | Required | admin | — | `AdminStats` | all |
| GET | `/api/v1/admin/users` | Required | admin | query: `?page=1&limit=50` | `Profile[]` | profiles |

---

## Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/health` | None | Liveness probe |

---

## Summary

| Category | Endpoints |
|----------|----------|
| Auth | 1 |
| Profiles | 2 |
| Vocabulary | 4 |
| Reviews | 2 |
| Study Sessions | 3 |
| Progress | 4 |
| Tests/Quizzes | 10 |
| Planner | 3 |
| Error Journal | 2 |
| Writing | 3 |
| Admin | 2 |
| Health | 1 |
| **Total** | **37** |
