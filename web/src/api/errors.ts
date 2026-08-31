/**
 * Errors (error journal) API client
 */

import { api } from './client'
import type { ErrorJournalEntry } from '@/lib/supabase'

export const errorsApi = {
  list: (limit = 200, skill?: string) => {
    const params = new URLSearchParams({ limit: String(limit) })
    if (skill) params.set('skill', skill)
    return api.get<ErrorJournalEntry[]>(`/api/v1/errors?${params.toString()}`)
  },

  create: (data: {
    session_id?: string
    error_category?: string
    skill?: string
    question_snapshot?: string
    user_answer?: string
    correct_answer?: string
  }) => api.post<ErrorJournalEntry>('/api/v1/errors', data),

  delete: (errorId: string) => api.delete<void>(`/api/v1/errors/${errorId}`),
}
