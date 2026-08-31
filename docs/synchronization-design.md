# Synchronization Design — EnglishCoach Pro

## Overview

This document designs a synchronization system that allows the desktop app to work offline with local SQLite, then sync learning data with a central PostgreSQL/Supabase database when online.

## Target Architecture

```
Desktop App (Offline)
    │
    ├── CustomTkinter UI
    ├── Local SQLite (source of truth when offline)
    ├── Sync Queue (pending changes)
    │
    └── When online → FastAPI API → PostgreSQL/Supabase
                                    ↑
Web App (Always online)
    │
    ├── React UI
    └── FastAPI API → PostgreSQL/Supabase (source of truth)
```

---

## 1. Sync Principles

| Principle | Description |
|-----------|-------------|
| **Server-authoritative** | PostgreSQL/Supabase is the source of truth when online |
| **Offline-first desktop** | SQLite is the source of truth when offline |
| **Last-write-wins with timestamps** | Conflicts resolved by `updated_at` timestamp |
| **Idempotent operations** | Replaying a sync operation produces the same result |
| **No data loss** | Sync failures are retried, not discarded |
| **User-visible sync status** | UI shows sync state (synced, pending, error) |

---

## 2. Data Classification

| Data Type | Sync Direction | Conflict Strategy | Delete Strategy |
|-----------|---------------|-------------------|----------------|
| User profile | Bidirectional | Last-write-wins | N/A (soft delete) |
| Vocabulary cards (content) | Server → Client only | N/A (read-only) | N/A |
| Vocab progress (SRS) | Bidirectional | Last-write-wins on `updated_at` | Soft delete via `deleted_at` |
| Study sessions | Client → Server only | No conflict (append-only) | No delete |
| Error journal | Client → Server only | No conflict (append-only) | No delete |
| Study plans | Bidirectional | Last-write-wins | Soft delete |
| Writing submissions | Client → Server only | No conflict (append-only) | No delete |
| Settings/preferences | Bidirectional | Last-write-wins | N/A |

---

## 3. Sync Queue Design

### Table: `sync_queue` (SQLite only)

```sql
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,      -- 'vocab_progress', 'study_session', etc.
    entity_id TEXT NOT NULL,        -- UUID of the entity
    operation TEXT NOT NULL,       -- 'upsert', 'delete'
    payload TEXT NOT NULL,          -- JSON serialization of the entity
    created_at TEXT NOT NULL,       -- ISO timestamp when queued
    attempts INTEGER DEFAULT 0,    -- retry count
    last_error TEXT,                -- last error message
    status TEXT DEFAULT 'pending'   -- 'pending', 'syncing', 'failed'
);
```

### Sync Flow

```
1. User action (e.g., rate a flashcard)
   │
   ├── Write to SQLite (immediate, local)
   ├── Write to sync_queue (async, non-blocking)
   │
2. Background sync worker (every 30s when online)
   │
   ├── Check if online
   ├── If offline → wait and retry
   ├── If online →
   │   ├── Read pending items from sync_queue (batch of 50)
   │   ├── POST /api/v1/sync with batch payload
   │   ├── On success → remove from queue
   │   └── On failure → increment attempts, keep in queue
   │
3. Server processes sync batch
   │
   ├── For each item:
   │   ├── Check if server record has newer `updated_at`
   │   ├── If server is newer → return server version (client updates local)
   │   ├── If client is newer → upsert to PostgreSQL
   │   └── If equal → no-op (idempotent)
   │
4. Server returns sync response
   │
   ├── List of applied changes (with server timestamps)
   ├── List of server-side changes (newer than client's last_sync_at)
   └── List of conflicts (if any)
   │
5. Client applies server changes
   │
   ├── Update local SQLite with server versions
   ├── Update `last_sync_at` timestamp
   └── Notify UI to refresh
```

---

## 4. Conflict Resolution

### Strategy: Last-Write-Wins (LWW) with `updated_at`

Every syncable record must have:
- `updated_at` (timestamp, set on every write)
- `deleted_at` (timestamp, nullable — for soft deletes)
- `client_id` (UUID, generated on client, stable across sync)

### Conflict Scenarios

| Scenario | Resolution |
|----------|------------|
| Client updated, server unchanged | Client wins → upsert to server |
| Server updated, client unchanged | Server wins → update local |
| Both updated, client timestamp newer | Client wins → upsert to server |
| Both updated, server timestamp newer | Server wins → update local |
| Both updated, same timestamp | No-op (idempotent) |
| Client deleted, server updated | Delete wins → soft-delete on server |
| Server deleted, client updated | Delete wins → soft-delete on client |

