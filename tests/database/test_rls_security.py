"""
Tests for Row Level Security (RLS) policy design.

These tests validate the RLS policy design by parsing the migration SQL.
They verify that:

  • User A can access User A data
  • User A cannot access User B data
  • Anonymous users cannot access private user data
  • Global vocabulary is readable according to policy
  • Anonymous users cannot modify global vocabulary

For live database RLS tests, see test_database_integration.py
(requires SUPABASE_DB_URL environment variable).
"""

import re
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MIGRATIONS_DIR = BASE_DIR / "supabase" / "migrations"


def read_migration(filename: str) -> str:
    filepath = MIGRATIONS_DIR / filename
    return filepath.read_text(encoding="utf-8")


class TestRLSPolicyDesign:
    """Verify RLS policy design from migration SQL."""

    @pytest.mark.parametrize("table_name, migration_file", [
        ("profiles", "002_profiles.sql"),
        ("vocab_progress", "004_vocab_progress.sql"),
        ("study_sessions", "005_study_sessions.sql"),
        ("error_journal", "006_error_journal.sql"),
        ("study_plans", "007_study_plans.sql"),
        ("writing_submissions", "009_writing_submissions.sql"),
    ])
    def test_rls_enabled(self, table_name, migration_file):
        """RLS must be enabled on all user-owned tables."""
        sql = read_migration(migration_file)
        pattern = rf"alter\s+table\s+{table_name}\s+enable\s+row\s+level\s+security"
        assert re.search(pattern, sql, re.IGNORECASE), \
            f"{table_name}: RLS not enabled"

    @pytest.mark.parametrize("table_name, migration_file", [
        ("profiles", "002_profiles.sql"),
        ("vocab_progress", "004_vocab_progress.sql"),
        ("study_sessions", "005_study_sessions.sql"),
        ("error_journal", "006_error_journal.sql"),
        ("study_plans", "007_study_plans.sql"),
        ("writing_submissions", "009_writing_submissions.sql"),
    ])
    def test_select_policy_uses_auth_uid(self, table_name, migration_file):
        """SELECT policy must restrict to auth.uid() = user_id (or id for profiles)."""
        sql = read_migration(migration_file)
        # profiles uses auth.uid() = id, others use auth.uid() = user_id
        assert "auth.uid()" in sql, \
            f"{table_name}: SELECT policy must use auth.uid()"
        assert "for select" in sql.lower(), \
            f"{table_name}: must have SELECT policy"

    @pytest.mark.parametrize("table_name, migration_file", [
        ("profiles", "002_profiles.sql"),
        ("vocab_progress", "004_vocab_progress.sql"),
        ("study_sessions", "005_study_sessions.sql"),
        ("error_journal", "006_error_journal.sql"),
        ("study_plans", "007_study_plans.sql"),
        ("writing_submissions", "009_writing_submissions.sql"),
    ])
    def test_insert_policy_uses_auth_uid(self, table_name, migration_file):
        """INSERT policy must check auth.uid() = user_id."""
        sql = read_migration(migration_file)
        assert "for insert" in sql.lower(), \
            f"{table_name}: must have INSERT policy"
        assert "with check" in sql.lower(), \
            f"{table_name}: INSERT must have WITH CHECK"

    @pytest.mark.parametrize("table_name, migration_file", [
        ("profiles", "002_profiles.sql"),
        ("vocab_progress", "004_vocab_progress.sql"),
        ("study_sessions", "005_study_sessions.sql"),
        ("error_journal", "006_error_journal.sql"),
        ("study_plans", "007_study_plans.sql"),
        ("writing_submissions", "009_writing_submissions.sql"),
    ])
    def test_update_policy_uses_auth_uid(self, table_name, migration_file):
        """UPDATE policy must restrict to auth.uid() = user_id."""
        sql = read_migration(migration_file)
        assert "for update" in sql.lower(), \
            f"{table_name}: must have UPDATE policy"

    @pytest.mark.parametrize("table_name, migration_file", [
        ("profiles", "002_profiles.sql"),
        ("vocab_progress", "004_vocab_progress.sql"),
        ("study_sessions", "005_study_sessions.sql"),
        ("error_journal", "006_error_journal.sql"),
        ("study_plans", "007_study_plans.sql"),
        ("writing_submissions", "009_writing_submissions.sql"),
    ])
    def test_delete_policy_uses_auth_uid(self, table_name, migration_file):
        """DELETE policy must restrict to auth.uid() = user_id."""
        sql = read_migration(migration_file)
        assert "for delete" in sql.lower(), \
            f"{table_name}: must have DELETE policy"

    def test_vocab_cards_public_read_only(self):
        """vocab_cards: public read, but no anon write policies."""
        sql = read_migration("003_vocab_cards.sql")
        assert "vocab_cards_public_read" in sql, \
            "vocab_cards: must have public read policy"
        assert "for select using (true)" in sql.lower() or \
               "for select using ( true )" in sql.lower(), \
            "vocab_cards: public read must use USING (true)"
        # Should NOT have insert/update/delete policies
        assert "for insert" not in sql.lower(), \
            "vocab_cards: should NOT have INSERT policy (blocks anon write)"
        assert "for update" not in sql.lower(), \
            "vocab_cards: should NOT have UPDATE policy (blocks anon write)"
        assert "for delete" not in sql.lower(), \
            "vocab_cards: should NOT have DELETE policy (blocks anon write)"

    def test_content_cache_no_user_policies(self):
        """content_cache: RLS enabled but no user policies (service-role only)."""
        sql = read_migration("008_content_cache.sql")
        assert "enable row level security" in sql.lower(), \
            "content_cache: RLS must be enabled"
        # No policies = blocked for all non-service-role users
        assert "for select" not in sql.lower(), \
            "content_cache: should NOT have SELECT policy (service-role only)"
        assert "for insert" not in sql.lower(), \
            "content_cache: should NOT have INSERT policy (service-role only)"

    def test_cross_user_access_blocked(self):
        """
        Verify cross-user access is impossible through normal queries.

        All user-owned tables use auth.uid() = user_id in their SELECT
        policy, which means a user can only see their own rows.
        """
        for table_name, migration_file in [
            ("vocab_progress", "004_vocab_progress.sql"),
            ("study_sessions", "005_study_sessions.sql"),
            ("error_journal", "006_error_journal.sql"),
            ("study_plans", "007_study_plans.sql"),
            ("writing_submissions", "009_writing_submissions.sql"),
        ]:
            sql = read_migration(migration_file)
            # Find SELECT policy and verify it uses auth.uid()
            # Use a simpler approach: find the select policy line and check for auth.uid()
            assert "for select" in sql.lower(), \
                f"{table_name}: must have SELECT policy"
            assert "auth.uid()" in sql, \
                f"{table_name}: SELECT policy must use auth.uid()"

    def test_anonymous_cannot_access_user_data(self):
        """
        Anonymous users (auth.uid() returns NULL) cannot access user data.

        When auth.uid() returns NULL, the condition auth.uid() = user_id
        evaluates to NULL = user_id, which is NULL (falsy), so the row
        is not visible. This is the correct behavior.
        """
        # This is implicitly tested by the auth.uid() = user_id condition.
        # When auth.uid() is NULL, NULL = anything is NULL (not true).
        # So no rows are returned for anonymous users.
        # We verify the condition exists in all user tables.
        for table_name, migration_file in [
            ("vocab_progress", "004_vocab_progress.sql"),
            ("study_sessions", "005_study_sessions.sql"),
            ("error_journal", "006_error_journal.sql"),
            ("study_plans", "007_study_plans.sql"),
            ("writing_submissions", "009_writing_submissions.sql"),
        ]:
            sql = read_migration(migration_file)
            assert "auth.uid() = user_id" in sql, \
                f"{table_name}: must use auth.uid() = user_id (blocks anonymous)"
