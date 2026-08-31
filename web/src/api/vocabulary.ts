/**
 * Vocabulary API client
 */

import { api } from './client'
import type { VocabCard } from '@/lib/supabase'

export interface VocabListResponse {
  items: VocabCard[]
  total: number
  page: number
  page_size: number
  has_next: boolean
}

export const vocabularyApi = {
  list: (params?: {
    page?: number
    page_size?: number
    search?: string
    cefr_level?: string
    category?: string
    exam_type?: string
  }) => {
    const search = new URLSearchParams()
    if (params?.page) search.set('page', String(params.page))
    if (params?.page_size) search.set('page_size', String(params.page_size))
    if (params?.search) search.set('search', params.search)
    if (params?.cefr_level) search.set('cefr_level', params.cefr_level)
    if (params?.category) search.set('category', params.category)
    if (params?.exam_type) search.set('exam_type', params.exam_type)
    const qs = search.toString()
    return api.get<VocabListResponse>(`/api/v1/vocabulary${qs ? `?${qs}` : ''}`)
  },

  get: (cardId: string) => api.get<VocabCard>(`/api/v1/vocabulary/${cardId}`),
}
