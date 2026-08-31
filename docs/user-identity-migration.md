# User Identity Migration Audit

**Phase 2C-1 — Live Database Migration Dry Run**
**Date:** 2026-08-31

---

## 1. SQLite Users Table Inspection

### Schema

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | INTEGER | NOT NULL | — | Auto-increment primary key |
| `name` | VARCHAR(50) | NOT NULL | — | Display name |
| `avatar_emoji` | VARCHAR(4) | NULL | — | Emoji avatar |
| `created_at` | DATETIME | NULL | — | Account creation timestamp |
| `target_exam` | VARCHAR(5) | NULL | — | Target exam (IELTS, TOEIC, etc.) |
| `target_score` | FLOAT | NULL | — | Target score |
| `current_band` | FLOAT | NULL | — | Current band level |
| `exam_date` | DATE | NULL | — | Exam date |
| `daily_free_minutes` | JSON | NULL | — | Daily availability schedule |
| `daily_schedule` | JSON | NULL | — | Detailed daily schedule |
| `preferred_session_time` | VARCHAR(10) | NULL | — | MORNING/AFTERNOON/EVENING |
| `theme_mode` | VARCHAR(20) | NULL | — | dark/light/system |
| `streak_days` | INTEGER | NULL | — | Current streak |
| `total_xp` | INTEGER | NULL | — | Total XP earned |
| `last_active` | DATETIME | NULL | — | Last activity timestamp |

### Data

**Total users:** 1

| Field | Value |
|-------|-------|
| id | 1 |
| name | Phat |
| avatar_emoji | 😊 |
| created_at | 2026-07-13 13:28:51 |
| target_exam | IELTS |
| target_score | 9.0 |
| current_band | NULL |
| exam_date | 2026-10-11 |
| preferred_session_time | MORNING |
| theme_mode | dark |
| streak_days | 1 |
| total_xp | 100 |
| last_active | 2026-08-05 15:35:58 |

---

## 2. Identity Information Assessment

### What Identity Information Exists

| Identity Field | Present? | Value/Notes |
|----------------|----------|-------------|
| **email** | ❌ NO | No email column exists in the SQLite users table |
| **username** | ❌ NO | No username column; `name` is a display name only |
| **display name** | ✅ YES | `name` = "Phat" — display name only, not unique |
| **password hash** | ❌ NO | No password column exists |
| **authentication credentials** | ❌ NO | No auth-related columns |
| **external identity (OAuth)** | ❌ NO | No OAuth provider columns |
| **stable identity identifier** | ⚠️ PARTIAL | `id` (INTEGER auto-increment) is stable within SQLite but not portable |
| **Supabase Auth UUID** | ❌ NO | No UUID or auth reference |

### What Identity Information Does NOT Exist

- **No email address** — the primary identifier for Supabase Auth
- **No username** — no unique login identifier
- **No password hash** — no authentication credentials
- **No OAuth provider** — no external identity linkage
- **No phone number** — no alternative auth method
- **No auth token** — no session or refresh tokens

---

## 3. User Classification

### Category A: Can Be Safely Mapped to an Existing Auth Identity

**Count: 0**

No SQLite users can be directly mapped to an existing Supabase Auth identity
because no email, username, or external identity exists.

### Category B: Requires User Account Claiming

**Count: 1** (user id=1, "Phat")

This user has study data (81 vocab_progress records, 34 study_sessions) but no
auth identity. The data must be preserved and claimed by the user after they
create a Supabase Auth account.

**Claiming strategy:** See Section 5 below.

### Category C: Cannot Currently Be Mapped

**Count: 0**

All users have at least a display name and can be claimed.

---

## 4. Orphaned Data (NULL user_id)

### Study Sessions with NULL user_id

**Count: 10** (out of 44 total)

These sessions were created before user association was implemented. They have
no `user_id` and cannot be migrated to a specific user's account.

