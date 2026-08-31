# Architecture

## Overview

EnglishCoach Pro is a desktop application built with Python and CustomTkinter.
All user data is stored locally in SQLite — no server, no cloud sync.

```
┌─────────────────────────────────────────────┐
│                  main.py                     │
│              (Entry Point)                   │
├──────────────┬──────────────────────────────┤
│   app.py     │       core/                   │
│  (Router)    │  • srs_engine (SM-2)          │
│              │  • adaptive_test (CAT)        │
│  ┌────────┐  │  • study_planner              │
│  │  UI    │  │  • ai_tutor (Claude)          │
│  │ screens│  │  • pronunciation (Whisper)   │
│  │        │  │  • content_fetcher            │
│  └────────┘  │  • session_manager             │
│              │  • analytics                   │
├──────────────┤  • tray                        │
│   data/      ├──────────────────────────────┤
│  • models    │       ui/                     │
│  • database  │  • screens/ (12 screens)       │
│  • seed/     │  • components/ (widgets)       │
└──────────────┴──────────────────────────────┘
```

## Data Flow

1. **User action** → UI screen → core module → database
2. **Study session** → `session_manager` → `StudySession` + `User` XP update
3. **Vocabulary review** → `srs_engine` → `UserVocabularyProgress` update
4. **Writing feedback** → `ai_tutor` → Claude API → display result
5. **Pronunciation** → `pronunciation` → Whisper STT → score + TTS

## Key Design Decisions

- **Offline-first**: All core features work without internet. Only AI writing
  feedback and content fetching require connectivity.
- **Local-only data**: SQLite database stored alongside the app. No accounts,
  no cloud sync.
- **Encrypted API key**: Claude API key stored encrypted using machine-specific
  key derivation via the `cryptography` library.
- **Graceful degradation**: If optional dependencies (Whisper, edge-tts) are
  missing, the app continues to function with reduced features.
