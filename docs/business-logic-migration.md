# Business Logic Migration Plan

Analysis of business logic duplicated between Python and TypeScript,
with a plan to centralize it in FastAPI.

---

## 1. SRS (Spaced Repetition — SM-2)

### Current Implementations

| Aspect | Python (`core/srs_engine.py`) | TypeScript (`web/src/lib/srs.ts`) |
|--------|-------------------------------|----------------------------------|
| Algorithm | SM-2 | SM-2 |
| Quality scale | 0–5 (any int) | `0 \| 2 \| 3 \| 5` |
| Interval formula | `reps==0→1, reps==1→6, else→round(interval*easiness)` | Same |
| Easiness formula | `EF + (0.1 - (5-q)*(0.08+(5-q)*0.02))` | Same |
| Easiness rounding | None (raw float) | `Math.round(e * 100) / 100` |
| Min easiness | `max(1.3, EF)` | `Math.max(1.3, EF)` |

### Field Name Divergence

| Python field | TS field | Canonical |
|--------------|----------|-----------|
| `srs_interval` | `interval_days` | `interval_days` |
| `srs_easiness` | `easiness` | `easiness` |
| `srs_repetitions` | `repetitions` | `repetitions` |
| `next_review_date` | `next_review` | `next_review` |
| `last_quality` | `last_quality` | `last_quality` |
| `times_seen` | `times_seen` | `times_seen` |
| `times_correct` | `times_correct` | `times_correct` |

### Behavior Differences

1. **Quality scale**: Python accepts 0–5; TypeScript restricts to
   `0|2|3|5`. **Canonical: `0|2|3|5`** (the user-facing options).
   Internal SM-2 allows 0–5 but the UI only offers 4 buttons.

2. **Easiness rounding**: Python stores raw float; TypeScript rounds
   to 2 decimals. **Canonical: round to 2 decimals** (matches
   `NUMERIC(3,2)` in PostgreSQL).

### Canonical Implementation

```python
# core/srs_engine.py (canonical)

QUALITY_VALUES = {0, 2, 3, 5}  # Again, Hard, Good, Easy

def sm2_update(
    interval_days: int,
    easiness: float,
    repetitions: int,
    quality: int,
) -> dict:
    if quality not in QUALITY_VALUES:
        raise ValueError(f"Quality must be one of {QUALITY_VALUES}")

    if quality < 3:
        new_interval = 1
        new_repetitions = 0
    else:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval_days * easiness)
        new_repetitions = repetitions + 1

    new_easiness = easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_easiness = round(max(1.3, new_easiness) * 100) / 100

    return {
        "interval_days": new_interval,
        "easiness": new_easiness,
        "repetitions": new_repetitions,
    }
```

### Required Test Cases

- [ ] Quality 0 (Again) resets repetitions to 0, interval to 1
- [ ] Quality 3 (Good) with reps=0 → interval=1, reps=1
- [ ] Quality 3 (Good) with reps=1 → interval=6, reps=2
- [ ] Quality 5 (Easy) with reps=2, interval=6, easiness=2.5 → interval=15, reps=3
- [ ] Easiness never drops below 1.3
- [ ] Easiness rounded to 2 decimal places
- [ ] Quality 1, 4 rejected (not in {0, 2, 3, 5})
- [ ] Quality -1, 6 rejected (out of range)

---

## 2. Study Planner

### Current Implementations

| Aspect | Python (`core/study_planner.py`) | TypeScript (`web/src/lib/planner.ts`) |
|--------|----------------------------------|--------------------------------------|
| Skills | vocabulary, reading, listening, writing, speaking | vocabulary, grammar, listening, reading, writing, speaking |
| Band overrides | Yes (band ≤2.0, ≤3.0, ≥5.0) | No |
| Weakest/strongest adjustment | No | Yes (+0.05/−0.05) |
| Mock test in final 4 weeks | No | Yes (0.10 weight, Saturday full) |
| Plan scope | Multi-week until exam_date | Single week (7 days) |
| Output fields | `type`, `minutes`, `lesson_count` | `type`, `minutes`, `label` |
| CEFR↔score conversion | No | Yes |

### Weight Table Divergence

**Python:**

