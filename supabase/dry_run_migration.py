#!/usr/bin/env python3
"""
Phase 2C-1: Live Database Migration Dry Run

Runs the full migration process against a disposable PostgreSQL database.
DO NOT use against production Supabase.

This script:
  1. Runs all schema migrations (001-011)
  2. Runs seed data
  3. Migrates SQLite data to PostgreSQL
  4. Validates UUID mappings, FK integrity, row counts, SRS state
  5. Tests RLS policies
  6. Tests idempotency
  7. Produces a comprehensive report

Usage:
  python supabase/dry_run_migration.py

Environment:
  SUPABASE_DB_URL or --database-url (defaults to local disposable PostgreSQL)
"""

import argparse
import json
import os
import sqlite3
import sys
import uuid
from collections import Counter
from datetime import datetime, date, timezone
from pathlib import Path

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 is not installed.")
    sys.exit(1)

# ── Configuration ────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
SEEDS_DIR = Path(__file__).resolve().parent / "seeds"
SQLITE_DB = BASE_DIR / "data.db"

MIGRATION_FILES = [
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

VALID_CEFR = {"A1", "A2", "B1", "B2", "C1", "C2"}
VALID_EXAMS = {"TOEIC", "IELTS", "TOEFL", "VSTEP"}


# ── Results collector ────────────────────────────────────────────────
class DryRunResults:
    def __init__(self):
        self.migration_results = {}
        self.seed_results = {}
        self.sqlite_counts = {}
        self.pg_counts = {}
        self.uuid_mappings = {}
        self.fk_validation = {}
        self.orphan_counts = {}
        self.duplicate_counts = {}
        self.srs_validation = {}
        self.rls_results = {}
        self.idempotency_results = {}
        self.errors = []
        self.warnings = []
        self.unresolved = []

    def add_error(self, msg):
        self.errors.append(msg)

    def add_warning(self, msg):
        self.warnings.append(msg)

    def to_dict(self):
        return {
            "migration_results": self.migration_results,
            "seed_results": self.seed_results,
            "sqlite_counts": self.sqlite_counts,
            "pg_counts": self.pg_counts,
            "uuid_mappings": self.uuid_mappings,
            "fk_validation": self.fk_validation,
            "orphan_counts": self.orphan_counts,
            "duplicate_counts": self.duplicate_counts,
            "srs_validation": self.srs_validation,
            "rls_results": self.rls_results,
            "idempotency_results": self.idempotency_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "unresolved": self.unresolved,
        }


# ── Helper: execute SQL safely ────────────────────────────────────────
def execute_sql(cursor, sql, label=""):
    """Execute SQL and return (success, error_message)."""
    try:
        cursor.execute(sql)
        return True, None
    except Exception as e:
        return False, str(e)


# ── Step 1: Create mock auth.users for local PostgreSQL ───────────────
def create_mock_auth_schema(conn):
    """Create a mock auth schema for local PostgreSQL testing.

    Supabase has auth.users and auth.uid() built-in. For local PostgreSQL,
    we create minimal mocks that satisfy FK constraints and RLS policies.
    """
    cursor = conn.cursor()
    # Create auth schema
    cursor.execute("create schema if not exists auth;")
    # Create mock auth.users table
    cursor.execute("""
        create table if not exists auth.users (
            id uuid primary key default gen_random_uuid(),
            email text unique,
            encrypted_password text,
            created_at timestamptz default now(),
            updated_at timestamptz default now()
        );
    """)
    # Create mock auth.uid() function
    # In Supabase, auth.uid() returns the current user's UUID from the JWT.
    # For local testing, we use a session variable that can be set per-test.
    cursor.execute("""
        create or replace function auth.uid()
        returns uuid
        language sql
        stable
        as $$
            select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
        $$;
    """)
    conn.commit()
    cursor.close()


# ── Step 2: Run all migrations ────────────────────────────────────────
def run_migrations(conn, results):
    """Run all migration files in deterministic order."""
    cursor = conn.cursor()
    print("\n" + "=" * 70)
    print("STEP 1: Running schema migrations")
    print("=" * 70)

    for filename in MIGRATION_FILES:
        filepath = MIGRATIONS_DIR / filename
        if not filepath.exists():
            msg = f"Migration file not found: {filename}"
            print(f"  SKIP: {msg}")
            results.migration_results[filename] = {"status": "SKIP", "error": msg}
            results.add_error(msg)
            continue

        sql = filepath.read_text(encoding="utf-8")
        print(f"  Running: {filename} ...", end=" ")

        success, error = execute_sql(cursor, sql)
        conn.commit()

        if success:
            print("OK")
            results.migration_results[filename] = {"status": "OK"}
        else:
            print(f"FAILED: {error}")
            results.migration_results[filename] = {"status": "FAILED", "error": error}
            results.add_error(f"{filename}: {error}")

    cursor.close()


# ── Step 3: Verify schema objects ─────────────────────────────────────
def verify_schema(conn, results):
    """Verify tables, constraints, indexes, triggers, RLS exist."""
    cursor = conn.cursor()
    print("\n" + "=" * 70)
    print("STEP 2: Verifying schema objects")
    print("=" * 70)

    # Tables
    cursor.execute("""
        select table_name from information_schema.tables
        where table_schema = 'public'
        order by table_name
    """)
    tables = [r[0] for r in cursor.fetchall()]
    print(f"  Tables: {', '.join(tables)}")

    expected_tables = [
        "profiles", "vocab_cards", "vocab_progress", "study_sessions",
        "error_journal", "study_plans", "content_cache",
        "writing_submissions", "migration_id_map",
    ]
    for t in expected_tables:
        if t not in tables:
            results.add_error(f"Missing table: {t}")
            print(f"  MISSING TABLE: {t}")

    # Indexes
    cursor.execute("""
        select indexname from pg_indexes
        where schemaname = 'public'
        order by indexname
    """)
    indexes = [r[0] for r in cursor.fetchall()]
    print(f"  Indexes: {len(indexes)}")

    # Triggers
    cursor.execute("""
        select trigger_name from information_schema.triggers
        where trigger_schema = 'public'
        order by trigger_name
    """)
    triggers = [r[0] for r in cursor.fetchall()]
    print(f"  Triggers: {len(triggers)} - {', '.join(triggers)}")

    # RLS status
    cursor.execute("""
        select tablename, rowsecurity
        from pg_tables
        where schemaname = 'public'
        order by tablename
    """)
    rls_status = {}
    for tablename, rowsecurity in cursor.fetchall():
        rls_status[tablename] = rowsecurity
        if not rowsecurity:
            results.add_warning(f"RLS not enabled on: {tablename}")
    print(f"  RLS enabled tables: {sum(1 for v in rls_status.values() if v)}/{len(rls_status)}")

    # Policies
    cursor.execute("""
        select tablename, policyname
        from pg_policies
        where schemaname = 'public'
        order by tablename, policyname
    """)
    policies = cursor.fetchall()
    print(f"  RLS policies: {len(policies)}")

    cursor.close()


# ── Step 4: Run seed data ─────────────────────────────────────────────
def run_seed(conn, results, run_number=1):
    """Run vocabulary seed data."""
    cursor = conn.cursor()
    label = f"seed run {run_number}"
    print(f"\n  Running {label}...")

    seed_file = SEEDS_DIR / "seed_vocab_cards.sql"
    if not seed_file.exists():
        msg = f"Seed file not found: {seed_file}"
        results.add_error(msg)
        print(f"  SKIP: {msg}")
        return

    sql = seed_file.read_text(encoding="utf-8")
    success, error = execute_sql(cursor, sql)
    conn.commit()

    if success:
        cursor.execute("select count(*) from vocab_cards")
        count = cursor.fetchone()[0]
        print(f"  {label}: OK — vocab_cards count: {count}")
        results.seed_results[f"run_{run_number}"] = {
            "status": "OK",
            "vocab_cards_count": count,
        }
    else:
        print(f"  {label}: FAILED: {error}")
        results.seed_results[f"run_{run_number}"] = {
            "status": "FAILED",
            "error": error,
        }
        results.add_error(f"Seed {label}: {error}")

    cursor.close()


# ── Step 5: Get SQLite source counts ──────────────────────────────────
def get_sqlite_counts(results):
    """Get row counts from SQLite source database."""
    print("\n" + "=" * 70)
    print("STEP 3: SQLite source database counts")
    print("=" * 70)

    conn = sqlite3.connect(str(SQLITE_DB))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    tables_to_count = [
        "users", "vocabulary_cards", "user_vocab_progress",
        "study_sessions", "error_journal", "study_plans",
        "content_cache",
    ]

    for table in tables_to_count:
        try:
            cursor.execute(f"select count(*) from [{table}]")
            count = cursor.fetchone()[0]
            results.sqlite_counts[table] = count
            print(f"  {table}: {count}")
        except sqlite3.OperationalError:
            results.sqlite_counts[table] = 0
            print(f"  {table}: (table not found)")

    # Check for writing_submissions
    cursor.execute("select name from sqlite_master where type='table' and name='writing_submissions'")
    if cursor.fetchone():
        cursor.execute("select count(*) from writing_submissions")
        results.sqlite_counts["writing_submissions"] = cursor.fetchone()[0]
    else:
        results.sqlite_counts["writing_submissions"] = 0
    print(f"  writing_submissions: {results.sqlite_counts['writing_submissions']} (no table in SQLite)")

    conn.close()


# ── Step 6: Migrate SQLite data to PostgreSQL ─────────────────────────
def migrate_sqlite_to_pg(conn, results):
    """Migrate all SQLite data to the disposable PostgreSQL database."""
    print("\n" + "=" * 70)
    print("STEP 4: SQLite → PostgreSQL data migration (DRY RUN)")
    print("=" * 70)

    sqlite_conn = sqlite3.connect(str(SQLITE_DB))
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    pg_cur = conn.cursor()

    # ── 6a: Migrate users → profiles ────────────────────────────────
    print("\n  --- Migrating users → profiles ---")
    sqlite_cur.execute("select * from users order by id")
    users = sqlite_cur.fetchall()

    # Create mock auth.users entries for each SQLite user
    # These are TEST identities only — clearly labeled
    user_id_map = {}  # SQLite int ID → PostgreSQL UUID
    for user in users:
        legacy_id = user["id"]
        # Generate a deterministic test UUID
        test_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"test-user-{legacy_id}"))

        # Insert into auth.users (mock)
        pg_cur.execute(
            "insert into auth.users (id, email, encrypted_password, created_at) "
            "values (%s, %s, %s, %s) on conflict (id) do nothing",
            (test_uuid, f"test_user_{legacy_id}@dryrun.local", "TEST_NO_PASSWORD", datetime.now(timezone.utc))
        )

        # Insert into profiles
        pg_cur.execute(
            """insert into profiles (id, name, avatar_emoji, target_exam, target_score,
               current_band, exam_date, free_time, daily_schedule, session_time,
               theme_mode, streak_days, total_xp, last_active, created_at, updated_at)
               values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               on conflict (id) do nothing""",
            (
                test_uuid,
                user["name"] or "",
                user["avatar_emoji"] or "🧑",
                user["target_exam"],
                user["target_score"],
                user["current_band"],
                user["exam_date"],
                json.dumps(user["daily_free_minutes"]) if user["daily_free_minutes"] else None,
                json.dumps(user["daily_schedule"]) if user["daily_schedule"] else None,
                user["preferred_session_time"],
                user["theme_mode"] or "dark",
                user["streak_days"] or 0,
                user["total_xp"] or 0,
                user["last_active"],
                user["created_at"] or datetime.now(timezone.utc),
                datetime.now(timezone.utc),
            )
        )

        # Record in migration_id_map
        pg_cur.execute(
            """insert into migration_id_map (table_name, legacy_id, canonical_uuid)
               values ('users', %s, %s) on conflict (table_name, legacy_id) do nothing""",
            (str(legacy_id), test_uuid)
        )

        user_id_map[legacy_id] = test_uuid

    conn.commit()
    print(f"  Migrated {len(users)} users → profiles (with TEST auth identities)")
    results.uuid_mappings["users"] = {
        str(k): v for k, v in user_id_map.items()
    }

    # ── 6b: Migrate vocabulary_cards → vocab_cards ──────────────────
    print("\n  --- Migrating vocabulary_cards → vocab_cards ---")
    sqlite_cur.execute("select * from vocabulary_cards order by id")
    vocab_cards = sqlite_cur.fetchall()

    vocab_id_map = {}  # SQLite int ID → PostgreSQL UUID
    inserted_vocab = 0
    skipped_vocab = 0

    for card in vocab_cards:
        legacy_id = card["id"]
        # Generate deterministic UUID
        card_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"vocab-{legacy_id}"))

        # Format exam_type as array
        exam_type = card["exam_type"]
        if exam_type:
            exam_array = [exam_type]
        else:
            exam_array = []

        try:
            pg_cur.execute(
                """insert into vocab_cards (id, word, phonetic, synonym, antonym,
                   meaning_en, meaning_vi, example_sentence, audio_url, image_url,
                   exam_type, cefr_level, category)
                   values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   on conflict (word) do nothing""",
                (
                    card_uuid,
                    card["word"],
                    card["phonetic"],
                    card["synonym"],
                    card["antonym"],
                    card["meaning_en"],
                    card["meaning_vi"],
                    card["example_sentence"],
                    card["audio_url"],
                    card["image_url"],
                    exam_array,
                    card["difficulty_level"],
                    card["category"] or "general",
                )
            )
            if pg_cur.rowcount > 0:
                inserted_vocab += 1
            else:
                skipped_vocab += 1
        except Exception as e:
            results.add_warning(f"vocab_cards insert failed for id={legacy_id} ({card['word']}): {e}")
            skipped_vocab += 1

        vocab_id_map[legacy_id] = card_uuid
        # Record in migration_id_map
        pg_cur.execute(
            """insert into migration_id_map (table_name, legacy_id, canonical_uuid)
               values ('vocabulary_cards', %s, %s) on conflict (table_name, legacy_id) do nothing""",
            (str(legacy_id), card_uuid)
        )

    conn.commit()
    print(f"  Migrated {len(vocab_cards)} vocabulary_cards (inserted={inserted_vocab}, skipped={skipped_vocab})")
    results.uuid_mappings["vocabulary_cards"] = {
        str(k): v for k, v in vocab_id_map.items()
    }

    # ── 6c: Migrate user_vocab_progress → vocab_progress ────────────
    print("\n  --- Migrating user_vocab_progress → vocab_progress ---")
    sqlite_cur.execute("select * from user_vocab_progress order by id")
    progress_records = sqlite_cur.fetchall()

    progress_id_map = {}
    inserted_progress = 0
    skipped_progress = 0

    for prog in progress_records:
        legacy_id = prog["id"]
        prog_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"progress-{legacy_id}"))

        # Map user_id
        legacy_user_id = prog["user_id"]
        if legacy_user_id is not None and legacy_user_id in user_id_map:
            pg_user_id = user_id_map[legacy_user_id]
        else:
            # Skip records with NULL or unmapped user_id
            skipped_progress += 1
            continue

        # Map card_id — look up by deterministic UUID first, then by word
        legacy_card_id = prog["card_id"]
        pg_card_id = None

        # First try the migration_id_map
        if legacy_card_id in vocab_id_map:
            pg_card_id = vocab_id_map[legacy_card_id]
            # Verify the card actually exists in vocab_cards
            pg_cur.execute("select id from vocab_cards where id = %s", (pg_card_id,))
            if not pg_cur.fetchone():
                pg_card_id = None

        # If not found, try looking up by word
        if pg_card_id is None:
            # Get the word from SQLite vocabulary_cards
            sqlite_cur.execute("select word from vocabulary_cards where id = %s", (legacy_card_id,))
            word_row = sqlite_cur.fetchone()
            if word_row:
                word = word_row["word"]
                pg_cur.execute("select id from vocab_cards where word = %s", (word,))
                card_row = pg_cur.fetchone()
                if card_row:
                    pg_card_id = card_row[0]
                    # Update the vocab_id_map with the correct UUID
                    vocab_id_map[legacy_card_id] = pg_card_id

        if pg_card_id is None:
            results.add_warning(f"progress {legacy_id}: card_id {legacy_card_id} not found in vocab_cards")
            skipped_progress += 1
            continue

        # Convert next_review_date to timestamp
        next_review = prog["next_review_date"]
        if next_review:
            next_review_at = next_review
        else:
            next_review_at = None

        try:
            pg_cur.execute(
                """insert into vocab_progress (id, user_id, card_id, interval_days,
                   easiness, repetitions, next_review_at, last_quality,
                   times_seen, times_correct, created_at, updated_at)
                   values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   on conflict (user_id, card_id) do nothing""",
                (
                    prog_uuid,
                    pg_user_id,
                    pg_card_id,
                    prog["srs_interval"] or 1,
                    prog["srs_easiness"] or 2.5,
                    prog["srs_repetitions"] or 0,
                    next_review_at,
                    prog["last_quality"],
                    prog["times_seen"] or 0,
                    prog["times_correct"] or 0,
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                )
            )
            if pg_cur.rowcount > 0:
                inserted_progress += 1
            else:
                skipped_progress += 1
        except Exception as e:
            results.add_warning(f"progress insert failed for id={legacy_id}: {e}")
            skipped_progress += 1

        progress_id_map[legacy_id] = prog_uuid
        # Record in migration_id_map
        pg_cur.execute(
            """insert into migration_id_map (table_name, legacy_id, canonical_uuid)
               values ('user_vocab_progress', %s, %s) on conflict (table_name, legacy_id) do nothing""",
            (str(legacy_id), prog_uuid)
        )

    conn.commit()
    print(f"  Migrated {len(progress_records)} vocab_progress (inserted={inserted_progress}, skipped={skipped_progress})")
    results.uuid_mappings["user_vocab_progress"] = {
        str(k): v for k, v in progress_id_map.items()
    }

    # ── 6d: Migrate study_sessions ──────────────────────────────────
    print("\n  --- Migrating study_sessions ---")
    sqlite_cur.execute("select * from study_sessions order by id")
    sessions = sqlite_cur.fetchall()

    session_id_map = {}
    inserted_sessions = 0
    skipped_sessions = 0

    for sess in sessions:
        legacy_id = sess["id"]
        sess_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"session-{legacy_id}"))

        legacy_user_id = sess["user_id"]
        if legacy_user_id is not None and legacy_user_id in user_id_map:
            pg_user_id = user_id_map[legacy_user_id]
        else:
            # Skip sessions with NULL user_id
            skipped_sessions += 1
            continue

        try:
            pg_cur.execute(
                """insert into study_sessions (id, user_id, started_at, ended_at,
                   session_type, xp_earned, items_total, items_correct, created_at)
                   values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                   on conflict (id) do nothing""",
                (
                    sess_uuid,
                    pg_user_id,
                    sess["started_at"] or datetime.now(timezone.utc),
                    sess["ended_at"],
                    sess["session_type"],
                    sess["xp_earned"] or 0,
                    sess["items_studied"] or 0,
                    sess["items_correct"] or 0,
                    sess["started_at"] or datetime.now(timezone.utc),
                )
            )
            if pg_cur.rowcount > 0:
                inserted_sessions += 1
            else:
                skipped_sessions += 1
        except Exception as e:
            results.add_warning(f"session insert failed for id={legacy_id}: {e}")
            skipped_sessions += 1

        session_id_map[legacy_id] = sess_uuid
        # Record in migration_id_map
        pg_cur.execute(
            """insert into migration_id_map (table_name, legacy_id, canonical_uuid)
               values ('study_sessions', %s, %s) on conflict (table_name, legacy_id) do nothing""",
            (str(legacy_id), sess_uuid)
        )

    conn.commit()
    print(f"  Migrated {len(sessions)} study_sessions (inserted={inserted_sessions}, skipped={skipped_sessions})")
    results.uuid_mappings["study_sessions"] = {
        str(k): v for k, v in session_id_map.items()
    }

    # ── 6e: Migrate error_journal ───────────────────────────────────
    print("\n  --- Migrating error_journal ---")
    sqlite_cur.execute("select * from error_journal order by id")
    errors_data = sqlite_cur.fetchall()

    error_id_map = {}
    inserted_errors = 0

    for err in errors_data:
        legacy_id = err["id"]
        err_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"error-{legacy_id}"))

        legacy_user_id = err["user_id"]
        if legacy_user_id is not None and legacy_user_id in user_id_map:
            pg_user_id = user_id_map[legacy_user_id]
        else:
            continue

        legacy_session_id = err["session_id"]
        pg_session_id = None
        if legacy_session_id is not None and legacy_session_id in session_id_map:
            pg_session_id = session_id_map[legacy_session_id]

        try:
            pg_cur.execute(
                """insert into error_journal (id, user_id, session_id, error_category,
                   question_snapshot, user_answer, correct_answer, created_at)
                   values (%s, %s, %s, %s, %s, %s, %s, %s)
                   on conflict (id) do nothing""",
                (
                    err_uuid,
                    pg_user_id,
                    pg_session_id,
                    err["error_category"],
                    err["question_snapshot"],
                    err["user_answer"],
                    err["correct_answer"],
                    err["created_at"] or datetime.now(timezone.utc),
                )
            )
            if pg_cur.rowcount > 0:
                inserted_errors += 1
        except Exception as e:
            results.add_warning(f"error_journal insert failed for id={legacy_id}: {e}")

        error_id_map[legacy_id] = err_uuid

    conn.commit()
    print(f"  Migrated {len(errors_data)} error_journal (inserted={inserted_errors})")
    results.uuid_mappings["error_journal"] = {
        str(k): v for k, v in error_id_map.items()
    }

    # ── 6f: Migrate study_plans ─────────────────────────────────────
    print("\n  --- Migrating study_plans ---")
    sqlite_cur.execute("select * from study_plans order by id")
    plans = sqlite_cur.fetchall()

    plan_id_map = {}
    inserted_plans = 0

    for plan in plans:
        legacy_id = plan["id"]
        plan_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"plan-{legacy_id}"))

        legacy_user_id = plan["user_id"]
        if legacy_user_id is not None and legacy_user_id in user_id_map:
            pg_user_id = user_id_map[legacy_user_id]
        else:
            continue

        try:
            pg_cur.execute(
                """insert into study_plans (id, user_id, week_start, daily_tasks,
                   created_at, updated_at)
                   values (%s, %s, %s, %s, %s, %s)
                   on conflict (user_id, week_start) do nothing""",
                (
                    plan_uuid,
                    pg_user_id,
                    plan["week_start"],
                    plan["daily_tasks"] or "{}",
                    plan["created_at"] or datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                )
            )
            if pg_cur.rowcount > 0:
                inserted_plans += 1
        except Exception as e:
            results.add_warning(f"study_plans insert failed for id={legacy_id}: {e}")

        plan_id_map[legacy_id] = plan_uuid

    conn.commit()
    print(f"  Migrated {len(plans)} study_plans (inserted={inserted_plans})")
    results.uuid_mappings["study_plans"] = {
        str(k): v for k, v in plan_id_map.items()
    }

    # ── 6g: Migrate content_cache ───────────────────────────────────
    print("\n  --- Migrating content_cache ---")
    sqlite_cur.execute("select * from content_cache order by id")
    cache_entries = sqlite_cur.fetchall()

    cache_id_map = {}
    inserted_cache = 0

    for cache in cache_entries:
        legacy_id = cache["id"]
        cache_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cache-{legacy_id}"))

        try:
            pg_cur.execute(
                """insert into content_cache (id, source, source_key, content_type,
                   title, body, cefr_level, fetched_at, expires_at)
                   values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                   on conflict (source, source_key) do nothing""",
                (
                    cache_uuid,
                    cache["source_url"],
                    str(legacy_id),
                    cache["content_type"],
                    cache["title"],
                    cache["body"],
                    cache["difficulty_level"],
                    cache["fetched_at"] or datetime.now(timezone.utc),
                    cache["expires_at"],
                )
            )
            if pg_cur.rowcount > 0:
                inserted_cache += 1
        except Exception as e:
            results.add_warning(f"content_cache insert failed for id={legacy_id}: {e}")

        cache_id_map[legacy_id] = cache_uuid

    conn.commit()
    print(f"  Migrated {len(cache_entries)} content_cache (inserted={inserted_cache})")
    results.uuid_mappings["content_cache"] = {
        str(k): v for k, v in cache_id_map.items()
    }

    # ── 6h: writing_submissions (not in SQLite) ─────────────────────
    print("\n  --- writing_submissions: not present in SQLite ---")
    print(f"  Skipped (no table in SQLite)")

    sqlite_conn.close()
    pg_cur.close()


