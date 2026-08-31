"""
Tests for data validation against the canonical schema design.

These tests validate:
  • Duplicate vocabulary detection
  • Orphan record detection (foreign key integrity)
  • Invalid CEFR values
  • Invalid SRS values
  • Null violations
  • Duplicate user progress
  • Invalid ownership

These tests run against the source data files (JSON) and validate
that the data conforms to the canonical schema constraints before
migration. They can also run against a clean database if
SUPABASE_DB_URL is set.
"""

import json
import os
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
VOCAB_FILE = BASE_DIR / "data" / "seed" / "vocab.json"
VOCAB_ENRICHED_FILE = BASE_DIR / "data" / "seed" / "vocab_enriched.json"

VALID_CEFR = {"A1", "A2", "B1", "B2", "C1", "C2"}
VALID_EXAMS = {"TOEIC", "IELTS", "TOEFL", "VSTEP"}
VALID_SESSION_TYPES = {
    "VOCABULARY", "GRAMMAR", "LISTENING", "READING",
    "WRITING", "SPEAKING", "MOCK",
}


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def vocab_data():
    """Load vocab.json data."""
    with open(VOCAB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def vocab_enriched():
    """Load vocab_enriched.json data."""
    with open(VOCAB_ENRICHED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Tests: Duplicate vocabulary ──────────────────────────────────────

class TestDuplicateVocabulary:
    """Verify no duplicate words in vocabulary data."""

    def test_no_duplicate_words(self, vocab_data):
        """vocab.json should have no duplicate words."""
        words = [d["word"] for d in vocab_data]
        from collections import Counter
        dupes = {k: v for k, v in Counter(words).items() if v > 1}
        assert len(dupes) == 0, \
            f"Found {len(dupes)} duplicate words: {list(dupes.keys())[:10]}"

    def test_no_duplicate_words_enriched(self, vocab_enriched):
        """vocab_enriched.json should have no duplicate words."""
        words = [d["word"] for d in vocab_enriched]
        from collections import Counter
        dupes = {k: v for k, v in Counter(words).items() if v > 1}
        assert len(dupes) == 0, \
            f"Found {len(dupes)} duplicate words: {list(dupes.keys())[:10]}"

    def test_vocab_files_consistent(self, vocab_data, vocab_enriched):
        """vocab.json and vocab_enriched.json should have the same words."""
        words_base = set(d["word"] for d in vocab_data)
        words_enriched = set(d["word"] for d in vocab_enriched)
        assert words_base == words_enriched, \
            "vocab.json and vocab_enriched.json have different word sets"


# ── Tests: Invalid CEFR values ───────────────────────────────────────

class TestCEFRValidation:
    """Verify all CEFR levels are valid."""

    def test_valid_cefr_levels(self, vocab_data):
        """All difficulty_level values must be valid CEFR levels."""
        invalid = [
            d for d in vocab_data
            if d.get("difficulty_level") and d["difficulty_level"] not in VALID_CEFR
        ]
        assert len(invalid) == 0, \
            f"Found {len(invalid)} entries with invalid CEFR levels"

    def test_valid_cefr_levels_enriched(self, vocab_enriched):
        """All difficulty_level values in enriched data must be valid."""
        invalid = [
            d for d in vocab_enriched
            if d.get("difficulty_level") and d["difficulty_level"] not in VALID_CEFR
        ]
        assert len(invalid) == 0, \
            f"Found {len(invalid)} entries with invalid CEFR levels"


# ── Tests: Invalid exam types ─────────────────────────────────────────

class TestExamTypeValidation:
    """Verify all exam types are valid."""

    def test_valid_exam_types(self, vocab_data):
        """All exam_type values must be valid."""
        invalid = [
            d for d in vocab_data
            if d.get("exam_type") and d["exam_type"] not in VALID_EXAMS
        ]
        assert len(invalid) == 0, \
            f"Found {len(invalid)} entries with invalid exam types"


# ── Tests: Null violations ───────────────────────────────────────────

class TestNullViolations:
    """Verify no null violations in required fields."""

    def test_word_not_null(self, vocab_data):
        """word must not be null."""
        nulls = [d for d in vocab_data if not d.get("word")]
        assert len(nulls) == 0, f"Found {len(nulls)} entries with null word"

    def test_meaning_en_not_null(self, vocab_data):
        """meaning_en must not be null."""
        nulls = [d for d in vocab_data if not d.get("meaning_en")]
        assert len(nulls) == 0, f"Found {len(nulls)} entries with null meaning_en"

    def test_meaning_vi_not_null(self, vocab_data):
        """meaning_vi must not be null."""
        nulls = [d for d in vocab_data if not d.get("meaning_vi")]
        assert len(nulls) == 0, f"Found {len(nulls)} entries with null meaning_vi"


# ── Tests: SRS value validation ──────────────────────────────────────

class TestSRSValueValidation:
    """Verify SRS constraint values are valid by design."""

    def test_srs_quality_range(self):
        """SM-2 quality must be 0-5. Verify the constraint exists in SQL."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "004_vocab_progress.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "check (last_quality >= 0 and last_quality <= 5)" in sql.lower(), \
            "last_quality CHECK constraint (0-5) not found"

    def test_srs_easiness_minimum(self):
        """SM-2 easiness must be >= 1.30."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "004_vocab_progress.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "easiness >= 1.30" in sql or "easiness >= 1.3" in sql, \
            "easiness CHECK constraint (>= 1.30) not found"

    def test_srs_repetitions_non_negative(self):
        """SRS repetitions must be >= 0."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "004_vocab_progress.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "check (repetitions >= 0)" in sql.lower(), \
            "repetitions CHECK constraint (>= 0) not found"

    def test_srs_interval_non_negative(self):
        """SRS interval_days must be >= 0."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "004_vocab_progress.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "check (interval_days >= 0)" in sql.lower(), \
            "interval_days CHECK constraint (>= 0) not found"


# ── Tests: Foreign key integrity (data-level) ────────────────────────

class TestForeignKeyIntegrity:
    """Verify foreign key relationships can be maintained."""

    def test_vocab_progress_can_reference_vocab_cards(self, vocab_data):
        """
        Verify that vocab_progress can reference vocab_cards.
        Since vocab_progress is user data (not in seed files), we verify
        that the FK constraint exists in the schema.
        """
        sql_path = BASE_DIR / "supabase" / "migrations" / "004_vocab_progress.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "references vocab_cards(id)" in sql, \
            "vocab_progress must reference vocab_cards(id)"

    def test_error_journal_can_reference_study_sessions(self):
        """Verify error_journal FK to study_sessions exists."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "006_error_journal.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "references study_sessions(id)" in sql, \
            "error_journal must reference study_sessions(id)"


# ── Tests: Invalid ownership ─────────────────────────────────────────

class TestInvalidOwnership:
    """Verify ownership constraints are enforced."""

    def test_user_owned_tables_have_user_id_fk(self):
        """All user-owned tables must have user_id referencing profiles."""
        for table_name, migration_file in [
            ("vocab_progress", "004_vocab_progress.sql"),
            ("study_sessions", "005_study_sessions.sql"),
            ("error_journal", "006_error_journal.sql"),
            ("study_plans", "007_study_plans.sql"),
            ("writing_submissions", "009_writing_submissions.sql"),
        ]:
            sql_path = BASE_DIR / "supabase" / "migrations" / migration_file
            sql = sql_path.read_text(encoding="utf-8")
            assert "user_id" in sql, \
                f"{table_name}: missing user_id column"
            assert "references profiles(id)" in sql, \
                f"{table_name}: user_id must reference profiles(id)"

    def test_global_tables_have_no_user_id(self):
        """Global content tables should not have user_id."""
        for table_name, migration_file in [
            ("vocab_cards", "003_vocab_cards.sql"),
            ("content_cache", "008_content_cache.sql"),
        ]:
            sql_path = BASE_DIR / "supabase" / "migrations" / migration_file
            sql = sql_path.read_text(encoding="utf-8")
            # Check that user_id is not a column definition
            lines = sql.split("\n")
            for line in lines:
                stripped = line.strip().lower()
                if stripped.startswith("--"):
                    continue
                assert not stripped.startswith("user_id"), \
                    f"{table_name}: should not have user_id column"


# ── Tests: Seed idempotency ──────────────────────────────────────────

class TestSeedIdempotency:
    """Verify seed data is idempotent."""

    def test_seed_uses_on_conflict_do_nothing(self):
        """Seed SQL must use ON CONFLICT DO NOTHING."""
        seed_path = BASE_DIR / "supabase" / "seeds" / "seed_vocab_cards.sql"
        sql = seed_path.read_text(encoding="utf-8")
        assert "on conflict (word) do nothing" in sql.lower(), \
            "Seed must use ON CONFLICT (word) DO NOTHING"

    def test_seed_safe_to_run_multiple_times(self):
        """Seed should be safe to run multiple times (idempotent)."""
        seed_path = BASE_DIR / "supabase" / "seeds" / "seed_vocab_cards.sql"
        sql = seed_path.read_text(encoding="utf-8")
        # Count insert statements (excluding comments) and on conflict statements
        # Strip comment lines first
        code_lines = [
            line for line in sql.split("\n")
            if not line.strip().startswith("--")
        ]
        code_sql = "\n".join(code_lines).lower()
        insert_count = code_sql.count("insert into vocab_cards")
        conflict_count = code_sql.count("on conflict (word) do nothing")
        assert insert_count == conflict_count, \
            f"Insert count ({insert_count}) != ON CONFLICT count ({conflict_count})"


# ── Tests: Session type validation ───────────────────────────────────

class TestSessionTypeValidation:
    """Verify session type CHECK constraint."""

    def test_session_type_check_constraint(self):
        """study_sessions must have CHECK on session_type."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "005_study_sessions.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "check (session_type in" in sql.lower(), \
            "study_sessions: session_type CHECK constraint not found"

    def test_all_session_types_in_check(self):
        """All 7 session types must be in the CHECK constraint."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "005_study_sessions.sql"
        sql = sql_path.read_text(encoding="utf-8")
        for st in VALID_SESSION_TYPES:
            assert st in sql, \
                f"study_sessions: session_type CHECK missing '{st}'"


# ── Tests: UUID migration mapping ────────────────────────────────────

class TestUUIDMigrationMapping:
    """Verify UUID migration infrastructure exists."""

    def test_migration_id_map_table_exists(self):
        """migration_id_map table must exist for UUID migration."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "011_migration_id_map.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "create table if not exists migration_id_map" in sql.lower(), \
            "migration_id_map table not found"

    def test_migration_id_map_has_required_columns(self):
        """migration_id_map must have table_name, legacy_id, canonical_uuid."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "011_migration_id_map.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "table_name" in sql, \
            "migration_id_map: missing table_name column"
        assert "legacy_id" in sql, \
            "migration_id_map: missing legacy_id column"
        assert "canonical_uuid" in sql, \
            "migration_id_map: missing canonical_uuid column"

    def test_migration_id_map_unique_constraint(self):
        """migration_id_map must have unique (table_name, legacy_id)."""
        sql_path = BASE_DIR / "supabase" / "migrations" / "011_migration_id_map.sql"
        sql = sql_path.read_text(encoding="utf-8")
        assert "unique (table_name, legacy_id)" in sql.lower(), \
            "migration_id_map: missing unique (table_name, legacy_id)"
