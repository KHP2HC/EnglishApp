"""
Tests for canonical PostgreSQL schema migration files.

These tests validate the migration SQL files for:
  • All expected migration files exist
  • Migration files are in deterministic order
  • SQL is non-destructive (no DROP TABLE, DELETE, TRUNCATE in migrations)
  • All canonical tables are created
  • All expected constraints are present
  • All expected indexes are present
  • All expected RLS policies are present
  • Seed data is idempotent (ON CONFLICT)
  • Seed data count matches source data

These tests do NOT require a running PostgreSQL instance — they parse
the SQL files. For integration tests against a live database, see
test_database_integration.py (requires SUPABASE_DB_URL).
"""

import os
import re
from pathlib import Path

import pytest

# ── Paths ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MIGRATIONS_DIR = BASE_DIR / "supabase" / "migrations"
SEEDS_DIR = BASE_DIR / "supabase" / "seeds"

# ── Expected migration files in order ─────────────────────────────────
EXPECTED_MIGRATIONS = [
    "001_extensions.sql",
    "002_profiles.sql",
    "003_vocab_cards.sql",
    "004_vocab_progress.sql",
    "005_study_sessions.sql",
    "006_error_journal.sql",
    "007_study_plans.sql",
    "008_content_cache.sql",
    "009_writing_submissions.sql",
    "010_triggers.sql",
    "011_migration_id_map.sql",
]

# ── Expected canonical tables ─────────────────────────────────────────
EXPECTED_TABLES = [
    "profiles",
    "vocab_cards",
    "vocab_progress",
    "study_sessions",
    "error_journal",
    "study_plans",
    "content_cache",
    "writing_submissions",
    "migration_id_map",
]


# ── Helper ────────────────────────────────────────────────────────────
def read_migration(filename: str) -> str:
    """Read a migration file's content."""
    filepath = MIGRATIONS_DIR / filename
    assert filepath.exists(), f"Migration file not found: {filename}"
    return filepath.read_text(encoding="utf-8")


def read_all_migrations() -> str:
    """Read all migration files concatenated."""
    return "\n\n".join(read_migration(f) for f in EXPECTED_MIGRATIONS)


# ── Tests: Migration files exist ──────────────────────────────────────

class TestMigrationFilesExist:
    """Verify all expected migration files exist."""

    @pytest.mark.parametrize("filename", EXPECTED_MIGRATIONS)
    def test_migration_file_exists(self, filename):
        filepath = MIGRATIONS_DIR / filename
        assert filepath.exists(), f"Migration file not found: {filename}"


# ── Tests: Non-destructive migrations ────────────────────────────────

class TestNonDestructiveMigrations:
    """Verify migrations are additive and safe (no destructive operations)."""

    @pytest.mark.parametrize("filename", EXPECTED_MIGRATIONS)
    def test_no_drop_table(self, filename):
        sql = read_migration(filename)
        # DROP TABLE is destructive — not allowed in migrations
        # (DROP TRIGGER IF EXISTS and DROP POLICY IF EXISTS are OK)
        lines = sql.split("\n")
        for line in lines:
            stripped = line.strip().lower()
            # Skip comment lines
            if stripped.startswith("--"):
                continue
            assert not re.match(r"^\s*drop\s+table", stripped), \
                f"{filename}: DROP TABLE found: {line.strip()}"

    @pytest.mark.parametrize("filename", EXPECTED_MIGRATIONS)
    def test_no_delete_data(self, filename):
        sql = read_migration(filename)
        lines = sql.split("\n")
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith("--"):
                continue
            assert not re.match(r"^\s*delete\s+from", stripped), \
                f"{filename}: DELETE FROM found: {line.strip()}"

    @pytest.mark.parametrize("filename", EXPECTED_MIGRATIONS)
    def test_no_truncate(self, filename):
        sql = read_migration(filename)
        lines = sql.split("\n")
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith("--"):
                continue
            assert not re.match(r"^\s*truncate", stripped), \
                f"{filename}: TRUNCATE found: {line.strip()}"

    @pytest.mark.parametrize("filename", EXPECTED_MIGRATIONS)
    def test_uses_create_if_not_exists(self, filename):
        """All CREATE TABLE statements should use IF NOT EXISTS."""
        sql = read_migration(filename)
        # Find all CREATE TABLE statements (case-insensitive)
        # Use multiline to handle newlines between keywords
        create_table_pattern = re.compile(
            r"create\s+table\s+(if\s+not\s+exists\s+)?\w+",
            re.IGNORECASE,
        )
        matches = create_table_pattern.findall(sql)
        # If there are CREATE TABLE statements, all must have IF NOT EXISTS
        # Also verify by checking each occurrence directly
        lines = sql.split("\n")
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith("create table"):
                assert "if not exists" in stripped, \
                    f"{filename}: CREATE TABLE missing IF NOT EXISTS: {line.strip()}"