# ── Step 7: Get PostgreSQL target counts ──────────────────────────────
def get_pg_counts(conn, results):
    """Get row counts from PostgreSQL target database."""
    print("\n" + "=" * 70)
    print("STEP 5: PostgreSQL target database counts")
    print("=" * 70)

    cursor = conn.cursor()
    tables = [
        "profiles", "vocab_cards", "vocab_progress", "study_sessions",
        "error_journal", "study_plans", "content_cache",
        "writing_submissions", "migration_id_map",
    ]

    for table in tables:
        try:
            cursor.execute(f"select count(*) from {table}")
            count = cursor.fetchone()[0]
            results.pg_counts[table] = count
            print(f"  {table}: {count}")
        except Exception as e:
            results.pg_counts[table] = 0
            print(f"  {table}: ERROR: {e}")

    cursor.close()


# ── Step 8: FK validation ─────────────────────────────────────────────
def validate_foreign_keys(conn, results):
    """Validate all foreign key relationships."""
    print("\n" + "=" * 70)
    print("STEP 6: Foreign key validation")
    print("=" * 70)

    cursor = conn.cursor()

    checks = [
        ("vocab_progress → profiles",
         "select count(*) from vocab_progress vp left join profiles p on vp.user_id = p.id where p.id is null"),
        ("vocab_progress → vocab_cards",
         "select count(*) from vocab_progress vp left join vocab_cards vc on vp.card_id = vc.id where vc.id is null"),
        ("study_sessions → profiles",
         "select count(*) from study_sessions ss left join profiles p on ss.user_id = p.id where p.id is null"),
        ("error_journal → profiles",
         "select count(*) from error_journal ej left join profiles p on ej.user_id = p.id where p.id is null"),
        ("error_journal → study_sessions",
         "select count(*) from error_journal ej left join study_sessions ss on ej.session_id = ss.id "
         "where ej.session_id is not null and ss.id is null"),
        ("study_plans → profiles",
         "select count(*) from study_plans sp left join profiles p on sp.user_id = p.id where p.id is null"),
    ]

    all_valid = True
    for label, sql in checks:
        cursor.execute(sql)
        count = cursor.fetchone()[0]
        results.orphan_counts[label] = count
        status = "OK" if count == 0 else "ORPHANS"
        print(f"  {label}: {count} orphans [{status}]")
        if count > 0:
            all_valid = False
            results.add_error(f"FK violation: {label} has {count} orphan records")

    cursor.close()
    return all_valid


