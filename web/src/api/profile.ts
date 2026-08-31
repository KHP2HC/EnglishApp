/**
 * Profile API client
 */

import { api } from './client'
import type { Profile } from '@/lib/supabase'

export const profileApi = {
  get: () => api.get<Profile>('/api/v1/profile'),

  update: (updates: Partial<Profile>) =>
    api.patch<Profile>('/api/v1/profile', updates),
}