| Exam | vocab | reading | listening | writing | speaking |
|------|-------|---------|-----------|---------|----------|
| IELTS | 0.25 | 0.25 | 0.25 | 0.15 | 0.10 |
| TOEFL | 0.20 | 0.30 | 0.30 | 0.10 | 0.10 |
| TOEIC | 0.25 | 0.20 | 0.35 | 0.10 | 0.10 |
| Default | 0.30 | 0.25 | 0.20 | 0.15 | 0.10 |

**TypeScript:**

| Exam | vocab | grammar | listening | reading | writing | speaking |
|------|-------|--------|-----------|---------|---------|----------|
| TOEIC | 0.35 | 0.25 | 0.30 | 0.10 | — | — |
| IELTS | 0.25 | 0.20 | 0.20 | 0.20 | 0.15 | — |
| TOEFL | 0.20 | 0.20 | 0.20 | 0.20 | 0.10 | 0.10 |
| VSTEP | 0.30 | 0.20 | 0.20 | 0.20 | 0.10 | — |

### Canonical Decision

1. **Add `grammar` as a skill** — TypeScript is correct; grammar is a
   distinct study area.
2. **Keep band-based overrides** — Python's approach is more
   sophisticated. Low-band users need more vocabulary.
3. **Add weakest/strongest adjustment** — TypeScript's dynamic
   adjustment is valuable.
4. **Add mock test in final 4 weeks** — TypeScript's approach.
5. **Multi-week plan** — Python's approach (generate until exam_date).
6. **Output**: `type`, `minutes`, `label` (drop `lesson_count` —
   derived value).

### Canonical Weight Table

```python
BASE_WEIGHTS = {
    "IELTS": {"vocabulary": 0.25, "grammar": 0.15, "reading": 0.20,
              "listening": 0.20, "writing": 0.12, "speaking": 0.08},
    "TOEFL":  {"vocabulary": 0.20, "grammar": 0.15, "reading": 0.20,
              "listening": 0.20, "writing": 0.10, "speaking": 0.15},
    "TOEIC":  {"vocabulary": 0.30, "grammar": 0.20, "reading": 0.15,
              "listening": 0.25, "writing": 0.05, "speaking": 0.05},
    "VSTEP":  {"vocabulary": 0.25, "grammar": 0.20, "reading": 0.20,
              "listening": 0.20, "writing": 0.10, "speaking": 0.05},
}

BAND_OVERRIDES = {
    "low":   {"vocabulary": 0.35, "grammar": 0.20, "reading": 0.15,
              "listening": 0.15, "writing": 0.08, "speaking": 0.07},  # band ≤ 3.0
    "high":  {"vocabulary": 0.18, "grammar": 0.15, "reading": 0.20,
              "listening": 0.17, "writing": 0.15, "speaking": 0.15},  # band ≥ 5.5
}
```

### Required Test Cases

- [ ] IELTS weights sum to 1.0
- [ ] TOEFL weights sum to 1.0
- [ ] TOEIC weights sum to 1.0
- [ ] VSTEP weights sum to 1.0
- [ ] Low-band override increases vocabulary weight
- [ ] High-band override increases writing/speaking weight
- [ ] Plan generates weeks until exam_date
- [ ] Each day has at least one task if free_time > 0
- [ ] Mock test added in final 4 weeks
- [ ] Weakest skill gets +0.05 weight boost

---

## 3. Computer Adaptive Test (CAT)

### Current Implementations

| Aspect | Python (`core/adaptive_test.py`) | TypeScript (`web/src/lib/cat.ts`) |
|--------|----------------------------------|----------------------------------|
| Levels | A1, A2, B1, B2, C1, C2 | Same |
| Start level | B1 (index 2) | B1 |
| Advancement | Streak: 3 correct → up, 2 wrong → down | Sliding window: >80% → up, <40% → down (last 5) |
| Min answers before adjust | None | 3 |
| Per-skill tracking | No | Yes |
| History | No | Yes (`{level, correct}[]`) |
| Completion | ~20 questions | ~20 questions |

### Canonical Decision

