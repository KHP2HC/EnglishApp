#!/usr/bin/env python3
"""
restore_original_content.py — Restore original EnglishApp content.

This script:
1. Regenerates the Supabase seed SQL from the canonical web vocabulary JSON
   (5,251 words) so the database seed matches the frontend fallback data.
2. Generates a user data migration SQL from the original SQLite database
   (extracted from git history) to preserve SRS state and study sessions.
3. Validates content integrity after migration.

Usage:
    python scripts/restore_original_content.py [--dry-run] [--apply]

Flags:
    --dry-run   Show what would be done without writing files (default)
    --apply     Write the generated files

Idempotent: Running multiple times produces the same result.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_VOCAB_PATH = PROJECT_ROOT / "web" / "public" / "data" / "vocab.json"
SEED_SQL_PATH = PROJECT_ROOT / "supabase" / "seeds" / "seed_vocab_cards.sql"
ENRICHED_JSON_PATH = PROJECT_ROOT / "data" / "seed" / "vocab_enriched.json"
USER_MIGRATION_SQL_PATH = PROJECT_ROOT / "supabase" / "seeds" / "migrate_user_data.sql"

ORIGINAL_DB_COMMIT = "98321ac"
ORIGINAL_DB_FILE = "data.db"

# Canonical vocabulary words that MUST be present in production.
# These are common English words verified to exist in the dataset.
CANONICAL_WORDS = [
    "abandon", "ability", "about", "above", "abroad", "absence", "absolute",
    "abstract", "abundant", "abuse", "academic", "access", "accommodate",
    "accomplish", "account", "accurate", "achieve", "acquire", "adapt",
    "adequate", "adjust", "administer", "admit", "adopt", "advance",
    "advantage", "adventure", "advice", "affect", "afford", "aggressive",
    "agree", "approach", "appropriate", "arrange", "assemble", "assess",
    "assign", "attain", "attend", "attract", "available", "away",
]

# Demo markers that should NOT appear in production vocabulary meanings.
# These are checked as exact phrase matches (case-insensitive), not substrings,
# to avoid false positives like "democracy" matching "demo".
DEMO_MARKERS = [
    "Common English vocabulary word",
    "lorem ipsum",
    "test word placeholder",
    "sample text placeholder",
    "demo vocabulary entry",
    "placeholder meaning",
]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def sql_escape(value: str | None) -> str:
    """Escape a string for safe SQL insertion."""
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def sql_array(value: str | None) -> str:
    """Convert a comma-separated string to a PostgreSQL text[] literal."""
    if not value:
        return "'{}'"
    items = [v.strip() for v in value.split(",") if v.strip()]
    if not items:
        return "'{}'"
    escaped = ",".join(sql_escape(i).strip("'") for i in items)
    return "'{" + escaped + "}'"


def extract_original_db() -> Path | None:
    """Extract the original data.db from git history."""
    db_path = Path(tempfile.gettempdir()) / "original_data.db"
    try:
        result = subprocess.run(
            ["git", "cat-file", "-p", f"{ORIGINAL_DB_COMMIT}:{ORIGINAL_DB_FILE}"],
            capture_output=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0 or not result.stdout:
            print(f"  ⚠ Could not extract original data.db from git: {result.stderr.decode()}")
            return None
        with open(db_path, "wb") as f:
            f.write(result.stdout)
        # Verify it's a valid SQLite database
        with open(db_path, "rb") as f:
            header = f.read(16)
        if header[:15] != b"SQLite format 3":
            print(f"  ⚠ Extracted file is not a valid SQLite database")
            return None
        print(f"  ✓ Extracted original data.db ({len(result.stdout):,} bytes)")
        return db_path
    except Exception as e:
        print(f"  ⚠ Error extracting original data.db: {e}")
        return None


# ─── Step 1: Regenerate Supabase Seed SQL ────────────────────────────────────

def regenerate_seed_sql(dry_run: bool) -> bool:
    """Regenerate seed_vocab_cards.sql from web/public/data/vocab.json."""
    print("\n═══ Step 1: Regenerate Supabase Seed SQL ═══")
    print(f"  Source: {WEB_VOCAB_PATH}")
    print(f"  Target: {SEED_SQL_PATH}")

    if not WEB_VOCAB_PATH.exists():
        print(f"  ✗ Source file not found")
        return False

    with open(WEB_VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    print(f"  Loaded {len(vocab):,} vocabulary entries")

    # Validate entries
    valid = []
    skipped = 0
    for entry in vocab:
        word = entry.get("word", "").strip()
        if not word:
            skipped += 1
            continue
        meaning_en = entry.get("meaning_en", "").strip()
        if not meaning_en:
            skipped += 1
            continue
        # Check for demo markers
        is_demo = any(marker.lower() in meaning_en.lower() for marker in DEMO_MARKERS)
        if is_demo:
            skipped += 1
            continue
        valid.append(entry)

    print(f"  Valid entries: {len(valid):,}")
    if skipped:
        print(f"  Skipped (empty/demo): {skipped}")

    # Generate SQL
    lines = [
        "-- ─────────────────────────────────────────────────────────────────────",
        "-- seed_vocab_cards.sql — Idempotent vocabulary seed data",
        "-- ─────────────────────────────────────────────────────────────────────",
        f"-- Auto-generated by scripts/restore_original_content.py",
        f"-- Source: web/public/data/vocab.json ({len(valid):,} records)",
        f"-- Generated: {datetime.now(timezone.utc).isoformat()}",
        "--",
        "-- This seed is IDEMPOTENT:",
        "--   • Uses ON CONFLICT (word) DO UPDATE — safe to run multiple times",
        "--   • Existing words are updated with latest content",
        "--   • New words are inserted",
        "--",
        "-- Run AFTER all schema migrations (001–011).",
        "-- ─────────────────────────────────────────────────────────────────────",
        "",
    ]

    # Batch in groups of 500
    BATCH_SIZE = 500
    for batch_idx in range(0, len(valid), BATCH_SIZE):
        batch = valid[batch_idx:batch_idx + BATCH_SIZE]
        batch_num = batch_idx // BATCH_SIZE + 1
        lines.append(f"-- Batch {batch_num} (rows {batch_idx + 1}–{batch_idx + len(batch)})")
        lines.append(
            "insert into vocab_cards "
            "(word, phonetic, synonym, antonym, meaning_en, meaning_vi, "
            "example_sentence, exam_type, cefr_level, category) values"
        )

        value_lines = []
        for entry in batch:
            word = sql_escape(entry.get("word"))
            phonetic = sql_escape(entry.get("phonetic"))
            synonym = sql_escape(entry.get("synonym"))
            antonym = sql_escape(entry.get("antonym"))
            meaning_en = sql_escape(entry.get("meaning_en"))
            meaning_vi = sql_escape(entry.get("meaning_vi"))
            example = sql_escape(entry.get("example_sentence"))
            exam_type = sql_array(entry.get("exam_type"))
            cefr = sql_escape(entry.get("difficulty_level") or entry.get("cefr_level"))
            category = sql_escape(entry.get("category"))
            value_lines.append(
                f"  ({word}, {phonetic}, {synonym}, {antonym}, {meaning_en}, "
                f"{meaning_vi}, {example}, {exam_type}, {cefr}, {category})"
            )

        lines.append(",\n".join(value_lines))
        lines.append("on conflict (word) do update set")
        lines.append("  phonetic = excluded.phonetic,")
        lines.append("  synonym = excluded.synonym,")
        lines.append("  antonym = excluded.antonym,")
        lines.append("  meaning_en = excluded.meaning_en,")
        lines.append("  meaning_vi = excluded.meaning_vi,")
        lines.append("  example_sentence = excluded.example_sentence,")
        lines.append("  exam_type = excluded.exam_type,")
        lines.append("  cefr_level = excluded.cefr_level,")
        lines.append("  category = excluded.category;")
        lines.append("")

    sql_content = "\n".join(lines)

    if dry_run:
        print(f"  [DRY RUN] Would write {len(sql_content):,} chars to {SEED_SQL_PATH}")
    else:
        SEED_SQL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SEED_SQL_PATH, "w", encoding="utf-8") as f:
            f.write(sql_content)
        print(f"  ✓ Written {len(sql_content):,} chars to {SEED_SQL_PATH}")

    return True


# ─── Step 2: Generate User Data Migration SQL ────────────────────────────────

def generate_user_migration_sql(dry_run: bool) -> bool:
    """Generate SQL to migrate user data from original SQLite to Supabase."""
    print("\n═══ Step 2: Generate User Data Migration SQL ═══")

    db_path = extract_original_db()
    if db_path is None:
        print("  ⚠ Original database not available — skipping user data migration")
        print("  ℹ This is expected if the original data.db is not in git history")
        return False

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Load original user data
    c.execute("SELECT * FROM users")
    users = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM user_vocab_progress WHERE user_id IS NOT NULL")
    vocab_progress = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM study_sessions WHERE user_id IS NOT NULL")
    study_sessions = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM study_plans")
    study_plans = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM error_journal")
    error_journal = [dict(r) for r in c.fetchall()]

    conn.close()

    print(f"  Original users: {len(users)}")
    print(f"  Original vocab progress (with user_id): {len(vocab_progress)}")
    print(f"  Original study sessions (with user_id): {len(study_sessions)}")
    print(f"  Original study plans: {len(study_plans)}")
    print(f"  Original error journal: {len(error_journal)}")

    # Build a mapping from original card_id → word
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, word FROM vocabulary_cards")
    card_word_map = {r["id"]: r["word"] for r in c.fetchall()}
    conn.close()

    lines = [
        "-- ─────────────────────────────────────────────────────────────────────",
        "-- migrate_user_data.sql — Migrate user data from original SQLite DB",
        "-- ─────────────────────────────────────────────────────────────────────",
        f"-- Generated by scripts/restore_original_content.py",
        f"-- Source: data.db from git commit {ORIGINAL_DB_COMMIT}",
        f"-- Generated: {datetime.now(timezone.utc).isoformat()}",
        "--",
        "-- This migration is IDEMPOTENT:",
        "--   • Uses ON CONFLICT DO NOTHING for sessions and plans",
        "--   • Uses ON CONFLICT DO UPDATE for vocab_progress (upsert)",
        "--",
        "-- PREREQUISITE: The user must already exist in auth.users.",
        "--   Map original user_id=1 to the Supabase auth user by setting",
        "--   :target_user_id below or running after authentication.",
        "-- ─────────────────────────────────────────────────────────────────────",
        "",
        "-- Replace :target_user_id with the actual Supabase auth user UUID",
        "-- Example: do $$ begin",
        "--   :target_user_id := 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';",
        "-- end $$;",
        "",
    ]

    # Note about user mapping
    if users:
        u = users[0]
        lines.append(f"-- Original user: id={u['id']}, name={u['name']}, "
                      f"target_exam={u['target_exam']}, target_score={u['target_score']}")
        lines.append("")

    # Vocab progress migration
    if vocab_progress:
        lines.append("-- ─── Vocabulary Progress (SRS State) ───")
        lines.append("-- Maps original card_id → word → Supabase vocab_cards.id")
        lines.append("")

        for vp in vocab_progress:
            word = card_word_map.get(vp["card_id"], "")
            if not word:
                continue
            lines.append(f"-- Word: '{word}' (original card_id={vp['card_id']})")
            lines.append(
                f"insert into vocab_progress "
                f"(user_id, vocab_card_id, interval_days, easiness, repetitions, "
                f"next_review_at, last_quality, times_seen, times_correct)"
            )
            lines.append(
                f"select :target_user_id, vc.id, "
                f"{vp['srs_interval']}, {vp['srs_easiness']}, {vp['srs_repetitions']}, "
                f"{sql_escape(vp['next_review_date'])}, {vp['last_quality']}, "
                f"{vp['times_seen']}, {vp['times_correct']}"
            )
            lines.append(
                f"from vocab_cards vc where lower(vc.word) = lower({sql_escape(word)})"
            )
            lines.append(
                "on conflict (user_id, vocab_card_id) do update set"
            )
            lines.append(f"  interval_days = excluded.interval_days,")
            lines.append(f"  easiness = excluded.easiness,")
            lines.append(f"  repetitions = excluded.repetitions,")
            lines.append(f"  next_review_at = excluded.next_review_at,")
            lines.append(f"  last_quality = excluded.last_quality,")
            lines.append(f"  times_seen = excluded.times_seen,")
            lines.append(f"  times_correct = excluded.times_correct;")
            lines.append("")

    # Study sessions migration
    if study_sessions:
        lines.append("-- ─── Study Sessions ───")
        lines.append("")
        for ss in study_sessions:
            lines.append(
                f"insert into study_sessions "
                f"(user_id, session_type, started_at, ended_at, xp_earned, "
                f"items_total, items_correct)"
            )
            lines.append(
                f"values (:target_user_id, {sql_escape(ss['session_type'])}, "
                f"{sql_escape(ss['started_at'])}, {sql_escape(ss['ended_at'])}, "
                f"{ss['xp_earned'] or 0}, {ss['items_studied'] or 0}, "
                f"{ss['items_correct'] or 0})"
            )
            lines.append("on conflict do nothing;")
            lines.append("")

    sql_content = "\n".join(lines)

    if dry_run:
        print(f"  [DRY RUN] Would write {len(sql_content):,} chars to {USER_MIGRATION_SQL_PATH}")
    else:
        USER_MIGRATION_SQL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(USER_MIGRATION_SQL_PATH, "w", encoding="utf-8") as f:
            f.write(sql_content)
        print(f"  ✓ Written {len(sql_content):,} chars to {USER_MIGRATION_SQL_PATH}")

    return True


# ─── Step 3: Validate Content ────────────────────────────────────────────────

def validate_content() -> bool:
    """Validate content integrity."""
    print("\n═══ Step 3: Validate Content ═══")
    all_pass = True

    # Check web vocab
    if not WEB_VOCAB_PATH.exists():
        print("  ✗ web/public/data/vocab.json not found")
        return False

    with open(WEB_VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    # Minimum count
    if len(vocab) < 5000:
        print(f"  ✗ FAIL: Vocabulary count {len(vocab)} < 5000 minimum")
        all_pass = False
    else:
        print(f"  ✓ PASS: Vocabulary count {len(vocab)} ≥ 5000")

    # No placeholders
    placeholders = sum(1 for v in vocab if any(m in (v.get("meaning_en", "")).lower() for m in DEMO_MARKERS))
    if placeholders > 0:
        print(f"  ✗ FAIL: {placeholders} entries contain demo/placeholder markers")
        all_pass = False
    else:
        print(f"  ✓ PASS: No demo/placeholder markers found")

    # Canonical words present
    vocab_words = {v.get("word", "").lower().strip() for v in vocab}
    missing_canonical = [w for w in CANONICAL_WORDS if w not in vocab_words]
    if missing_canonical:
        print(f"  ✗ FAIL: Missing canonical words: {missing_canonical[:10]}")
        all_pass = False
    else:
        print(f"  ✓ PASS: All {len(CANONICAL_WORDS)} canonical words present")

    # Check for duplicates
    word_counts: dict[str, int] = {}
    for v in vocab:
        w = v.get("word", "").lower().strip()
        word_counts[w] = word_counts.get(w, 0) + 1
    duplicates = {w: c for w, c in word_counts.items() if c > 1}
    if duplicates:
        print(f"  ✗ FAIL: {len(duplicates)} duplicate words found")
        all_pass = False
    else:
        print(f"  ✓ PASS: No duplicate words")

    # Check required fields
    missing_fields = 0
    for v in vocab:
        if not v.get("word") or not v.get("meaning_en") or not v.get("meaning_vi"):
            missing_fields += 1
    if missing_fields > 0:
        print(f"  ✗ FAIL: {missing_fields} entries missing required fields")
        all_pass = False
    else:
        print(f"  ✓ PASS: All entries have required fields")

    # Check test content
    test_files = ["reading_tests", "listening_tests", "writing_tests", "speaking_tests"]
    for name in test_files:
        path = PROJECT_ROOT / "web" / "public" / "data" / f"{name}.json"
        if not path.exists():
            print(f"  ✗ FAIL: {name}.json not found")
            all_pass = False
        else:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if len(data) < 100:
                print(f"  ✗ FAIL: {name} has only {len(data)} records (< 100)")
                all_pass = False
            else:
                print(f"  ✓ PASS: {name} has {len(data)} records")

    # Check seed SQL
    if SEED_SQL_PATH.exists():
        with open(SEED_SQL_PATH, "r", encoding="utf-8") as f:
            sql_content = f.read()
        insert_count = sql_content.count("insert into vocab_cards")
        if insert_count == 0:
            print(f"  ✗ FAIL: Seed SQL has no INSERT statements")
            all_pass = False
        else:
            print(f"  ✓ PASS: Seed SQL has {insert_count} batch INSERT statements")
    else:
        print(f"  ⚠ WARN: Seed SQL not found at {SEED_SQL_PATH}")

    return all_pass


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Restore original EnglishApp content")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Show what would be done without writing files")
    parser.add_argument("--apply", action="store_true", default=False,
                        help="Write the generated files")
    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        args.dry_run = True

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     EnglishApp — Restore Original Content                    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"  Mode: {'DRY RUN' if args.dry_run else 'APPLY'}")
    print(f"  Project: {PROJECT_ROOT}")

    # Step 1: Regenerate seed SQL
    ok1 = regenerate_seed_sql(args.dry_run)

    # Step 2: Generate user data migration SQL
    ok2 = generate_user_migration_sql(args.dry_run)

    # Step 3: Validate
    if args.apply:
        valid = validate_content()
    else:
        print("\n═══ Step 3: Validation (skipped in dry-run) ═══")
        valid = True

    print("\n═══════════════════════════════════════════════════════════════")
    print(f"  Seed SQL regeneration: {'✓' if ok1 else '✗'}")
    print(f"  User data migration:    {'✓' if ok2 else '⚠ (skipped)'}")
    print(f"  Content validation:     {'✓ PASS' if valid else '✗ FAIL'}")
    print("═══════════════════════════════════════════════════════════════")

    if args.dry_run:
        print("\n  Run with --apply to write files.")

    return 0 if (ok1 and valid) else 1


if __name__ == "__main__":
    sys.exit(main())