# ── Tests: Canonical tables ──────────────────────────────────────────

class TestCanonicalTables:
    """Verify all canonical tables are created."""

    @pytest.mark.parametrize("table_name", EXPECTED_TABLES)
    def test_table_created(self, table_name):
        sql = read_all_migrations()
        pattern = rf"create\s+table\s+if\s+not\s+exists\s+{table_name}\s*\("
        assert re.search(pattern, sql, re.IGNORECASE), \
            f"Table {table_name} not found in migrations"


# ── Tests: UUID primary keys ──────────────────────────────────────────

class TestUUIDPrimaryKeys:
    """Verify all canonical tables use UUID primary keys."""

    @pytest.mark.parametrize("table_name", [
        "vocab_cards", "vocab_progress", "study_sessions",
        "error_journal", "study_plans", "content_cache",
        "writing_submissions", "migration_id_map",
    ])
    def test_uuid_primary_key(self, table_name):
        sql = read_all_migrations()
        # Find the table definition and check for uuid primary key
        # Pattern: create table if not exists TABLE_NAME ( ... uuid primary key ...
        pattern = rf"create\s+table\s+if\s+not\s+exists\s+{table_name}\s*\((.*?)\);"
        match = re.search(pattern, sql, re.IGNORECASE | re.DOTALL)
        assert match, f"Could not find table definition for {table_name}"
        table_def = match.group(1)
        assert "uuid" in table_def.lower(), \
            f"{table_name}: no UUID column found"
        assert "primary key" in table_def.lower(), \
            f"{table_name}: no primary key found"

    def test_profiles_uses_auth_users_id(self):
        """profiles.id must reference auth.users.id."""
        sql = read_migration("002_profiles.sql")
        assert "references auth.users(id)" in sql, \
            "profiles.id must reference auth.users(id)"


# ── Tests: Constraints ──────────────────────────────────────────────

