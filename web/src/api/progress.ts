/**
 * Progress API client
 */

import { api } from './client'

export interface ProgressStats {
  words_learned: number
  words_mastered: number
  total_xp: number
  total_sessions: number
  time_by_skill: Record<string, number>
  skill_accuracy: Record<string, { correct: number; total: number }>
  recent_sessions: any[]
}

export const progressApi = {
  getStats: () => api.get<ProgressStats>('/api/v1/progress/stats'),

  getActivity: (days = 365) =>
    api.get<{ activity: Record<string, number> }>(
      `/api/v1/progress/activity?days=${days}`,
    ),
}