**Adopt the TypeScript sliding-window approach** — it is more robust:
- Less sensitive to noise (single wrong answer doesn't drop level).
- Per-skill tracking enables targeted feedback.
- History enables post-test analysis.

### Canonical Algorithm

```python
LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
START_LEVEL = "B1"
MIN_ANSWERS_BEFORE_ADJUST = 3
WINDOW_SIZE = 5
UP_THRESHOLD = 0.8
DOWN_THRESHOLD = 0.4
MAX_QUESTIONS = 20

def next_level(history, current_level, skill_scores):
    if len(history) < MIN_ANSWERS_BEFORE_ADJUST:
        return current_level

    recent = history[-WINDOW_SIZE:]
    accuracy = sum(1 for h in recent if h["correct"]) / len(recent)

    idx = LEVELS.index(current_level)
    if accuracy >= UP_THRESHOLD and idx < len(LEVELS) - 1:
        return LEVELS[idx + 1]
    if accuracy <= DOWN_THRESHOLD and idx > 0:
        return LEVELS[idx - 1]
    return current_level
```

### Required Test Cases

- [ ] Starts at B1
- [ ] 3 correct in last 5 → level up
- [ ] 2 wrong in last 5 → level down
- [ ] No adjustment before 3 answers
- [ ] Stays at C2 (can't go higher)
- [ ] Stays at A1 (can't go lower)
- [ ] Stops at 20 questions
- [ ] Per-skill scores tracked correctly

---

## 4. XP and Levels

### Current State

| Aspect | Python | TypeScript (`web/src/lib/srs.ts`) |
|--------|--------|----------------------------------|
| XP calculation | None (received as parameter) | `calculateXp()` with action-based values |
| Level system | None | `getLevelInfo()` with 7 thresholds |
| Streak badges | None | `getStreakBadge()` |

### Canonical XP Table

```python
XP_REWARDS = {
    "srs_review_correct": 8,   # 3 base + 5 bonus
    "srs_review_wrong": 3,
    "exercise_correct": 10,
    "exercise_wrong": 2,
    "mock_test": 50,
    "writing_feedback": 20,
    "daily_goal": 25,
    "streak_bonus": 100,
}
```

### Canonical Level Table

```python
LEVELS = [
    {"threshold": 0,     "name": "A1 Newcomer",  "emoji": "🌱"},
    {"threshold": 500,   "name": "A2 Explorer",   "emoji": "🗺️"},
    {"threshold": 1500,  "name": "B1 Builder",    "emoji": "🏗️"},
    {"threshold": 3000,  "name": "B2 Achiever",   "emoji": "🎯"},
    {"threshold": 5000,  "name": "C1 Expert",     "emoji": "💡"},
    {"threshold": 8000,  "name": "C2 Master",     "emoji": "👑"},
    {"threshold": 12000, "name": "Exam Ready",     "emoji": "🎓"},
]
```

### Canonical Streak Badges

```python
STREAK_BADGES = [
    {"threshold": 7,   "badge": "🔥"},
    {"threshold": 30,   "badge": "💎"},
    {"threshold": 100,  "badge": "👑"},
    {"threshold": 365,  "badge": "🏆"},
]
```

### Required Test Cases

- [ ] SRS correct → 8 XP
- [ ] SRS wrong → 3 XP
- [ ] Mock test → 50 XP
- [ ] Level at 0 XP → A1 Newcomer
- [ ] Level at 500 XP → A2 Explorer
- [ ] Level at 12000 XP → Exam Ready
- [ ] Streak badge at 7 days → 🔥
- [ ] `total_xp` is derived from sum of session `xp_earned` (not stored independently)

---

## 5. Band Conversion

### Current State

| Aspect | Python (`core/reading_test.py`) | TypeScript (`web/src/lib/ielts-bands.ts`) |
|--------|--------------------------------|------------------------------------------|
| Reading table | 17 entries (39→9.0 ... 1→1.0) | 19 entries (40→9.0 ... 0→0) |
| Listening table | None | 18 entries (40→9.0 ... 0→0) |
| Overall band | None | Average, rounded to 0.5 |
| Band labels | None | Yes (9→"Expert User", etc.) |
| Scaling | `round(raw * 40 / total)` | Same |

### Canonical Decision

- **Adopt TypeScript's tables** (include 40→9.0 and 0→0 entries).
- **Add listening table** to Python.
- **Add overall band calculation** to Python.
- **Add band labels** to Python.
- **Centralize in FastAPI** — both clients call the API for grading.

### Canonical Band Tables

```python
READING_BAND_TABLE = [
    (40, 9.0), (39, 8.5), (37, 8.0), (35, 7.5), (33, 7.0),
    (30, 6.5), (27, 6.0), (23, 5.5), (19, 5.0), (15, 4.5),
    (13, 4.0), (10, 3.5), (8, 3.0), (6, 2.5), (4, 2.0),
    (3, 1.5), (2, 1.5), (1, 1.0), (0, 0.0),
]

LISTENING_BAND_TABLE = [
    (40, 9.0), (39, 8.5), (37, 8.0), (35, 7.5), (32, 7.0),
    (30, 6.5), (26, 6.0), (23, 5.5), (19, 5.0), (15, 4.5),
    (12, 4.0), (8, 3.5), (6, 3.0), (4, 2.5), (3, 2.0),
    (2, 1.5), (1, 1.0), (0, 0.0),
]
```

### Required Test Cases

- [ ] 40/40 → band 9.0
- [ ] 30/40 → band 6.5
- [ ] 0/40 → band 0.0
- [ ] 15/20 → scaled to 30/40 → band 6.5
- [ ] Overall band = average of [6.0, 7.0, 6.5] → 6.5
- [ ] Overall band rounds to nearest 0.5

---

## 6. Streak Calculation

### Current State

| Aspect | Python (`core/session_manager.py`) | TypeScript |
|--------|-------------------------------------|------------|
| Streak update | `last_active` date comparison | None (reads stored value) |
| Logic | today=keep, yesterday=+1, else=reset to 1 | N/A |

### Canonical Algorithm

```python
def update_streak(user, session_date=None):
    today = (session_date or datetime.utcnow()).date()
    last = user.last_active.date() if user.last_active else None

    if last is None:
        new_streak = 1
    elif last == today:
        new_streak = user.streak_days  # already active today
    elif last == today - timedelta(days=1):
        new_streak = user.streak_days + 1  # consecutive day
    else:
        new_streak = 1  # streak broken

    user.streak_days = new_streak
    user.last_active = datetime.utcnow()
    return new_streak
```

### Required Test Cases

- [ ] First-ever session → streak = 1
- [ ] Session same day → streak unchanged
- [ ] Session next day → streak + 1
- [ ] Session after 2-day gap → streak = 1
- [ ] `last_active` updated to current timestamp

---

## 7. Session Management

### Current State

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Session lifecycle | Full (DB + XP + streak) | In-memory Zustand + page-level Supabase writes |
| Score | `items_correct / items_studied` | Not stored |
| Field names | `items_studied` | `items_total` |

### Canonical Decision

- **Canonical field name**: `items_total` (not `items_studied`)
- **Score is derived** — do not store; compute on read
- **FastAPI manages full lifecycle**: start session → record items →
  end session (updates XP, streak, creates error journal entries)

---

## 8. CEFR ↔ Score Conversion

### Current State

TypeScript only (`web/src/lib/planner.ts`):

| CEFR | TOEIC | IELTS | TOEFL |
|------|-------|-------|-------|
| A1 | 0 | 0 | 0 |
| A2 | 250 | 2 | 30 |
| B1 | 400 | 3.5 | 50 |
| B2 | 550 | 4.5 | 70 |
| C1 | 785 | 5.5 | 90 |
| C2 | 945 | 7 | 105 |

### Canonical Decision

Centralize in FastAPI. Both clients call the API for conversion.

---

## Summary: Migration Priority

| Logic | Divergence | Priority | Effort |
|-------|------------|----------|--------|
| SRS (SM-2) | Minor (field names, rounding) | P0 — blocks vocab API | Low |
| Band conversion | Moderate (missing tables in Python) | P0 — blocks test grading | Low |
| XP/Levels | TypeScript-only | P1 — blocks progress API | Low |
| Streak | Python-only | P1 — blocks session API | Low |
| Session management | Major (split across TS files) | P1 — blocks session API | Medium |
| Study planner | Major (different weight tables) | P2 — blocks planner API | Medium |
| CAT | Major (different algorithms) | P2 — blocks adaptive test API | Medium |
| CEFR↔score | TypeScript-only | P2 — nice to have | Low |

### Migration Order

1. **SRS** → enables vocabulary/review API
2. **Band conversion** → enables test grading API
3. **XP/Levels** → enables progress API
4. **Streak** → enables session API
5. **Session management** → enables full session lifecycle
6. **Study planner** → enables planner API
7. **CAT** → enables adaptive test API
8. **CEFR↔score** → utility function