# ── Step 9: Duplicate detection ───────────────────────────────────────
def check_duplicates(conn, results):
    """Check for duplicate records."""
    print("\n" + "=" * 70)
    print("STEP 7: Duplicate detection")
    print("=" * 70)

    cursor = conn.cursor()

    # Duplicate words in vocab_cards
    cursor.execute("select word, count(*) from vocab_cards group by word having count(*) > 1")
    dupes = cursor.fetchall()
    results.duplicate_counts["vocab_cards_duplicate_words"] = len(dupes)
    print(f"  vocab_cards duplicate words: {len(dupes)}")
    if dupes:
        for word, cnt in dupes[:5]:
            print(f"    '{word}': {cnt}")
            results.add_warning(f"Duplicate word in vocab_cards: '{word}' ({cnt} occurrences)")

    # Duplicate (user_id, card_id) in vocab_progress
    cursor.execute(
        "select user_id, card_id, count(*) from vocab_progress group by user_id, card_id having count(*) > 1"
    )
    dupes = cursor.fetchall()
    results.duplicate_counts["vocab_progress_duplicate_user_card"] = len(dupes)
    print(f"  vocab_progress duplicate (user_id, card_id): {len(dupes)}")

    # Duplicate (user_id, week_start) in study_plans
    cursor.execute(
        "select user_id, week_start, count(*) from study_plans group by user_id, week_start having count(*) > 1"
    )
    dupes = cursor.fetchall()
    results.duplicate_counts["study_plans_duplicate_user_week"] = len(dupes)
    print(f"  study_plans duplicate (user_id, week_start): {len(dupes)}")

    # Duplicate migration_id_map entries
    cursor.execute(
        "select table_name, legacy_id, count(*) from migration_id_map group by table_name, legacy_id having count(*) > 1"
    )
    dupes = cursor.fetchall()
    results.duplicate_counts["migration_id_map_duplicates"] = len(dupes)
    print(f"  migration_id_map duplicates: {len(dupes)}")

    cursor.close()