### Timestamp Handling

- All timestamps in UTC ISO 8601
- Client generates `updated_at` at write time
- Server validates and may override `updated_at` if clock skew detected
- `last_sync_at` stored per-user to track last successful sync

---

## 5. Offline Queue & Retry

### Retry Policy

| Attempt | Delay | Action |
|---------|-------|--------|
| 1 | Immediate | Retry |
| 2 | 5s | Retry |
| 3 | 30s | Retry |
| 4 | 2min | Retry |
| 5 | 10min | Retry |
| 6+ | 1hr | Mark as `failed`, notify user |

### Queue Management

- Maximum queue size: 10,000 items
- If queue exceeds limit, oldest non-failed items are compacted (only latest state kept per entity)
- Failed items require manual intervention or app restart
- Queue persists across app restarts (stored in SQLite)

---

## 6. Idempotency

### Design

- Every sync operation includes a `client_id` (UUID) for the entity
- Server checks if `client_id` already exists with same `updated_at`
- If yes → no-op (already applied)
- If no → upsert

### Example

```
Client rates card "obfuscate" at 10:00:
  payload = {client_id: "abc-123", card_id: "...", quality: 3, updated_at: "2026-01-01T10:00:00Z"}

Sync attempt 1 → network fails → stays in queue
Sync attempt 2 → succeeds → server stores with client_id "abc-123"

If sync attempt 1's request actually reached server but response was lost:
  Server sees client_id "abc-123" already exists → returns success, no duplicate write
```

---

## 7. Delete Handling

### Soft Deletes

- Records are never hard-deleted during sync
- `deleted_at` timestamp marks deletion
- Sync propagates `deleted_at` to both sides
- Periodic cleanup (server-side cron) purges records older than 90 days with `deleted_at` set

### Delete vs Update Conflict

- If one side deletes and the other updates, **delete wins**
- This prevents resurrecting deleted records

---

## 8. Partial Synchronization

### Scenario: User syncs after 7 days offline

1. Client sends `last_sync_at = 2026-01-01T00:00:00Z`
2. Server returns all records modified since that timestamp
3. Client applies changes in order:
   - Schema migrations first (if needed)
   - Content updates (vocab cards)
   - User data updates (progress, sessions, plans)
4. If sync is interrupted:
   - Client stores `last_sync_at` from the last successful batch
   - Next sync resumes from there

### Batch Size

- Maximum 100 records per batch
- Server returns `has_more: true` if more records available
- Client continues fetching until `has_more: false`

---

## 9. API Endpoints (Proposed)

### POST `/api/v1/sync/push`

```
Request:
{
  "user_id": "uuid",
  "changes": [
    {
      "entity_type": "vocab_progress",
      "entity_id": "uuid",
      "operation": "upsert",
      "payload": { ... },
      "client_updated_at": "2026-01-01T10:00:00Z"
    }
  ]
}

Response:
{
  "applied": [...],
  "conflicts": [...],
  "errors": [...]
}
```

### POST `/api/v1/sync/pull`

```
Request:
{
  "user_id": "uuid",
  "last_sync_at": "2026-01-01T00:00:00Z",
  "entity_types": ["vocab_progress", "study_sessions", ...]
}

Response:
{
  "changes": [...],
  "has_more": false,
  "server_time": "2026-01-08T12:00:00Z"
}
```

### GET `/api/v1/sync/status`

```
Response:
{
  "user_id": "uuid",
  "last_sync_at": "2026-01-08T12:00:00Z",
  "pending_count": 0,
  "server_time": "2026-01-08T12:00:01Z"
}
```

---

## 10. Security Considerations

| Concern | Mitigation |
|---------|------------|
| Unauthorized sync | Require JWT auth on all sync endpoints |
| Data tampering | Server validates all payloads against schema |
| Replay attacks | `updated_at` must be within ±5min of server time |
| Queue poisoning | Failed items capped at 6 retries, then quarantined |
| Large payloads | Batch size limit (100), payload size limit (1MB) |

---

## 11. Testing Strategy

| Test | Description |
|------|-------------|
| Offline write → online sync | Write locally, go online, verify server has data |
| Online write → offline read | Write on server, go offline, verify local has data |
| Conflict resolution | Both sides update same record, verify LWW |
| Idempotent replay | Send same sync twice, verify no duplicates |
| Partial sync | Interrupt sync, resume, verify completeness |
| Delete propagation | Delete locally, sync, verify server has `deleted_at` |
| Queue overflow | Generate 10,000+ changes, verify compaction works |
| Network failure | Simulate network failure, verify retry and no data loss |