**Action:** These 10 sessions are excluded from migration. They represent
pre-user-tracking test data.

### Vocab Progress with NULL user_id

**Count: 2** (out of 83 total)

These progress records were created before user association was implemented.

**Action:** These 2 records are excluded from migration.

---

## 5. Legacy User Data Strategy

### Recommended Strategy: Migration Token + One-Time Claim Process

Since no auth identity exists in SQLite, the safest strategy is:

#### Step 1: Pre-Migration (Automated)

1. For each SQLite user, generate a **deterministic migration UUID** using
   `uuid5(NAMESPACE_DNS, f"legacy-user-{id}")`.
2. Insert a `profiles` row with this UUID and all SQLite user data.
3. Insert a row in `migration_id_map` linking the legacy integer ID to the UUID.
4. Insert a row in a new `migration_claims` table:
   - `legacy_user_id` (INTEGER)
   - `claim_token` (UUID, random)
   - `claimed_by` (UUID, nullable — set when claimed)
   - `expires_at` (TIMESTAMPTZ)
   - `created_at` (TIMESTAMPTZ)

#### Step 2: User Claims Account (Manual)

1. User creates a Supabase Auth account (email + password).
2. User receives or accesses a claim link containing the `claim_token`.
3. The claim endpoint:
   - Verifies the token is valid and unexpired.
   - Updates `migration_claims.claimed_by` with the new auth UID.
   - Updates all related tables (`vocab_progress`, `study_sessions`, etc.)
     to replace the temporary UUID with the real auth UID.
   - Or: creates a `profiles` row with the real auth UID and copies data.

#### Step 3: Cleanup

1. After claim, the temporary `profiles` row (with deterministic UUID) is
   replaced by the real auth UID.
2. `migration_id_map` is updated to point to the real auth UID.
3. After all users are claimed, the `migration_claims` table can be dropped.

### Why This Strategy

| Criterion | This Strategy | Alternative: Direct Auth Creation |
|------------|---------------|--------------------------------|
| Safety | ✅ No fake auth users created | ❌ Would create auth users without email |
| User consent | ✅ User explicitly claims data | ❌ No user consent |
| Email requirement | ✅ User provides their own email | ❌ Would need to invent emails |
| Password security | ✅ User sets their own password | ❌ Would need fake passwords |
| Audit trail | ✅ Full claim audit trail | ❌ No audit trail |
| Reversible | ✅ Can be undone before claim | ❌ Cannot undo auth creation |

### What Is NOT Done

- **No Supabase Auth users are created** during migration.
- **No fake passwords** are generated.
- **No password hashes** are copied.
- **No emails** are invented.
- The claim mechanism is **not implemented** in this phase — only designed.

---

## 6. Dry Run Test Identity

For the dry run, a **TEST identity** was created:

| Field | Value |
|-------|-------|
| Auth email | `test_user_1@dryrun.local` |
| Auth password | `TEST_NO_PASSWORD` (not a real password) |
| Profile UUID | `uuid5(NAMESPACE_DNS, "test-user-1")` |
| Label | **TEST IDENTITY — NOT A REAL USER** |

This test identity exists only in the disposable PostgreSQL database and
will be destroyed when the test database is dropped.

---

## 7. Migration Readiness

| Check | Status | Notes |
|-------|--------|-------|
| User identity mapping | ⚠️ DESIGNED | Strategy designed, not implemented |
| Auth user creation | ✅ NOT DONE | No auth users created (correct) |
| Profile data migration | ✅ TESTED | 1 profile migrated to test DB |
| Claim mechanism | ⚠️ NOT IMPLEMENTED | Designed but not built |
| Orphaned data handling | ✅ DOCUMENTED | 10 sessions + 2 progress records excluded |

**The user identity mapping is RESOLVED at the design level.** The claim
process is safe and does not require creating fake auth users. Implementation
will be done in Phase 2C-2.