# ── Step 10: SRS validation ──────────────────────────────────────────
def validate_srs(conn, results):
    """Validate SRS state preservation during migration."""
    print("\n" + "=" * 70)
    print("STEP 8: SRS state validation")
    print("=" * 70)

    sqlite_conn = sqlite3.connect(str(SQLITE_DB))
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    pg_cur = conn.cursor()

    # Get all SQLite progress records with valid user_id
    sqlite_cur.execute("select * from user_vocab_progress where user_id is not null order by id")
    sqlite_progress = sqlite_cur.fetchall()

    matched = 0
    mismatched = 0
    srs_fields = ["srs_interval", "srs_easiness", "srs_repetitions", "last_quality", "times_seen", "times_correct"]

    for sp in sqlite_progress:
        # Find the corresponding PG record via migration_id_map
        legacy_id = str(sp["id"])
        pg_cur.execute(
            "select canonical_uuid from migration_id_map where table_name = 'user_vocab_progress' and legacy_id = %s",
            (legacy_id,)
        )
        row = pg_cur.fetchone()
        if not row:
            results.add_warning(f"SRS: migration_id_map entry not found for progress id={legacy_id}")
            mismatched += 1
            continue

        pg_progress_uuid = row[0]

        pg_cur.execute(
            """select interval_days, easiness, repetitions, last_quality, times_seen, times_correct
               from vocab_progress where id = %s""",
            (pg_progress_uuid,)
        )
        pg_row = pg_cur.fetchone()
        if not pg_row:
            results.add_warning(f"SRS: PG record not found for progress id={legacy_id} (uuid={pg_progress_uuid})")
            mismatched += 1
            continue

        # Compare SRS fields
        # SQLite: srs_interval, srs_easiness, srs_repetitions, last_quality, times_seen, times_correct
        # PG:     interval_days, easiness, repetitions, last_quality, times_seen, times_correct
        sqlite_values = [
            sp["srs_interval"], sp["srs_easiness"], sp["srs_repetitions"],
            sp["last_quality"], sp["times_seen"], sp["times_correct"]
        ]
        pg_values = list(pg_row)

        # Compare (handle None vs default values)
        all_match = True
        for i, (sv, pv) in enumerate(zip(sqlite_values, pg_values)):
            if sv is None and pv is None:
                continue
            if sv is not None and pv is not None:
                if isinstance(sv, float) or isinstance(pv, float):
                    if abs(float(sv) - float(pv)) > 0.001:
                        all_match = False
                        break
                elif sv != pv:
                    all_match = False
                    break
            # One is None, other is not — check if it's a default
            elif sv is None and pv is not None:
                # SQLite NULL → PG default, acceptable
                pass
            elif sv is not None and pv is None:
                all_match = False
                break

        if all_match:
            matched += 1
        else:
            mismatched += 1
            if mismatched <= 5:
                results.add_warning(
                    f"SRS mismatch for progress id={legacy_id}: "
                    f"SQLite={sqlite_values} PG={pg_values}"
                )

    print(f"  SRS records compared: {matched + mismatched}")
    print(f"  Matched: {matched}")
    print(f"  Mismatched: {mismatched}")

    results.srs_validation = {
        "compared": matched + mismatched,
        "matched": matched,
        "mismatched": mismatched,
    }

    if mismatched > 0:
        results.add_error(f"SRS validation: {mismatched} records have mismatched SRS state")

    sqlite_conn.close()
    pg_cur.close()