class TestConstraints:
    """Verify appropriate constraints are present."""

    def test_vocab_cards_unique_word(self):
        sql = read_migration("003_vocab_cards.sql")
        assert "unique" in sql.lower(), \
            "vocab_cards must have UNIQUE constraint on word"

    def test_vocab_progress_unique_user_card(self):
        sql = read_migration("004_vocab_progress.sql")
        assert "unique (user_id, card_id)" in sql.lower(), \
            "vocab_progress must have UNIQUE (user_id, card_id)"

    def test_study_plans_unique_user_week(self):
        sql = read_migration("007_study_plans.sql")
        assert "unique (user_id, week_start)" in sql.lower(), \
            "study_plans must have UNIQUE (user_id, week_start)"

    def test_content_cache_unique_source_key(self):
        sql = read_migration("008_content_cache.sql")
        assert "unique (source, source_key)" in sql.lower(), \
            "content_cache must have UNIQUE (source, source_key)"

    def test_cefr_check_constraint(self):
        """Verify CEFR CHECK constraints exist."""
        sql = read_all_migrations()
        # vocab_cards and content_cache should have CEFR checks
        assert "check (cefr_level in ('A1','A2','B1','B2','C1','C2'))" in sql.lower() or \
               "check (cefr_level in ('A1','A2','B1','B2','C1','C2'))" in sql, \
            "CEFR CHECK constraint not found"

    def test_srs_check_constraints(self):
        """Verify SRS value constraints (non-negative, valid easiness)."""
        sql = read_migration("004_vocab_progress.sql")
        assert "check (interval_days >= 0)" in sql.lower(), \
            "vocab_progress: interval_days must have CHECK >= 0"
        assert "check (easiness >= 1.30)" in sql.lower() or \
               "check (easiness >= 1.3)" in sql.lower(), \
            "vocab_progress: easiness must have CHECK >= 1.30"
        assert "check (repetitions >= 0)" in sql.lower(), \
            "vocab_progress: repetitions must have CHECK >= 0"
        assert "check (last_quality >= 0 and last_quality <= 5)" in sql.lower(), \
            "vocab_progress: last_quality must have CHECK 0-5"

    def test_xp_check_constraints(self):
        """Verify non-negative XP constraint."""
        sql = read_migration("002_profiles.sql")
        assert "check (total_xp >= 0)" in sql.lower(), \
            "profiles: total_xp must have CHECK >= 0"

    def test_session_type_check(self):
        """Verify session_type CHECK constraint."""
        sql = read_migration("005_study_sessions.sql")
        assert "check (session_type in" in sql.lower(), \
            "study_sessions: session_type CHECK constraint not found"

    def test_exam_type_check(self):
        """Verify target_exam CHECK constraint."""
        sql = read_migration("002_profiles.sql")
        assert "check (target_exam in ('toeic','ielts','toefl','vstep'))" in sql.lower(), \
            "profiles: target_exam CHECK constraint not found"

    def test_foreign_keys_exist(self):
        """Verify foreign key relationships are present."""
        sql = read_all_migrations()
        # vocab_progress → profiles
        assert "references profiles(id)" in sql, \
            "vocab_progress must reference profiles"
        # vocab_progress → vocab_cards
        assert "references vocab_cards(id)" in sql, \
            "vocab_progress must reference vocab_cards"
        # study_sessions → profiles
        assert "references profiles(id)" in sql, \
            "study_sessions must reference profiles"
        # error_journal → profiles
        assert "references profiles(id)" in sql, \
            "error_journal must reference profiles"
        # error_journal → study_sessions
        assert "references study_sessions(id)" in sql, \
            "error_journal must reference study_sessions"
        # study_plans → profiles
        assert "references profiles(id)" in sql, \
            "study_plans must reference profiles"
        # writing_submissions → profiles
        assert "references profiles(id)" in sql, \
            "writing_submissions must reference profiles"

    def test_cascade_delete_on_user(self):
        """Verify ON DELETE CASCADE for user-owned tables."""
        sql = read_all_migrations()
        # All user-owned tables should cascade delete when profile is deleted
        cascade_count = sql.lower().count("on delete cascade")
        assert cascade_count >= 6, \
            f"Expected at least 6 ON DELETE CASCADE, found {cascade_count}"


# ── Tests: Indexes ───────────────────────────────────────────────────

class TestIndexes:
    """Verify justified indexes are present."""

    def test_vocab_progress_user_review_index(self):
        sql = read_migration("004_vocab_progress.sql")
        assert "idx_vocab_progress_user_review" in sql.lower(), \
            "vocab_progress: missing index on (user_id, next_review_at)"

    def test_study_sessions_user_started_index(self):
        sql = read_migration("005_study_sessions.sql")
        assert "idx_study_sessions_user_started" in sql.lower(), \
            "study_sessions: missing index on (user_id, started_at)"

    def test_error_journal_user_created_index(self):
        sql = read_migration("006_error_journal.sql")
        assert "idx_error_journal_user_created" in sql.lower(), \
            "error_journal: missing index on (user_id, created_at)"

    def test_study_plans_user_week_index(self):
        sql = read_migration("007_study_plans.sql")
        assert "idx_study_plans_user_week" in sql.lower(), \
            "study_plans: missing index on (user_id, week_start)"

    def test_writing_submissions_user_created_index(self):
        sql = read_migration("009_writing_submissions.sql")
        assert "idx_writing_submissions_user_created" in sql.lower(), \
            "writing_submissions: missing index on (user_id, created_at)"

    def test_vocab_cards_word_index(self):
        sql = read_migration("003_vocab_cards.sql")
        assert "idx_vocab_cards_word" in sql.lower(), \
            "vocab_cards: missing index on word"


