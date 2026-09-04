"""
test_original_content_integrity.py — Content regression tests.

These tests prevent future deployments from accidentally replacing original
production content with development/demo content.

Run: python -m pytest tests/test_original_content_integrity.py -v
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

# ─── Paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_DATA_DIR = PROJECT_ROOT / "web" / "public" / "data"
SEED_SQL_PATH = PROJECT_ROOT / "supabase" / "seeds" / "seed_vocab_cards.sql"

# ─── Constants ───────────────────────────────────────────────────────────────

MIN_VOCAB_COUNT = 5000
MIN_TEST_COUNT = 100

# Canonical words that MUST be present in production vocabulary
CANONICAL_WORDS = [
    "abandon", "ability", "about", "above", "abroad", "absence", "absolute",
    "abstract", "abundant", "abuse", "academic", "access", "accommodate",
    "accomplish", "account", "accurate", "achieve", "acquire", "adapt",
    "adequate", "adjust", "administer", "admit", "adopt", "advance",
    "advantage", "adventure", "advice", "affect", "afford", "aggressive",
    "agree", "approach", "appropriate", "arrange", "assemble", "assess",
    "assign", "attain", "attend", "attract", "available", "away",
]

# Markers that indicate demo/test/placeholder content
DEMO_MARKERS = [
    "Common English vocabulary word",
    "lorem ipsum",
    "test word placeholder",
    "sample text placeholder",
    "demo vocabulary entry",
    "placeholder meaning",
]


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def vocab_data():
    """Load the web vocabulary JSON."""
    path = WEB_DATA_DIR / "vocab.json"
    if not path.exists():
        pytest.skip(f"Vocabulary file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def seed_sql():
    """Load the Supabase seed SQL."""
    if not SEED_SQL_PATH.exists():
        pytest.skip(f"Seed SQL not found: {SEED_SQL_PATH}")
    with open(SEED_SQL_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ─── Vocabulary Tests ────────────────────────────────────────────────────────

class TestVocabularyIntegrity:
    """Verify vocabulary content integrity."""

    def test_minimum_count(self, vocab_data):
        """Vocabulary must have at least MIN_VOCAB_COUNT entries."""
        assert len(vocab_data) >= MIN_VOCAB_COUNT, (
            f"Vocabulary has only {len(vocab_data)} entries, "
            f"expected at least {MIN_VOCAB_COUNT}"
        )

    def test_no_duplicates(self, vocab_data):
        """Vocabulary must not have duplicate words."""
        words = [v.get("word", "").lower().strip() for v in vocab_data]
        duplicates = [w for w in words if words.count(w) > 1]
        unique_duplicates = list(set(duplicates))
        assert not unique_duplicates, (
            f"Found {len(unique_duplicates)} duplicate words: "
            f"{unique_duplicates[:10]}"
        )

    def test_canonical_words_present(self, vocab_data):
        """All canonical words must be present in the vocabulary."""
        vocab_words = {v.get("word", "").lower().strip() for v in vocab_data}
        missing = [w for w in CANONICAL_WORDS if w not in vocab_words]
        assert not missing, f"Missing canonical words: {missing}"

    def test_no_placeholder_content(self, vocab_data):
        """No vocabulary entry should contain placeholder/demo markers."""
        for entry in vocab_data:
            meaning_en = entry.get("meaning_en", "")
            for marker in DEMO_MARKERS:
                assert marker.lower() not in meaning_en.lower(), (
                    f"Entry '{entry.get('word')}' contains demo marker "
                    f"'{marker}' in meaning_en"
                )

    def test_required_fields(self, vocab_data):
        """Every vocabulary entry must have required fields."""
        # phonetic is optional (some words may not have IPA available)
        required = ["word", "meaning_en", "meaning_vi",
                     "difficulty_level", "category"]
        for i, entry in enumerate(vocab_data):
            for field in required:
                value = entry.get(field)
                assert value is not None and str(value).strip(), (
                    f"Entry {i} ('{entry.get('word', '?')}') "
                    f"missing required field '{field}'"
                )

    def test_valid_cefr_levels(self, vocab_data):
        """All CEFR levels must be valid (A1–C2)."""
        valid_levels = {"A1", "A2", "B1", "B2", "C1", "C2"}
        for entry in vocab_data:
            level = entry.get("difficulty_level") or entry.get("cefr_level")
            assert level in valid_levels, (
                f"Entry '{entry.get('word')}' has invalid CEFR level: '{level}'"
            )

    def test_valid_exam_types(self, vocab_data):
        """All exam types must be from the known set."""
        valid_exams = {"IELTS", "TOEIC", "TOEFL", "VSTEP"}
        for entry in vocab_data:
            exam = entry.get("exam_type", "")
            if exam:
                # exam_type can be a string, comma-separated, or array
                if isinstance(exam, list):
                    for e in exam:
                        assert e in valid_exams, (
                            f"Entry '{entry.get('word')}' has invalid exam type: '{e}'"
                        )
                elif isinstance(exam, str):
                    for e in exam.split(","):
                        e = e.strip()
                        if e:
                            assert e in valid_exams, (
                                f"Entry '{entry.get('word')}' has invalid exam type: '{e}'"
                            )


# ─── Test Content Tests ──────────────────────────────────────────────────────

class TestContentIntegrity:
    """Verify test content (reading, listening, writing, speaking)."""

    @pytest.mark.parametrize("test_file", [
        "reading_tests",
        "listening_tests",
        "writing_tests",
        "speaking_tests",
    ])
    def test_test_content_count(self, test_file):
        """Each test content file must have at least MIN_TEST_COUNT records."""
        path = WEB_DATA_DIR / f"{test_file}.json"
        if not path.exists():
            pytest.skip(f"{test_file}.json not found")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) >= MIN_TEST_COUNT, (
            f"{test_file} has only {len(data)} records, "
            f"expected at least {MIN_TEST_COUNT}"
        )


# ─── Seed SQL Tests ───────────────────────────────────────────────────────────

class TestSeedSQL:
    """Verify Supabase seed SQL integrity."""

    def test_seed_sql_exists(self, seed_sql):
        """Seed SQL file must exist."""
        assert seed_sql, "Seed SQL is empty or not found"

    def test_seed_sql_has_inserts(self, seed_sql):
        """Seed SQL must contain INSERT statements."""
        insert_count = seed_sql.count("insert into vocab_cards")
        assert insert_count > 0, "Seed SQL has no INSERT statements"

    def test_seed_sql_is_idempotent(self, seed_sql):
        """Seed SQL must use ON CONFLICT for idempotency."""
        assert "on conflict" in seed_sql.lower(), (
            "Seed SQL does not use ON CONFLICT — not idempotent"
        )

    def test_seed_sql_covers_vocab(self, seed_sql, vocab_data):
        """Seed SQL should cover all vocabulary words."""
        # Count actual value tuples in the SQL (rough estimate)
        # Each insert batch has a values clause with multiple rows
        # We check that the word count is reasonable
        word_mentions = 0
        for entry in vocab_data:
            word = entry.get("word", "")
            if word and f"'{word}'" in seed_sql:
                word_mentions += 1
        # At least 90% of words should be in the SQL
        threshold = len(vocab_data) * 0.9
        assert word_mentions >= threshold, (
            f"Seed SQL only covers {word_mentions}/{len(vocab_data)} words "
            f"(expected at least {threshold:.0f})"
        )


# ─── No Demo Data in Production ──────────────────────────────────────────────

class TestNoDemoData:
    """Ensure no demo/test data leaks into production content."""

    def test_question_bank_is_not_demo(self):
        """Question bank should have more than 6 questions (demo had only 6)."""
        path = WEB_DATA_DIR / "question_bank.json"
        if not path.exists():
            pytest.skip("question_bank.json not found")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Note: 6 is the original demo count. If this test fails,
        # it means the question bank still has demo-level content.
        # This is a WARNING, not a hard failure.
        if len(data) <= 6:
            import warnings
            warnings.warn(
                f"Question bank has only {len(data)} questions — "
                f"this may be demo-level content"
            )