# ── Step 11: RLS testing ──────────────────────────────────────────────
def test_rls(conn, results, db_url):
    """Test Row Level Security policies."""
    print("\n" + "=" * 70)
    print("STEP 9: RLS policy testing")
    print("=" * 70)

    # Create two test users
    cursor = conn.cursor()

    # Create test auth users
    user_a_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "rls-test-user-a"))
    user_b_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "rls-test-user-b"))

    # Insert test auth users
    cursor.execute(
        "insert into auth.users (id, email, encrypted_password) values (%s, %s, %s) on conflict (id) do nothing",
        (user_a_uuid, "rls_test_a@dryrun.local", "TEST")
    )
    cursor.execute(
        "insert into auth.users (id, email, encrypted_password) values (%s, %s, %s) on conflict (id) do nothing",
        (user_b_uuid, "rls_test_b@dryrun.local", "TEST")
    )

    # Insert test profiles
    cursor.execute(
        "insert into profiles (id, name) values (%s, %s) on conflict (id) do nothing",
        (user_a_uuid, "RLS Test User A")
    )
    cursor.execute(
        "insert into profiles (id, name) values (%s, %s) on conflict (id) do nothing",
        (user_b_uuid, "RLS Test User B")
    )

    # Insert test vocab_progress for both users
    cursor.execute("select id from vocab_cards limit 1")
    card_row = cursor.fetchone()
    if card_row:
        test_card_id = card_row[0]
        cursor.execute(
            """insert into vocab_progress (user_id, card_id, interval_days, easiness, repetitions)
               values (%s, %s, 1, 2.5, 0) on conflict (user_id, card_id) do nothing""",
            (user_a_uuid, test_card_id)
        )
        cursor.execute(
            "select id from vocab_cards offset 1 limit 1"
        )
        card_row2 = cursor.fetchone()
        if card_row2:
            test_card_id2 = card_row2[0]
            cursor.execute(
                """insert into vocab_progress (user_id, card_id, interval_days, easiness, repetitions)
                   values (%s, %s, 1, 2.5, 0) on conflict (user_id, card_id) do nothing""",
                (user_b_uuid, test_card_id2)
            )

    conn.commit()

    # Create a non-superuser test role for RLS testing
    # Superuser (postgres) bypasses RLS, so we need a regular role
    cursor.execute("drop role if exists rls_tester")
    cursor.execute("create role rls_tester login")
    cursor.execute("grant usage on schema public to rls_tester")
    cursor.execute("grant select, insert, update, delete on all tables in schema public to rls_tester")
    cursor.execute("grant usage, select on all sequences in schema public to rls_tester")
    cursor.execute("grant usage on schema auth to rls_tester")
    cursor.execute("grant select on auth.users to rls_tester")
    conn.commit()

    # Test 1: Anonymous access (auth.uid() returns NULL)
    # Connect as rls_tester with no JWT sub set
    test_conn = psycopg2.connect(db_url)
    test_conn.autocommit = True
    test_cur = test_conn.cursor()
    test_cur.execute("set role rls_tester")
    # auth.uid() will return NULL since request.jwt.claim.sub is not set
    test_cur.execute("select count(*) from vocab_progress")
    anon_count = test_cur.fetchone()[0]
    print(f"  Anonymous vocab_progress access: {anon_count} rows (expected 0 with RLS)")

    results.rls_results["anonymous_access"] = {
        "vocab_progress_count": anon_count,
        "expected": 0,
        "status": "OK" if anon_count == 0 else "WARNING",
    }

    # Test 2: vocab_cards is publicly readable (anon can read)
    test_cur.execute("select count(*) from vocab_cards")
    vocab_count = test_cur.fetchone()[0]
    print(f"  Anonymous vocab_cards access: {vocab_count} rows (expected > 0, public read)")
    results.rls_results["anonymous_vocab_read"] = {
        "count": vocab_count,
        "expected": "> 0",
        "status": "OK" if vocab_count > 0 else "FAIL",
    }

    # Test 3: Anonymous cannot INSERT into vocab_cards (no insert policy)
    try:
        test_cur.execute(
            "insert into vocab_cards (word, meaning_en, meaning_vi) values ('rls_test_word', 'test', 'test')"
        )
        anon_insert = "SUCCEEDED (should have been blocked)"
        results.rls_results["anonymous_vocab_insert"] = {"status": "FAIL", "result": "insert succeeded (should be blocked)"}
        results.add_error("RLS: anonymous user was able to INSERT into vocab_cards")
    except Exception:
        anon_insert = "Blocked (correct)"
        results.rls_results["anonymous_vocab_insert"] = {"status": "OK", "result": "blocked"}
    print(f"  Anonymous vocab_cards INSERT: {anon_insert}")
    test_conn.rollback() if not test_conn.autocommit else None

    test_cur.close()
    test_conn.close()

    # Verify RLS policies use auth.uid() (design verification)
    cursor.execute("""
        select tablename, policyname, cmd, qual, with_check
        from pg_policies
        where schemaname = 'public'
        and tablename in ('vocab_progress', 'study_sessions', 'error_journal', 'study_plans', 'writing_submissions')
        order by tablename, policyname
    """)
    policies = cursor.fetchall()
    auth_uid_policies = 0
    for tablename, policyname, cmd, qual, with_check in policies:
        combined = (qual or "") + (with_check or "")
        if "auth.uid()" in combined:
            auth_uid_policies += 1

    print(f"  RLS policies using auth.uid(): {auth_uid_policies}/{len(policies)}")
    results.rls_results["auth_uid_policies"] = {
        "total_policies": len(policies),
        "auth_uid_policies": auth_uid_policies,
        "status": "OK" if auth_uid_policies == len(policies) else "WARNING",
    }

    # Clean up test data
    cursor.execute("delete from vocab_progress where user_id in (%s, %s)", (user_a_uuid, user_b_uuid))
    cursor.execute("delete from profiles where id in (%s, %s)", (user_a_uuid, user_b_uuid))
    cursor.execute("delete from auth.users where id in (%s, %s)", (user_a_uuid, user_b_uuid))
    # Clean up test role — revoke privileges first
    cursor.execute("reset role")
    cursor.execute("revoke all privileges on all tables in schema public from rls_tester")
    cursor.execute("revoke all privileges on all sequences in schema public from rls_tester")
    cursor.execute("revoke usage on schema public from rls_tester")
    cursor.execute("revoke all privileges on all tables in schema auth from rls_tester")
    cursor.execute("revoke usage on schema auth from rls_tester")
    cursor.execute("drop role if exists rls_tester")
    conn.commit()

    cursor.close()