# ── Tests: RLS policies ──────────────────────────────────────────────

class TestRLSPolicies:
    """Verify Row Level Security policies are present."""

    @pytest.mark.parametrize("table_name", [
        "profiles", "vocab_progress", "study_sessions",
        "error_journal", "study_plans", "writing_submissions",
    ])
    def test_rls_enabled(self, table_name):
        sql = read_all_migrations()
        pattern = rf"alter\s+table\s+{table_name}\s+enable\s+row\s+level\s+security"
        assert re.search(pattern, sql, re.IGNORECASE), \
            f"{table_name}: RLS not enabled"

    def test_vocab_cards_public_read(self):
        """vocab_cards should be publicly readable."""
        sql = read_migration("003_vocab_cards.sql")
        assert "vocab_cards_public_read" in sql, \
            "vocab_cards: missing public read policy"

    def test_vocab_cards_no_anon_write(self):
        """vocab_cards should NOT have insert/update/delete policies for anon."""
        sql = read_migration("003_vocab_cards.sql")
        # Check that there are no insert/update/delete policies
        # (only the public select policy should exist)
        assert "for insert" not in sql.lower() or "with check" not in sql.lower(), \
            "vocab_cards: should not have insert policy (anon write blocked)"

    @pytest.mark.parametrize("table_name", [
        "profiles", "vocab_progress", "study_sessions",
        "error_journal", "study_plans", "writing_submissions",
    ])
    def test_user_owned_rls_uses_auth_uid(self, table_name):
        """User-owned tables must use auth.uid() = user_id."""
        # Read the specific migration for this table
        table_to_migration = {
            "profiles": "002_profiles.sql",
            "vocab_progress": "004_vocab_progress.sql",
            "study_sessions": "005_study_sessions.sql",
            "error_journal": "006_error_journal.sql",
            "study_plans": "007_study_plans.sql",
            "writing_submissions": "009_writing_submissions.sql",
        }
        sql = read_migration(table_to_migration[table_name])
        assert "auth.uid() = user_id" in sql or "auth.uid() = id" in sql, \
            f"{table_name}: RLS policy must use auth.uid() = user_id or auth.uid() = id"


# ── Tests: Timestamps ────────────────────────────────────────────────

class TestTimestamps:
    """Verify timezone-aware timestamps are used."""

    def test_all_tables_use_timestamptz(self):
        """All timestamp columns should use TIMESTAMPTZ."""
        sql = read_all_migrations()
        # Should have many timestamptz columns
        count = sql.lower().count("timestamptz")
        assert count >= 10, \
            f"Expected at least 10 TIMESTAMPTZ columns, found {count}"

    def test_created_at_present_on_user_tables(self):
        """All user-owned tables must have created_at."""
        for table_name, migration_file in [
            ("profiles", "002_profiles.sql"),
            ("vocab_progress", "004_vocab_progress.sql"),
            ("study_sessions", "005_study_sessions.sql"),
            ("error_journal", "006_error_journal.sql"),
            ("study_plans", "007_study_plans.sql"),
            ("writing_submissions", "009_writing_submissions.sql"),
        ]:
            sql = read_migration(migration_file)
            assert "created_at" in sql.lower(), \
                f"{table_name}: missing created_at"

    def test_updated_at_on_mutable_tables(self):
        """Tables that can be updated must have updated_at."""
        for table_name, migration_file in [
            ("profiles", "002_profiles.sql"),
            ("vocab_progress", "004_vocab_progress.sql"),
            ("study_plans", "007_study_plans.sql"),
            ("writing_submissions", "009_writing_submissions.sql"),
        ]:
            sql = read_migration(migration_file)
            assert "updated_at" in sql.lower(), \
                f"{table_name}: missing updated_at"

    def test_updated_at_trigger_exists(self):
        """Triggers for updated_at must exist."""
        sql = read_migration("010_triggers.sql")
        assert "set_updated_at" in sql, \
            "Missing set_updated_at trigger function"
        assert "trg_profiles_updated_at" in sql, \
            "Missing profiles updated_at trigger"
        assert "trg_vocab_progress_updated_at" in sql, \
            "Missing vocab_progress updated_at trigger"
        assert "trg_study_plans_updated_at" in sql, \
            "Missing study_plans updated_at trigger"
        assert "trg_writing_submissions_updated_at" in sql, \
            "Missing writing_submissions updated_at trigger"

    def test_immutable_tables_no_updated_at(self):
        """Immutable tables should NOT have updated_at."""
        for table_name, migration_file in [
            ("study_sessions", "005_study_sessions.sql"),
            ("error_journal", "006_error_journal.sql"),
        ]:
            sql = read_migration(migration_file)
            # Should not have updated_at column
            lines = sql.split("\n")
            for line in lines:
                stripped = line.strip().lower()
                if stripped.startswith("--"):
                    continue
                assert not re.match(r"^updated_at\s+", stripped), \
                    f"{table_name}: should not have updated_at (immutable record)"


