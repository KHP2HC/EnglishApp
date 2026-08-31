#!/usr/bin/env python3
"""
Local migration runner for canonical PostgreSQL schema.

Runs all migration SQL files in deterministic order against a local
PostgreSQL database. Used for local testing and validation.

Usage:
  python supabase/run_migrations.py [--database-url DATABASE_URL]

If no DATABASE_URL is provided, uses the SUPABASE_DB_URL environment
variable, or defaults to a local PostgreSQL instance.

This script does NOT require production credentials.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 is not installed.")
    print("Install with: pip install psycopg2-binary")
    sys.exit(1)


MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
SEEDS_DIR = Path(__file__).resolve().parent / "seeds"

# Deterministic migration order
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

SEED_FILES = [
    "seed_vocab_cards.sql",
]


def run_migrations(database_url: str, include_seeds: bool = False):
    """Run all migration files in order."""
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor()

    # ── Run schema migrations ─────────────────────────────────────────
    print("=" * 70)
    print("Running schema migrations")
    print("=" * 70)

    for filename in MIGRATION_FILES:
        filepath = MIGRATIONS_DIR / filename
        if not filepath.exists():
            print(f"  SKIP (not found): {filename}")
            continue

        sql = filepath.read_text(encoding="utf-8")
        print(f"  Running: {filename} ...", end=" ")

        try:
            cursor.execute(sql)
            print("OK")
        except Exception as e:
            print(f"FAILED")
            print(f"    Error: {e}")
            # Continue — some statements may fail if objects already exist
            # but CREATE IF NOT EXISTS should handle most cases

    # ── Run seed files ────────────────────────────────────────────────
    if include_seeds:
        print()
        print("=" * 70)
        print("Running seed data")
        print("=" * 70)

        for filename in SEED_FILES:
            filepath = SEEDS_DIR / filename
            if not filepath.exists():
                print(f"  SKIP (not found): {filename}")
                continue

            sql = filepath.read_text(encoding="utf-8")
            print(f"  Running: {filename} ...", end=" ")

            try:
                cursor.execute(sql)
                print("OK")
            except Exception as e:
                print(f"FAILED")
                print(f"    Error: {e}")

    # ── Summary ───────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("Migration summary")
    print("=" * 70)

    cursor.execute("""
        select table_name from information_schema.tables
        where table_schema = 'public'
        order by table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  Tables in public schema: {', '.join(tables)}")

    cursor.execute("""
        select count(*) from vocab_cards
    """)
    vocab_count = cursor.fetchone()[0]
    print(f"  vocab_cards count: {vocab_count}")

    cursor.close()
    conn.close()

    print()
    print("Done.")


def main():
    parser = argparse.ArgumentParser(
        description="Run canonical PostgreSQL schema migrations"
    )
    parser.add_argument(
        "--database-url",
        default=os.environ.get("SUPABASE_DB_URL", ""),
        help="PostgreSQL connection string (default: SUPABASE_DB_URL env var)",
    )
    parser.add_argument(
        "--with-seeds",
        action="store_true",
        help="Also run seed data files",
    )
    args = parser.parse_args()

    if not args.database_url:
        print("ERROR: No database URL provided.")
        print("Set SUPABASE_DB_URL or use --database-url")
        print()
        print("For local testing, you can use:")
        print("  --database-url 'postgresql://postgres:postgres@localhost:5432/englishcoach_test'")
        sys.exit(1)

    run_migrations(args.database_url, include_seeds=args.with_seeds)


if __name__ == "__main__":
    main()
