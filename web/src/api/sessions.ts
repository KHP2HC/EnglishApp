/**
 * Study sessions API client
 */

import { api } from './client'
import type { StudySession, SessionType } from '@/lib/supabase'

export const sessionsApi = {
  list: (limit = 100) =>
    api.get<StudySession[]>(`/api/v1/study-sessions?limit=${limit}`),

  start: (sessionType: SessionType) =>
    api.post<StudySession>('/api/v1/study-sessions', {
      session_type: sessionType,
    }),

  update: (
    sessionId: string,
    updates: {
      ended_at?: string
      xp_earned?: number
      items_total?: number
      items_correct?: number
    },
  ) => api.patch<StudySession>(`/api/v1/study-sessions/${sessionId}`, updates),

  get: (sessionId: string) =>
    api.get<StudySession>(`/api/v1/study-sessions/${sessionId}`),
}
