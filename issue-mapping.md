# EnglishCoachPro Issue Mapping

This file tracks which issues have been mapped to an implementation/fix and which are still pending.

## Mapped Issues
- [x] Progress analytics schema mismatch — `study_sessions` now includes `xp_earned`, `items_studied`, and `items_correct`, and the analytics query path was verified.
- [x] Planner integration consistency check — the planner now normalizes string exam types and ISO string exam dates, while the dashboard safely renders stored string exam values and keeps the generated plan fallback active.
- [x] Study screen behavior polish — vocabulary review now filters to due/new cards even when stored review dates arrive as ISO strings, and the regression suite covers that path.
- [x] Onboarding flow completion and validation — the onboarding wizard now normalizes stored exam types to a stable enum value, blocks backward navigation so the required forward-only flow is enforced, and preserves profile consistency across the first-run path.
- [x] Startup profile normalization — the app now normalizes persisted user profiles on launch so older records with missing/default values or string-backed exam fields behave like a completed onboarding profile.
- [x] Reading content loading path — the reading screen now loads curated reading content through the content fetcher instead of relying on a hardcoded placeholder passage.
- [x] Pronunciation feedback guard — the speaking screen now only enables playback when a pronunciation audio file is actually available, preventing false-positive controls.
- [x] Pronunciation dependency resilience — the pronunciation coach now degrades gracefully when text-to-speech dependencies are unavailable, so the speaking flow still evaluates and reports feedback.
- [x] Planner lesson counts — study plans now include a lesson_count for every skill so the UI and downstream flows can show total lessons per skill.
- [x] Vocabulary seed expansion — the app now backfills the vocabulary bank to 50,000 words on startup, using generated seed items when the database is sparse.
- [x] Vocabulary practice sequencing — new words now appear first in practice, learned words are marked in the UI, and review words reappear only when due or after 20 learn cycles.
- [x] Vocabulary enrichment detail — vocabulary cards now surface IPA pronunciation, a synonym, an opposite, and example usage on the practice screen, with on-demand lookup for stored rows that do not yet have those fields.
- [x] Writing fallback coaching — the writing screen now delivers offline feedback if the AI tutor is not configured, ensuring the flow remains useful.

## Unmapped Issues
- [x] Final regression verification suite

## Phase 3-5 Implementation (New)
- [x] Grammar lesson viewer — built-in lessons (Present Simple, Past Simple, Conditionals, Passive Voice, Articles, Present Continuous) with MCQ exercises and error-journal logging.
- [x] Mock test mode — full exam simulation for TOEIC (200Q/120min), IELTS (4 sections), TOEFL, and VSTEP with timer, auto-submit, per-section results, band estimate, and improvement tips.
- [x] Dashboard full spec — streak banner with 7-day heatmap, daily goal ring, quick stats (words learned, band, XP), today's plan cards, and word of the day from DB.
- [x] Progress screen with charts — matplotlib bar chart (time per skill), radar chart (skill balance), line chart (band over time), error journal tab with weak-area review.
- [x] System tray integration — minimize to tray, daily streak reminder, word-of-the-day notification, APScheduler-based.
- [x] Settings with API key management — encrypted Claude API key storage, language selector (EN/VI), theme, profile editing.
- [x] i18n hook — bilingual labels (English / Vietnamese) for all UI elements.
- [x] Word card component — flip-able SRS flashcard with front/back display.
- [x] Streak banner component — fire emoji + streak count + 7-day mini-heatmap.
- [x] GitHub Actions CI/CD — test on PR, build EXE on tag, deploy docs on main.
- [x] MkDocs Material documentation — full site with installation, features, architecture, database schema, and contributing guides.
- [x] Pre-commit hooks — Ruff linting and formatting.
- [x] CHANGELOG.md — semantic versioning changelog.
- [x] Assets directory structure — fonts, icons, audio placeholders.
- [x] AI tutor updated — uses claude-sonnet-4-6 model, passes user's exam type.
