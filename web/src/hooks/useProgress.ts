import { useQuery } from '@tanstack/react-query'
import { progressApi, type ProgressStats } from '@/api/progress'
import { errorsApi } from '@/api/errors'
import { subDays, format } from 'date-fns'

// ── Check if API is configured ──────────────────────────────────

function isApiConfigured(): boolean {
  const url = import.meta.env.VITE_API_BASE_URL
  return !!url && !url.includes('placeholder')
}

// ── Daily activity for heatmap ───────────────────────────────────────

export function useDailyActivity(userId: string | undefined, days = 365) {
  return useQuery({
    queryKey: ['progress', 'activity', userId, days],
    queryFn: async () => {
      if (!userId) return {}
      if (!isApiConfigured()) {
        // Fallback: return empty activity
        const activity: Record<string, number> = {}
        for (let i = 0; i < days; i++) {
          const d = subDays(new Date(), i)
          activity[format(d, 'yyyy-MM-dd')] = 0
        }
        return activity
      }

      const data = await progressApi.getActivity(days)
      return data.activity
    },
    enabled: !!userId,
  })
}

// ── Stats summary ────────────────────────────────────────────────────

export function useProgressStats(userId: string | undefined) {
  return useQuery({
    queryKey: ['progress', 'stats', userId],
    queryFn: async () => {
      if (!userId) return null
      if (!isApiConfigured()) return null

      return await progressApi.getStats()
    },
    enabled: !!userId,
  })
}

// ── Error journal ────────────────────────────────────────────────────

export function useErrorJournal(userId: string | undefined) {
  return useQuery({
    queryKey: ['progress', 'errors', userId],
    queryFn: async () => {
      if (!userId) return []
      if (!isApiConfigured()) return []
      return await errorsApi.list(200)
    },
    enabled: !!userId,
  })
}
