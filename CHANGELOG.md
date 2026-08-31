# Changelog

All notable changes to EnglishCoach Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Grammar screen with 6 built-in lessons and MCQ exercises
- Mock test mode with TOEIC, IELTS, TOEFL, and VSTEP simulations
- System tray integration with daily streak reminders and word-of-the-day notifications
- Matplotlib charts on progress screen (bar, radar, line)
- Error journal tab on progress screen with weak-area review
- Streak banner component with 7-day heatmap
- Word card component with flip animation
- GitHub Actions CI/CD pipeline (test + build EXE + release)
- MkDocs Material documentation site
- Pre-commit hooks with Ruff
- i18n hook for Vietnamese UI labels
- Settings screen with Claude API key management
- Dashboard upgraded with streak banner, daily goal ring, quick stats, word of the day

### Changed
- Sidebar now includes grammar and mock test navigation
- App enforces minimum 1280×720 window size
- Dashboard pulls word of the day from database when available

### Fixed
- Navigation routing for grammar and mock test screens
