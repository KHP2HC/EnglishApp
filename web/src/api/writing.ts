/**
 * Writing API client
 */

import { api } from './client'
import type { WritingSubmission } from '@/lib/supabase'

export const writingApi = {
  list: (limit = 50) =>
    api.get<WritingSubmission[]>(`/api/v1/writing?limit=${limit}`),

  submit: (data: {
    task_prompt: string
    user_essay: string
    exam_type?: string
  }) => api.post<WritingSubmission>('/api/v1/writing', data),
}
