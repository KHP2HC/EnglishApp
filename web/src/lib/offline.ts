import { openDB, type DBSchema, type IDBPDatabase } from 'idb'
import type { VocabCard } from './supabase'

// ── IndexedDB Offline Cache ──────────────────────────────────────────

interface EnglishCoachDB extends DBSchema {
  'offline-vocab': {
    key: string
    value: VocabCard
  }
  'pending-updates': {
    key: string
    value: {
      card_id: string
      quality: number
      timestamp: string
    }
  }
}

let dbPromise: Promise<IDBPDatabase<EnglishCoachDB>> | null = null

function getDB() {
  if (!dbPromise) {
    dbPromise = openDB<EnglishCoachDB>('EnglishCoachPro', 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('offline-vocab')) {
          db.createObjectStore('offline-vocab', { keyPath: 'id' })
        }
        if (!db.objectStoreNames.contains('pending-updates')) {
          db.createObjectStore('pending-updates', { keyPath: 'card_id' })
        }
      },
    })
  }
  return dbPromise
}

export async function cacheSessionCards(cards: VocabCard[]) {
  const db = await getDB()
  const tx = db.transaction('offline-vocab', 'readwrite')
  await Promise.all(cards.map((card) => tx.store.put(card)))
  await tx.done
}

export async function getOfflineCards(): Promise<VocabCard[]> {
  const db = await getDB()
  return db.getAll('offline-vocab')
}

export async function clearOfflineCards() {
  const db = await getDB()
  await db.clear('offline-vocab')
}

export async function queuePendingUpdate(card_id: string, quality: number) {
  const db = await getDB()
  await db.put('pending-updates', {
    card_id,
    quality,
    timestamp: new Date().toISOString(),
  })
}

export async function getPendingUpdates() {
  const db = await getDB()
  return db.getAll('pending-updates')
}

export async function clearPendingUpdates() {
  const db = await getDB()
  await db.clear('pending-updates')
}

export async function isOnline(): Promise<boolean> {
  return navigator.onLine
}