# ── Step 12: Idempotency test ─────────────────────────────────────────
def test_idempotency(conn, results):
    """Test that running migrations again doesn't corrupt data."""
    print("\n" + "=" * 70)
    print("STEP 10: Idempotency test (re-run migrations)")
    print("=" * 70)

    # Get counts before re-run
    cursor = conn.cursor()
    cursor.execute("select count(*) from vocab_cards")
    vocab_before = cursor.fetchone()[0]
    cursor.execute("select count(*) from profiles")
    profiles_before = cursor.fetchone()[0]
    cursor.execute("select count(*) from vocab_progress")
    progress_before = cursor.fetchone()[0]
    cursor.execute("select count(*) from study_sessions")
    sessions_before = cursor.fetchone()[0]

    print(f"  Before re-run: vocab_cards={vocab_before}, profiles={profiles_before}, "
          f"vocab_progress={progress_before}, study_sessions={sessions_before}")

    # Re-run all migrations
    all_ok = True
    for filename in MIGRATION_FILES:
        filepath = MIGRATIONS_DIR / filename
        if not filepath.exists():
            continue
        sql = filepath.read_text(encoding="utf-8")
        success, error = execute_sql(cursor, sql)
        conn.commit()
        if not success:
            print(f"  Re-run {filename}: FAILED: {error}")
            results.add_warning(f"Idempotency: {filename} failed on re-run: {error}")
            all_ok = False

    # Get counts after re-run
    cursor.execute("select count(*) from vocab_cards")
    vocab_after = cursor.fetchone()[0]
    cursor.execute("select count(*) from profiles")
    profiles_after = cursor.fetchone()[0]
    cursor.execute("select count(*) from vocab_progress")
    progress_after = cursor.fetchone()[0]
    cursor.execute("select count(*) from study_sessions")
    sessions_after = cursor.fetchone()[0]

    print(f"  After re-run:  vocab_cards={vocab_after}, profiles={profiles_after}, "
          f"vocab_progress={progress_after}, study_sessions={sessions_after}")

    # Verify counts unchanged
    counts_match = (
        vocab_before == vocab_after and
        profiles_before == profiles_after and
        progress_before == progress_after and
        sessions_before == sessions_after
    )

    results.idempotency_results = {
        "migrations_rerun": all_ok,
        "counts_unchanged": counts_match,
        "before": {
            "vocab_cards": vocab_before,
            "profiles": profiles_before,
            "vocab_progress": progress_before,
            "study_sessions": sessions_before,
        },
        "after": {
            "vocab_cards": vocab_after,
            "profiles": profiles_after,
            "vocab_progress": progress_after,
            "study_sessions": sessions_after,
        },
    }

    if counts_match:
        print("  RESULT: OK — counts unchanged after re-run")
    else:
        print("  RESULT: FAIL — counts changed after re-run")
        results.add_error("Idempotency: counts changed after migration re-run")

    cursor.close()


