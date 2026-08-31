/**
 * Reviews (SRS) API client
 */

import { api } from './client'
import type { VocabCard, VocabProgress } from '@/lib/supabase'
import type { Quality } from '@/lib/srs'

export interface DueCardsResponse {
  review_cards: (VocabProgress & { card?: VocabCard })[]
  new_cards: VocabCard[]
}

export interface RateCardResponse {
  id: string
  interval_days: number
  easiness: number
  repetitions: number
  next_review_at: string | null
  last_quality: number
  times_seen: number
  times_correct: number
  xp_earned: number
}

export const reviewsApi = {
  getDue: () => api.get<DueCardsResponse>('/api/v1/reviews/due'),

  start: (cardId: string) =>
    api.post<VocabProgress>('/api/v1/reviews/start', { card_id: cardId }),

  rate: (cardId: string, quality: Quality) =>
    api.post<RateCardResponse>('/api/v1/reviews/rate', {
      card_id: cardId,
      quality,
    }),
}