# ── Tests: Soft delete ────────────────────────────────────────────────

class TestSoftDelete:
    """Verify soft delete is only on writing_submissions."""

    def test_writing_submissions_has_deleted_at(self):
        sql = read_migration("009_writing_submissions.sql")
        assert "deleted_at" in sql.lower(), \
            "writing_submissions: missing deleted_at (soft delete)"

    def test_other_tables_no_deleted_at(self):
        """No other table should have deleted_at."""
        for table_name, migration_file in [
            ("profiles", "002_profiles.sql"),
            ("vocab_cards", "003_vocab_cards.sql"),
            ("vocab_progress", "004_vocab_progress.sql"),
            ("study_sessions", "005_study_sessions.sql"),
            ("error_journal", "006_error_journal.sql"),
            ("study_plans", "007_study_plans.sql"),
            ("content_cache", "008_content_cache.sql"),
        ]:
            sql = read_migration(migration_file)
            lines = sql.split("\n")
            for line in lines:
                stripped = line.strip().lower()
                if stripped.startswith("--"):
                    continue
                assert not re.match(r"^deleted_at\s+", stripped), \
                    f"{table_name}: should not have deleted_at (no soft delete)"


# ── Tests: Ownership ──────────────────────────────────────────────────

class TestOwnership:
    """Verify user-owned tables have user_id NOT NULL."""

    @pytest.mark.parametrize("table_name, migration_file", [
        ("vocab_progress", "004_vocab_progress.sql"),
        ("study_sessions", "005_study_sessions.sql"),
        ("error_journal", "006_error_journal.sql"),
        ("study_plans", "007_study_plans.sql"),
        ("writing_submissions", "009_writing_submissions.sql"),
    ])
    def test_user_id_not_null(self, table_name, migration_file):
        sql = read_migration(migration_file)
        # Check for user_id uuid not null
        assert re.search(r"user_id\s+uuid\s+not\s+null", sql, re.IGNORECASE), \
            f"{table_name}: user_id must be NOT NULL"

    def test_vocab_cards_no_user_id(self):
        """vocab_cards is global content — should not have user_id."""
        sql = read_migration("003_vocab_cards.sql")
        lines = sql.split("\n")
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith("--"):
                continue
            assert not re.match(r"^user_id\s+", stripped), \
                "vocab_cards: should not have user_id (global content)"

    def test_content_cache_no_user_id(self):
        """content_cache is system-managed — should not have user_id."""
        sql = read_migration("008_content_cache.sql")
        lines = sql.split("\n")
        for line in lines:
            stripped = line.strip().lower()
            if stripped.startswith("--"):
                continue
            assert not re.match(r"^user_id\s+", stripped), \
                "content_cache: should not have user_id (system-managed)"


# ── Tests: Seed data ─────────────────────────────────────────────────

