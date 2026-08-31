# Database Validation Plan

Validation checks to run before, during, and after the database
migration from SQLite/Supabase to the canonical PostgreSQL schema.

---

## Pre-Migration Validation

Run these checks on the **source databases** before any migration.

### 1. Row Count Baseline

Record row counts for every table in both databases.

| Table | SQLite count | Supabase count | Notes |
|-------|-------------|----------------|-------|
| `users` / `profiles` | — | — | |
| `vocabulary_cards` / `vocab_cards` | — | — | |
| `user_vocab_progress` / `vocab_progress` | — | — | |
| `study_sessions` | — | — | |
| `error_journal` | — | — | |
| `study_plans` | — | — | |
| `content_cache` | — | — | |
| `writing_submissions` | N/A | — | SQLite only: N/A |

**SQL (Supabase):**
```sql
select 'profiles' as t, count(*) from profiles
union all select 'vocab_cards', count(*) from vocab_cards
union all select 'vocab_progress', count(*) from vocab_progress
union all select 'study_sessions', count(*) from study_sessions
union all select 'error_journal', count(*) from error_journal
union all select 'study_plans', count(*) from study_plans
union all select 'content_cache', count(*) from content_cache
union all select 'writing_submissions', count(*) from writing_submissions;
```

**SQL (SQLite):**
```sql
select 'users' as t, count(*) from users
union all select 'vocabulary_cards', count(*) from vocabulary_cards
union all select 'user_vocab_progress', count(*) from user_vocab_progress
union all select 'study_sessions', count(*) from study_sessions
union all select 'error_journal', count(*) from error_journal
union all select 'study_plans', count(*) from study_plans
union all select 'content_cache', count(*) from content_cache;
```

### 2. Orphan Detection (Source)

Detect rows with broken foreign keys before migration.

| Check | SQL (SQLite) | SQL (Supabase) |
|-------|-------------|----------------|
| vocab_progress → users | `select count(*) from user_vocab_progress where user_id not in (select id from users)` | `select count(*) from vocab_progress where user_id not in (select id from profiles)` |
| vocab_progress → vocab_cards | `select count(*) from user_vocab_progress where card_id not in (select id from vocabulary_cards)` | `select count(*) from vocab_progress where card_id not in (select id from vocab_cards)` |
| study_sessions → users | `select count(*) from study_sessions where user_id not in (select id from users)` | `select count(*) from study_sessions where user_id not in (select id from profiles)` |
| error_journal → users | `select count(*) from error_journal where user_id not in (select id from users)` | `select count(*) from error_journal where user_id not in (select id from profiles)` |
| error_journal → study_sessions | `select count(*) from error_journal where session_id is not null and session_id not in (select id from study_sessions)` | Same pattern |
| study_plans → users | `select count(*) from study_plans where user_id not in (select id from users)` | Same pattern |

**Expected:** 0 orphans. If any found, fix or document before migrating.

### 3. Duplicate Detection (Source)

| Check | SQL |
|-------|-----|
| Duplicate words in vocab_cards | `select word, count(*) from vocab_cards group by word having count(*) > 1` |
| Duplicate (user_id, card_id) in vocab_progress | `select user_id, card_id, count(*) from vocab_progress group by user_id, card_id having count(*) > 1` |
| Duplicate (user_id, week_start) in study_plans | `select user_id, week_start, count(*) from study_plans group by user_id, week_start having count(*) > 1` |

---

## During-Migration Validation

Run these checks **after each table is migrated**.

### 4. Row Count Reconciliation

For each table, verify:
```
source_count == migrated_count
```

| Table | Source (SQLite + Supabase) | Migrated (canonical) | Match? |
|-------|---------------------------|----------------------|-------|
| profiles | SQLite users + Supabase profiles | — | |
| vocab_cards | SQLite vocabulary_cards + Supabase vocab_cards (dedup by word) | — | |
| vocab_progress | SQLite user_vocab_progress + Supabase vocab_progress | — | |
| study_sessions | SQLite study_sessions + Supabase study_sessions | — | |
| error_journal | SQLite error_journal + Supabase error_journal | — | |
| study_plans | SQLite study_plans + Supabase study_plans | — | |
| writing_submissions | Supabase writing_submissions | — | |

> ⚠️ `vocab_cards` may have duplicates across SQLite and Supabase
> (same word in both). Deduplicate by `word` — keep the Supabase
> version (has UUID) and map the SQLite ID to it.

### 5. Foreign Key Validation (Post-Migration)

```sql
-- vocab_progress must reference valid profiles and vocab_cards
select count(*) as orphan_progress_users
from vocab_progress vp
left join profiles p on vp.user_id = p.id
where p.id is null;

select count(*) as orphan_progress_cards
from vocab_progress vp
left join vocab_cards vc on vp.card_id = vc.id
where vc.id is null;

-- study_sessions must reference valid profiles
select count(*) as orphan_sessions
from study_sessions ss
left join profiles p on ss.user_id = p.id
where p.id is null;

-- error_journal must reference valid profiles
select count(*) as orphan_errors
from error_journal ej
left join profiles p on ej.user_id = p.id
where p.id is null;

-- study_plans must reference valid profiles
select count(*) as orphan_plans
from study_plans sp
left join profiles p on sp.user_id = p.id
where p.id is null;
```

