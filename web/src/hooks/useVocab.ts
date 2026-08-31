/// <reference types="vite/client" />
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { reviewsApi, type DueCardsResponse } from '@/api/reviews'
import type { VocabCard, VocabProgress } from '@/lib/supabase'
import { sm2Update, type Quality } from '@/lib/srs'
import { cacheSessionCards } from '@/lib/offline'
import { loadVocabData, seedToVocabCard, formatSynonym } from '@/lib/seed-data'

// ── Check if API is configured ──────────────────────────────────

function isApiConfigured(): boolean {
  const url = import.meta.env.VITE_API_BASE_URL
  return !!url && !url.includes('placeholder')
}

// ── Local SRS progress (fallback when API not configured) ────────

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
      // If API is not configured, use local seed data
      if (!isApiConfigured() || !userId) {
        return await loadFromSeed()
      }

      try {
        const data = await reviewsApi.getDue()

        // Cache for offline use
        const allCards = [
          ...data.review_cards.map((p) => p.card).filter(Boolean),
          ...data.new_cards,
        ] as VocabCard[]
        await cacheSessionCards(allCards)

        return data
      } catch {
        // API unreachable (CORS, network, server down) — fall back to seed data
        return await loadFromSeed()
      }
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  })
}

// ── Load from local seed data (no Supabase) ──────────────────────────

async function loadFromSeed(): Promise<DueCardsResponse> {
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

  return { review_cards: reviewCards, new_cards: newCards }
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

      if (isApiConfigured()) {
        try {
          return await reviewsApi.rate(progress.card_id, quality)
        } catch {
          // API unreachable — fall back to local
        }
      }
      // Local mode: save to localStorage
      const cardId = progress.card_id
      const local = getLocalProgress()
      local[cardId] = { ...updated, card_id: cardId }
      saveLocalProgress(local)
      return { ...progress, ...updated }
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
      if (isApiConfigured()) {
        try {
          return await reviewsApi.start(cardId)
        } catch {
          // API unreachable — fall back to local
        }
      }
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
    queryFn: async () => {
      const { getOfflineCards } = await import('@/lib/offline')
      return getOfflineCards()
    },
    enabled: false, // manually triggered
  })
}
