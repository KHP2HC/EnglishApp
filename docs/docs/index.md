# EnglishCoach Pro

**AI-Powered English Exam Preparation Desktop App**

EnglishCoach Pro is a fully offline-capable Windows desktop application for
Vietnamese learners preparing for TOEIC, IELTS, TOEFL, or VSTEP. It functions
as a personal AI coach — not just a content library.

## Key Features

- 🧠 **SRS Vocabulary** — SM-2 spaced repetition with 50,000+ words
- 📐 **Grammar Lessons** — Interactive lessons with exercises and error tracking
- 📖 **Reading Practice** — IELTS-style academic reading tests
- 👂 **Listening Practice** — Audio comprehension exercises
- ✍️ **Writing Feedback** — AI-powered essay evaluation (Claude API)
- 🗣️ **Pronunciation Coach** — Whisper STT + pronunciation scoring
- 🧪 **Mock Tests** — Full exam simulation with timer and results
- 📊 **Progress Tracking** — Heatmaps, charts, and error journal
- 🗓️ **Study Planner** — AI-generated weekly plans from your deadline
- 🔥 **Streak System** — Gamified daily study habit builder

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## Build EXE

```bash
pyinstaller --onefile --windowed --name EnglishCoachPro main.py
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI | CustomTkinter |
| Database | SQLite + SQLAlchemy |
| AI | Anthropic Claude API |
| TTS | edge-tts |
| STT | openai-whisper |
| Charts | matplotlib |
| Packaging | PyInstaller |

## License

MIT