**Expected:** All counts = 0.

### 6. Unique Constraint Validation

```sql
-- No duplicate (user_id, card_id) in vocab_progress
select user_id, card_id, count(*)
from vocab_progress
group by user_id, card_id
having count(*) > 1;

-- No duplicate (user_id, week_start) in study_plans
select user_id, week_start, count(*)
from study_plans
group by user_id, week_start
having count(*) > 1;

-- No duplicate words in vocab_cards
select word, count(*)
from vocab_cards
group by word
having count(*) > 1;
```

**Expected:** All queries return 0 rows.

### 7. Nullability Validation

```sql
-- profiles: name must not be null
select count(*) from profiles where name is null;

-- vocab_cards: word, meaning_en, meaning_vi must not be null
select count(*) from vocab_cards where word is null or meaning_en is null or meaning_vi is null;

-- vocab_progress: user_id, card_id must not be null
select count(*) from vocab_progress where user_id is null or card_id is null;

-- study_plans: week_start must not be null
select count(*) from study_plans where week_start is null;
```

**Expected:** All counts = 0.

### 8. Timestamp Validation

```sql
-- created_at must not be in the future
select count(*) from profiles where created_at > now();
select count(*) from study_sessions where started_at > now();

-- ended_at must be after started_at (if not null)
select count(*) from study_sessions
where ended_at is not null and ended_at < started_at;

-- updated_at must be >= created_at
select count(*) from profiles where updated_at < created_at;
select count(*) from vocab_progress where updated_at < created_at;
```

**Expected:** All counts = 0.

### 9. User Ownership Validation

```sql
-- Every vocab_progress row's user_id must exist in profiles
select count(*) from vocab_progress vp
where not exists (select 1 from profiles p where p.id = vp.user_id);

-- Every study_session row's user_id must exist in profiles
select count(*) from study_sessions ss
where not exists (select 1 from profiles p where p.id = ss.user_id);

-- Every error_journal row's user_id must exist in profiles
select count(*) from error_journal ej
where not exists (select 1 from profiles p where p.id = ej.user_id);
```

**Expected:** All counts = 0.

### 10. ID Mapping Validation

After migrating SQLite INTEGER IDs to UUIDs:

```sql
-- Every SQLite user should have a UUID mapping
-- (using the migration_id_map table)
select count(*) as unmigrated_users
from sqlite_users_legacy s
where not exists (
  select 1 from migration_id_map m
  where m.table_name = 'users' and m.sqlite_id = s.id
);
```

**Expected:** 0 unmigrated records.

---

## Post-Migration Validation

### 11. RLS Policy Validation

After enabling RLS on canonical tables:

```sql
-- Test: user can only see their own profile
-- Run as a specific user (using set_config)
set request.jwt.claim.sub = '<test-user-uuid>';
select count(*) from profiles;  -- Should be 1 (own profile)
select count(*) from vocab_progress;  -- Should be only user's progress
select count(*) from study_sessions;  -- Should be only user's sessions

-- Test: anon user cannot see any user data
set role anon;
select count(*) from profiles;  -- Should be 0
select count(*) from vocab_progress;  -- Should be 0
```

### 12. Data Integrity Summary

| Check | Method | Pass Criteria |
|-------|--------|---------------|
| Row counts match | Compare source vs target | Exact match (after dedup) |
| No orphans | FK validation queries | 0 orphans |
| No duplicates | Unique constraint queries | 0 duplicates |
| No null violations | Nullability queries | 0 violations |
| Timestamps valid | Timestamp queries | 0 invalid |
| Ownership correct | Ownership queries | 0 violations |
| RLS enforced | RLS test queries | Users see only own data |

---

## Validation Script Template

```python
"""Post-migration validation script.

Run after migrating data to the canonical Supabase schema.
Reports any data integrity issues.
"""

import os
from supabase import create_client

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
sb = create_client(url, key)

checks = [
    ("orphan_progress_users", "vocab_progress", "user_id", "profiles", "id"),
    ("orphan_progress_cards", "vocab_progress", "card_id", "vocab_cards", "id"),
    ("orphan_sessions", "study_sessions", "user_id", "profiles", "id"),
    ("orphan_errors", "error_journal", "user_id", "profiles", "id"),
    ("orphan_plans", "study_plans", "user_id", "profiles", "id"),
]

all_passed = True
for name, child, fk, parent, pk in checks:
    result = sb.rpc("check_orphan", {
        "child_table": child, "fk_col": fk,
        "parent_table": parent, "pk_col": pk,
    }).execute()
    count = result.data[0]["count"] if result.data else -1
    status = "PASS" if count == 0 else "FAIL"
    if count != 0:
        all_passed = False
    print(f"{status}: {name} = {count}")

print("\n" + ("All checks passed!" if all_passed else "VALIDATION FAILED!"))
```

---

## Rollback Plan

If validation fails:

1. **Do NOT drop the canonical tables.**
2. Identify the failing check(s).
3. Fix the data in the canonical tables (re-run migration for
   affected rows).
4. Re-run validation.
5. If unfixable, keep clients on the source database until resolved.

The source databases (SQLite + original Supabase tables) remain
untouched until Phase 2F (cleanup), providing a full rollback path.
