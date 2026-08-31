# API Audit — EnglishCoach Pro

## Overview

The FastAPI backend (`api.py`) is a **minimal API** with only 5 endpoints. The web frontend bypasses FastAPI entirely and communicates **directly with Supabase** from the browser. The desktop app does not use the API at all — it accesses SQLite directly via SQLAlchemy.

### Current API Surface

```
FastAPI (api.py)
├── POST   /api/vocab/rate              — SRS card rating
├── GET    /api/reading/tests           — List reading tests
├── GET    /api/reading/test/{test_id}  — Get single reading test
├── POST   /api/reading/test/{test_id}/grade — Grade reading test
└── GET    /api/v1/health              — Health check
```

---

## 1. Endpoint Details

### POST `/api/vocab/rate`

| Aspect | Detail |
|--------|--------|
| Method | POST |
| Authentication | **None** |
| Request body | `{"card_id": int, "quality": int}` |
| Response | `{"message": str, "next_review": date}` |
| Database | SQLite via SQLAlchemy (`UserVocabularyProgress`) |
| Business logic | `SRSEngine.update_card()` |
| Desktop consumer | **None** (desktop uses SQLite directly) |
| Web consumer | **None** (web uses Supabase directly) |

**Problem**: No consumer actually uses this endpoint. The desktop calls `SRSEngine` directly. The web frontend calls Supabase directly.

---

### GET `/api/reading/tests`

| Aspect | Detail |
|--------|--------|
| Method | GET |
| Authentication | **None** |
| Response | `[{"id": str, "title": str}]` |
| Database | File read (`data/seed/reading_tests.json`) |
| Business logic | `reading_test.load_tests()` |
| Desktop consumer | **None** (reads JSON directly) |
| Web consumer | **None** (reads from `web/public/data/reading_tests.json`) |

**Problem**: Both desktop and web have their own copies of reading test data. The API endpoint is unused.

---

### GET `/api/reading/test/{test_id}`

| Aspect | Detail |
|--------|--------|
| Method | GET |
| Authentication | **None** |
| Response | Full test object with passages and questions |
| Database | File read (`data/seed/reading_tests.json`) |
| Business logic | `reading_test.load_test()` |
| Desktop consumer | **None** |
| Web consumer | **None** |

---

### POST `/api/reading/test/{test_id}/grade`

| Aspect | Detail |
|--------|--------|
| Method | POST |
| Authentication | **None** |
| Request body | `{"answers": dict}` |
| Response | Grading result with score and band |
| Database | None (pure computation) |
| Business logic | `reading_test.grade()` |
| Desktop consumer | **None** (grades locally) |
| Web consumer | **None** (grades locally) |

---

### GET `/api/v1/health`

| Aspect | Detail |
|--------|--------|
| Method | GET |
| Authentication | **None** |
| Response | `{"status": "healthy"}` |
| Database | None |
| Desktop consumer | **None** |
| Web consumer | **None** (used by Docker healthcheck) |

---

## 2. Missing API Boundaries

The following functionality exists in both desktop and web but has **no API endpoint**:

### User Management
| Operation | Desktop | Web | API |
|-----------|---------|-----|-----|
| Create user | SQLite direct | Supabase Auth | **Missing** |
| Get profile | SQLite direct | Supabase direct | **Missing** |
| Update profile | SQLite direct | Supabase direct | **Missing** |
| Delete user | SQLite direct | Supabase Auth | **Missing** |

### Vocabulary
| Operation | Desktop | Web | API |
|-----------|---------|-----|-----|
| List cards | SQLite direct | Supabase direct | **Missing** |
| Get due cards | SQLite direct | Supabase direct | **Missing** |
| Rate card (SRS) | `SRSEngine` direct | `sm2Update()` in browser | **Exists but unused** |
| Enrich card | `vocabulary_enrichment` | Not implemented | **Missing** |

### Study Sessions
| Operation | Desktop | Web | API |
|-----------|---------|-----|-----|
| Start session | `session_manager` direct | `session.store` (client only) | **Missing** |
| End session | `session_manager` direct | Not persisted | **Missing** |
| List sessions | SQLite direct | Supabase direct | **Missing** |

### Progress & Analytics
| Operation | Desktop | Web | API |
|-----------|---------|-----|-----|
| Daily activity | `analytics.py` direct | Supabase direct | **Missing** |
| Weekly aggregates | `analytics.py` direct | Computed in browser | **Missing** |
| Error journal | SQLite direct | Supabase direct | **Missing** |

### Study Planner
| Operation | Desktop | Web | API |
|-----------|---------|-----|-----|
| Generate plan | `study_planner.py` | `planner.ts` (browser) | **Missing** |
| Save plan | SQLite direct | Supabase direct | **Missing** |
| Get plan | SQLite direct | Supabase direct | **Missing** |

### Writing Feedback
| Operation | Desktop | Web | API |
|-----------|---------|-----|-----|
| Submit essay | `ai_tutor.py` (Claude direct) | Supabase Edge Function | **Missing** |
| Get feedback | `ai_tutor.py` | Edge Function response | **Missing** |

### Reading Tests
| Operation | Desktop | Web | API |
|-----------|---------|-----|-----|
| List tests | JSON file direct | Static JSON file | **Exists but unused** |
| Get test | JSON file direct | Static JSON file | **Exists but unused** |
| Grade test | `reading_test.grade()` | Local computation | **Exists but unused** |

### Content Fetching
| Operation | Desktop | Web | API |
|-----------|---------|-----|-----|
| Fetch articles | `content_fetcher.py` | Supabase Edge Function | **Missing** |

### Pronunciation
| Operation | Desktop | Web | API |
|-----------|---------|-----|-----|
| Evaluate speech | `pronunciation.py` (Whisper) | Browser Speech API | **Missing** |

---

## 3. Authentication

**The FastAPI backend has zero authentication.** All endpoints are publicly accessible.

- No JWT validation
- No API key requirement
- No session checking
- No rate limiting
- No user context in any endpoint

The web frontend authenticates via Supabase Auth directly, but the API does not validate Supabase tokens.

---

## 4. Duplicated Business Logic

| Logic | Desktop Implementation | Web Implementation | Divergence |
|-------|----------------------|-------------------|------------|
| SRS (SM-2) | `core/srs_engine.py` | `web/src/lib/srs.ts` | **Identical algorithm, different language** |
| Study planner | `core/study_planner.py` | `web/src/lib/planner.ts` | **Different allocation weights** |
| IELTS band conversion | `core/reading_test.py` | `web/src/lib/ielts-bands.ts` | **Identical tables** |
| CAT (adaptive test) | `core/adaptive_test.py` | `web/src/lib/cat.ts` | **Different algorithms** |
| XP calculation | Inline in `session_manager.py` | `web/src/lib/srs.ts` | **Different XP values** |
| Content fetching | `core/content_fetcher.py` | `web/supabase/functions/fetch-content/` | **Different sources, different parsing** |
| AI writing feedback | `core/ai_tutor.py` | `web/supabase/functions/ai-feedback/` | **Different prompts, different response format** |

---

## 5. Critical Findings

1. **The API is effectively a no-op**: No consumer uses it. Both desktop and web bypass it entirely.
2. **No authentication on any endpoint**: Anyone can rate cards or fetch tests.
3. **Business logic is duplicated** across Python and TypeScript with diverging implementations.
4. **No API contract documentation**: No OpenAPI/Swagger schema, no shared types.
5. **The web frontend directly accesses Supabase** from the browser, bypassing any backend control.
6. **The desktop app directly accesses SQLite**, with no API layer for potential sync.