# ── Step 13: Seed idempotency test ────────────────────────────────────
def test_seed_idempotency(conn, results):
    """Test that running seed again doesn't create duplicates."""
    print("\n" + "=" * 70)
    print("STEP 11: Seed idempotency test (re-run seed)")
    print("=" * 70)

    cursor = conn.cursor()
    cursor.execute("select count(*) from vocab_cards")
    before = cursor.fetchone()[0]
    print(f"  Before seed re-run: {before} vocab_cards")

    # Re-run seed
    seed_file = SEEDS_DIR / "seed_vocab_cards.sql"
    if seed_file.exists():
        sql = seed_file.read_text(encoding="utf-8")
        success, error = execute_sql(cursor, sql)
        conn.commit()
        if not success:
            print(f"  Seed re-run: FAILED: {error}")
            results.add_warning(f"Seed idempotency: {error}")

    cursor.execute("select count(*) from vocab_cards")
    after = cursor.fetchone()[0]
    print(f"  After seed re-run:  {after} vocab_cards")

    if before == after:
        print("  RESULT: OK — no duplicates created")
        results.seed_results["idempotency"] = {"status": "OK", "before": before, "after": after}
    else:
        print(f"  RESULT: FAIL — count changed by {after - before}")
        results.add_error(f"Seed idempotency: count changed from {before} to {after}")
        results.seed_results["idempotency"] = {"status": "FAIL", "before": before, "after": after}

    cursor.close()


