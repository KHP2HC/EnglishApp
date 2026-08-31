/**
 * Health API client
 */

import { api } from './client'

export const healthApi = {
  check: () => api.get<{ status: string }>('/api/v1/health'),
}
