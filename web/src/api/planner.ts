/**
 * Planner API client
 */

import { api } from './client'
import type { DailyTask } from '@/lib/planner'

export interface StudyPlan {
  id: string
  user_id: string
  week_start: string
  daily_tasks: Record<string, DailyTask[]>
  created_at?: string
  updated_at?: string
}

export const plannerApi = {
  get: () => api.get<StudyPlan>('/api/v1/planner'),

  generate: (overrides?: {
    target_exam?: string
    target_score?: number
    current_band?: number
    exam_date?: string
    free_time?: Record<string, number>
  }) => api.post<StudyPlan>('/api/v1/planner', overrides || {}),
}