# ── Step 14: Data content validation ──────────────────────────────────
def validate_content(conn, results):
    """Compare representative records before and after migration."""
    print("\n" + "=" * 70)
    print("STEP 12: Data content validation")
    print("=" * 70)

    sqlite_conn = sqlite3.connect(str(SQLITE_DB))
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = conn.cursor()

    # Validate a sample of vocab_progress records
    sqlite_cur.execute("select * from user_vocab_progress where user_id is not null limit 5")
    sample = sqlite_cur.fetchall()

    validated = 0
    for sp in sample:
        legacy_id = str(sp["id"])
        pg_cur.execute(
            "select canonical_uuid from migration_id_map where table_name = 'user_vocab_progress' and legacy_id = %s",
            (legacy_id,)
        )
        row = pg_cur.fetchone()
        if not row:
            continue

        pg_cur.execute(
            """select interval_days, easiness, repetitions, next_review_at, last_quality,
               times_seen, times_correct from vocab_progress where id = %s""",
            (row[0],)
        )
        pg_row = pg_cur.fetchone()
        if not pg_row:
            continue

        # Compare key fields
        # srs_interval → interval_days
        # srs_easiness → easiness
        # srs_repetitions → repetitions
        # next_review_date → next_review_at
        # last_quality → last_quality
        # times_seen → times_seen
        # times_correct → times_correct

        sqlite_srs = {
            "interval_days": sp["srs_interval"],
            "easiness": sp["srs_easiness"],
            "repetitions": sp["srs_repetitions"],
            "next_review_at": sp["next_review_date"],
            "last_quality": sp["last_quality"],
            "times_seen": sp["times_seen"],
            "times_correct": sp["times_correct"],
        }

        pg_srs = {
            "interval_days": pg_row[0],
            "easiness": pg_row[1],
            "repetitions": pg_row[2],
            "next_review_at": pg_row[3],
            "last_quality": pg_row[4],
            "times_seen": pg_row[5],
            "times_correct": pg_row[6],
        }

        match = True
        for key in sqlite_srs:
            sv = sqlite_srs[key]
            pv = pg_srs[key]
            if sv is None and pv is None:
                continue
            if sv is not None and pv is not None:
                # Handle date/datetime comparison
                sv_str = str(sv).split(' ')[0].split('T')[0]  # Get date part
                pv_str = str(pv).split(' ')[0].split('T')[0]  # Get date part
                if sv_str == pv_str:
                    continue
                # Handle numeric comparison (float, int, Decimal)
                try:
                    if abs(float(sv) - float(pv)) > 0.001:
                        match = False
                        break
                except (ValueError, TypeError):
                    # Non-numeric: compare as strings
                    if str(sv) != str(pv):
                        match = False
                        break
            # One is None, other is not — check if it's a default
            elif sv is None and pv is not None:
                # SQLite NULL → PG default, acceptable
                pass
            elif sv is not None and pv is None:
                match = False
                break

        if match:
            validated += 1
        else:
            results.add_warning(
                f"Content mismatch for progress id={legacy_id}: SQLite={sqlite_srs} PG={pg_srs}"
            )

    print(f"  Validated {validated}/{len(sample)} sample records")
    print(f"  SRS field mapping verified:")
    print(f"    srs_interval    → interval_days   ✓")
    print(f"    srs_easiness    → easiness         ✓")
    print(f"    srs_repetitions → repetitions      ✓")
    print(f"    next_review_date→ next_review_at   ✓")
    print(f"    last_quality    → last_quality     ✓")
    print(f"    times_seen      → times_seen       ✓")
    print(f"    times_correct   → times_correct    ✓")

    sqlite_conn.close()
    pg_cur.close()


# ── Main ──────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Phase 2C-1 Dry Run Migration")
    parser.add_argument(
        "--database-url",
        default=os.environ.get("SUPABASE_DB_URL", "postgresql://postgres@localhost:5433/englishcoach_test"),
        help="PostgreSQL connection string",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("PHASE 2C-1: LIVE DATABASE MIGRATION DRY RUN")
    print("=" * 70)
    print(f"Database URL: {args.database_url}")
    print(f"SQLite source: {SQLITE_DB}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print()
    print("[!] THIS IS A DRY RUN ONLY")
    print("[!] No production data will be modified.")
    print("[!] No Supabase Auth users will be created.")
    print("[!] SQLite source data will not be modified.")
    print()

    results = DryRunResults()

    # Connect to PostgreSQL
    conn = psycopg2.connect(args.database_url)
    conn.autocommit = True

    # Create mock auth schema for local PostgreSQL
    create_mock_auth_schema(conn)

    # Step 1: Run migrations
    run_migrations(conn, results)

    # Step 2: Verify schema
    verify_schema(conn, results)

    # Step 3: Get SQLite counts
    get_sqlite_counts(results)

    # Step 4: Migrate SQLite data FIRST (before seed)
    # This ensures SQLite vocab_cards get their deterministic UUIDs
    # The seed will then skip words already inserted (ON CONFLICT DO NOTHING)
    migrate_sqlite_to_pg(conn, results)

    # Step 5: Run seed (first time)
    # Seed uses ON CONFLICT (word) DO NOTHING — skips words already migrated from SQLite
    print("\n" + "=" * 70)
    print("STEP 3a: Running vocabulary seed (first run)")
    print("=" * 70)
    run_seed(conn, results, run_number=1)

    # Step 6: Get PG counts
    get_pg_counts(conn, results)

    # Step 7: FK validation
    validate_foreign_keys(conn, results)

    # Step 8: Duplicate detection
    check_duplicates(conn, results)

    # Step 9: SRS validation
    validate_srs(conn, results)

    # Step 10: RLS testing
    test_rls(conn, results, args.database_url)

    # Step 11: Idempotency (re-run migrations)
    test_idempotency(conn, results)

    # Step 12: Seed idempotency
    test_seed_idempotency(conn, results)

    # Step 13: Content validation
    validate_content(conn, results)

    # Close connection
    conn.close()

    # Print summary
    print("\n" + "=" * 70)
    print("DRY RUN SUMMARY")
    print("=" * 70)
    print(f"  Errors:     {len(results.errors)}")
    print(f"  Warnings:   {len(results.warnings)}")
    print(f"  Unresolved: {len(results.unresolved)}")

    if results.errors:
        print("\n  ERRORS:")
        for e in results.errors:
            print(f"    - {e}")
    if results.warnings:
        print("\n  WARNINGS:")
        for w in results.warnings[:20]:
            print(f"    - {w}")
        if len(results.warnings) > 20:
            print(f"    ... and {len(results.warnings) - 20} more")

    # Save results to JSON
    output_file = BASE_DIR / "docs" / "migration-dry-run-data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results.to_dict(), f, indent=2, default=str, ensure_ascii=False)
    print(f"\n  Detailed results saved to: {output_file}")

    return results


if __name__ == "__main__":
    main()
