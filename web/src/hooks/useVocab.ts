/// <reference types="vite/client" />
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase, type VocabCard, type VocabProgress } from '@/lib/supabase'
import { sm2Update, type Quality } from '@/lib/srs'
import { cacheSessionCards, queuePendingUpdate, getOfflineCards, isOnline } from '@/lib/offline'
import { loadVocabData, seedToVocabCard, formatSynonym, type SeedVocabEntry } from '@/lib/seed-data'

// ── Check if Supabase is configured ──────────────────────────────────

function isSupabaseConfigured(): boolean {
  const url = import.meta.env.VITE_SUPABASE_URL
  return !!url && !url.includes('placeholder')
}

// ── Local SRS progress (IndexedDB-backed, no Supabase needed) ────────

const LOCAL_PROGRESS_KEY = 'ecp_vocab_progress'

interface LocalProgress {
  card_id: string
  interval_days: number
  easiness: number
  repetitions: number
  next_review: string
  last_quality: number | null
  times_seen: number
  times_correct: number
}

function getLocalProgress(): Record<string, LocalProgress> {
  try {
    const raw = localStorage.getItem(LOCAL_PROGRESS_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function saveLocalProgress(data: Record<string, LocalProgress>) {
  localStorage.setItem(LOCAL_PROGRESS_KEY, JSON.stringify(data))
}

// ── Fetch due cards ──────────────────────────────────────────────────

export function useDueCards(userId: string | undefined) {
  return useQuery({
    queryKey: ['vocab', 'due', userId],
    queryFn: async () => {
      // If Supabase is not configured, use local seed data
      if (!isSupabaseConfigured() || !userId) {
        return await loadFromSeed()
      }

      const today = new Date().toISOString().split('T')[0]

      // Get progress rows that are due
      const { data: progress, error: pErr } = await supabase
        .from('vocab_progress')
        .select('*, card:vocab_cards(*)')
        .eq('user_id', userId)
        .lte('next_review', today)
        .limit(50)

      if (pErr) throw pErr

      // Get new cards (no progress yet)
      const { data: newCards, error: nErr } = await supabase
        .from('vocab_cards')
        .select('*')
        .limit(20)

      if (nErr) throw nErr

      const existingCardIds = new Set(progress?.map((p) => p.card_id) || [])
      const freshCards = (newCards || []).filter((c) => !existingCardIds.has(c.id))

      // Cache for offline use
      const allCards = [...(progress?.map((p) => p.card) || []), ...freshCards]
      await cacheSessionCards(allCards.filter(Boolean) as VocabCard[])

      return {
        reviewCards: progress || [],
        newCards: freshCards,
      }
    },
    staleTime: 5 * 60 * 1000,
  })
}

// ── Load from local seed data (no Supabase) ──────────────────────────

async function loadFromSeed() {
  const seedData = await loadVocabData()
  const today = new Date().toISOString().split('T')[0]
  const localProgress = getLocalProgress()

  const reviewCards: any[] = []
  const newCards: VocabCard[] = []

  // Shuffle and take a subset
  const shuffled = [...seedData].sort(() => Math.random() - 0.5)
  const sessionSize = Math.min(30, shuffled.length)

  for (let i = 0; i < sessionSize; i++) {
    const entry = shuffled[i]
    const cardId = `seed-${i}`
    const card: any = seedToVocabCard(entry, cardId)
    // Enrich with synonym/antonym
    card.synonym = formatSynonym(entry.synonym)
    card.antonym = formatSynonym(entry.antonym)

    const progress = localProgress[cardId]
    if (progress && progress.next_review <= today) {
      reviewCards.push({ ...progress, card })
    } else if (!progress) {
      newCards.push(card)
    }
  }

  // Cache for offline
  const allCards = [...reviewCards.map((p) => p.card), ...newCards]
  await cacheSessionCards(allCards.filter(Boolean) as VocabCard[])

  return { reviewCards, newCards }
}

// ── Rate a card (SM-2 update) ────────────────────────────────────────

export function useRateCard(userId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      progress,
      quality,
    }: {
      progress: VocabProgress
      quality: Quality
    }) => {
      const updated = sm2Update(
        {
          interval_days: progress.interval_days,
          easiness: progress.easiness,
          repetitions: progress.repetitions,
          next_review: progress.next_review,
          last_quality: progress.last_quality,
          times_seen: progress.times_seen,
          times_correct: progress.times_correct,
        },
        quality
      )

      if (isSupabaseConfigured() && (await isOnline())) {
        const { data, error } = await supabase
          .from('vocab_progress')
          .update({
            interval_days: updated.interval_days,
            easiness: updated.easiness,
            repetitions: updated.repetitions,
            next_review: updated.next_review,
            last_quality: updated.last_quality,
            times_seen: updated.times_seen,
            times_correct: updated.times_correct,
          })
          .eq('id', progress.id)
          .select()
          .single()

        if (error) throw error
        return data
      } else {
        // Local mode: save to localStorage
        const cardId = progress.card_id
        const local = getLocalProgress()
        local[cardId] = { ...updated, card_id: cardId }
        saveLocalProgress(local)
        return { ...progress, ...updated }
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vocab', 'due'] })
      queryClient.invalidateQueries({ queryKey: ['progress', 'stats'] })
    },
  })
}

// ── Create new progress row (for new cards) ──────────────────────────

export function useStartCard(userId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (cardId: string) => {
      if (!isSupabaseConfigured()) {
        // Local mode: create progress entry in localStorage
        const local = getLocalProgress()
        local[cardId] = {
          card_id: cardId,
          interval_days: 1,
          easiness: 2.5,
          repetitions: 0,
          next_review: new Date().toISOString().split('T')[0],
          last_quality: null,
          times_seen: 0,
          times_correct: 0,
        }
        saveLocalProgress(local)
        return local[cardId]
      }

      const { data, error } = await supabase
        .from('vocab_progress')
        .insert({
          user_id: userId,
          card_id: cardId,
          interval_days: 1,
          easiness: 2.5,
          repetitions: 0,
          next_review: new Date().toISOString().split('T')[0],
        })
        .select()
        .single()

      if (error) throw error
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vocab', 'due'] })
    },
  })
}

// ── Offline fallback ──────────────────────────────────────────────────

export function useOfflineCards() {
  return useQuery({
    queryKey: ['vocab', 'offline'],
    queryFn: getOfflineCards,
    enabled: false, // manually triggered
  })
}
