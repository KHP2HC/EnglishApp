import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { plannerApi, type StudyPlan } from '@/api/planner'
import type { Profile } from '@/lib/supabase'

// ── Check if API is configured ──────────────────────────────────

function isApiConfigured(): boolean {
  const url = import.meta.env.VITE_API_BASE_URL
  return !!url && !url.includes('placeholder')
}

// ── Get current week's plan ──────────────────────────────────────────

export function useStudyPlan(userId: string | undefined) {
  return useQuery({
    queryKey: ['study-plan', userId],
    queryFn: async () => {
      if (!userId) return null
      if (!isApiConfigured()) return null
      return await plannerApi.get()
    },
    enabled: !!userId,
  })
}

// ── Generate and save plan ───────────────────────────────────────────

export function useGeneratePlan() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (profile: Profile) => {
      if (!isApiConfigured()) {
        // Fallback: generate locally
        const { generateWeeklyPlan } = await import('@/lib/planner')
        type UserProfile = import('@/lib/planner').UserProfile
        const userProfile: UserProfile = {
          target_exam: profile.target_exam || 'IELTS',
          target_score: profile.target_score || 6.5,
          current_band: profile.current_band || 3,
          skill_bands: profile.skill_bands || {},
          exam_date: profile.exam_date || new Date(Date.now() + 90 * 86400000).toISOString(),
          free_time: profile.free_time || { mon: 60, tue: 60, wed: 60, thu: 60, fri: 60, sat: 120, sun: 120 },
        }
        const plan = generateWeeklyPlan(userProfile)
        return {
          id: '',
          user_id: profile.id,
          week_start: new Date().toISOString().split('T')[0],
          daily_tasks: plan,
        } as StudyPlan
      }

      return await plannerApi.generate()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['study-plan'] })
    },
  })
}