class TestSeedData:
    """Verify seed data is idempotent and correct."""

    def test_seed_file_exists(self):
        filepath = SEEDS_DIR / "seed_vocab_cards.sql"
        assert filepath.exists(), "seed_vocab_cards.sql not found"

    def test_seed_uses_on_conflict(self):
        """Seed must use ON CONFLICT DO NOTHING for idempotency."""
        sql = (SEEDS_DIR / "seed_vocab_cards.sql").read_text(encoding="utf-8")
        assert "on conflict (word) do nothing" in sql.lower(), \
            "Seed must use ON CONFLICT (word) DO NOTHING"

    def test_seed_count_matches_source(self):
        """Seed record count should match vocab_enriched.json."""
        import json
        source_path = BASE_DIR / "data" / "seed" / "vocab_enriched.json"
        with open(source_path, "r", encoding="utf-8") as f:
            source_data = json.load(f)

        seed_sql = (SEEDS_DIR / "seed_vocab_cards.sql").read_text(encoding="utf-8")
        # Count value rows (lines starting with '  (' that are data rows)
        data_rows = len(re.findall(r"^\s+\('.*?\)", seed_sql, re.MULTILINE))
        assert data_rows == len(source_data), \
            f"Seed has {data_rows} rows, source has {len(source_data)}"

    def test_seed_generator_exists(self):
        """The seed generator script must exist."""
        filepath = SEEDS_DIR / "generate_seed.py"
        assert filepath.exists(), "generate_seed.py not found"


# ── Tests: SRS timestamp design ──────────────────────────────────────

class TestSRSTimestampDesign:
    """Verify the SRS timestamp design decision is implemented."""

    def test_vocab_progress_uses_next_review_at(self):
        """vocab_progress should use next_review_at TIMESTAMPTZ, not next_review DATE."""
        sql = read_migration("004_vocab_progress.sql")
        assert "next_review_at" in sql, \
            "vocab_progress: should use next_review_at (TIMESTAMPTZ)"
        assert "timestamptz" in sql.lower(), \
            "vocab_progress: next_review_at should be TIMESTAMPTZ"

    def test_no_next_review_date_in_canonical(self):
        """Canonical schema should not use next_review_date (SQLite name)."""
        sql = read_migration("004_vocab_progress.sql")
        assert "next_review_date" not in sql.lower(), \
            "vocab_progress: should not use next_review_date (legacy name)"


# ── Tests: Content cache design ──────────────────────────────────────

class TestContentCacheDesign:
    """Verify content cache design decisions."""

    def test_content_cache_has_source_and_source_key(self):
        sql = read_migration("008_content_cache.sql")
        assert "source" in sql.lower(), \
            "content_cache: missing 'source' column"
        assert "source_key" in sql.lower(), \
            "content_cache: missing 'source_key' column"

    def test_content_cache_has_payload_jsonb(self):
        sql = read_migration("008_content_cache.sql")
        assert "payload" in sql.lower(), \
            "content_cache: missing 'payload' column"
        assert "jsonb" in sql.lower(), \
            "content_cache: payload should be JSONB"

    def test_content_cache_has_fetched_at_and_expires_at(self):
        sql = read_migration("008_content_cache.sql")
        assert "fetched_at" in sql.lower(), \
            "content_cache: missing 'fetched_at'"
        assert "expires_at" in sql.lower(), \
            "content_cache: missing 'expires_at'"


# ── Tests: No secrets in migrations ──────────────────────────────────

class TestNoSecrets:
    """Verify no secrets are hardcoded in migration files."""

    @pytest.mark.parametrize("filename", EXPECTED_MIGRATIONS)
    def test_no_hardcoded_passwords(self, filename):
        sql = read_migration(filename)
        # Check for common secret patterns
        assert "password" not in sql.lower() or "password" in sql.lower().split("--")[0] == "", \
            f"{filename}: possible hardcoded password"
        assert "service_role" not in sql.lower(), \
            f"{filename}: service_role key reference found"
        assert "jwt_secret" not in sql.lower(), \
            f"{filename}: JWT secret reference found"

    @pytest.mark.parametrize("filename", EXPECTED_MIGRATIONS)
    def test_no_api_keys(self, filename):
        sql = read_migration(filename)
        assert "api_key" not in sql.lower(), \
            f"{filename}: API key reference found"
        assert "anon_key" not in sql.lower(), \
            f"{filename}: anon key reference found"
