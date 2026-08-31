import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { supabase, type Profile } from '@/lib/supabase'
import { generateWeeklyPlan, type UserProfile } from '@/lib/planner'

// ── Get current week's plan ──────────────────────────────────────────

export function useStudyPlan(userId: string | undefined) {
  return useQuery({
    queryKey: ['study-plan', userId],
    queryFn: async () => {
      if (!userId) return null
      const today = new Date()
      const weekStart = new Date(today)
      weekStart.setDate(today.getDate() - today.getDay() + 1)

      const { data, error } = await supabase
        .from('study_plans')
        .select('*')
        .eq('user_id', userId)
        .gte('week_start', weekStart.toISOString().split('T')[0])
        .order('created_at', { ascending: false })
        .limit(1)
        .maybeSingle()

      if (error) throw error
      return data
    },
    enabled: !!userId,
  })
}

// ── Generate and save plan ───────────────────────────────────────────

export function useGeneratePlan() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (profile: Profile) => {
      const userProfile: UserProfile = {
        target_exam: profile.target_exam || 'IELTS',
        target_score: profile.target_score || 6.5,
        current_band: profile.current_band || 3,
        skill_bands: profile.skill_bands || {},
        exam_date: profile.exam_date || new Date(Date.now() + 90 * 86400000).toISOString(),
        free_time: profile.free_time || { mon: 60, tue: 60, wed: 60, thu: 60, fri: 60, sat: 120, sun: 120 },
      }

      const plan = generateWeeklyPlan(userProfile)
      const weekStart = new Date()
      weekStart.setDate(weekStart.getDate() - weekStart.getDay() + 1)

      const { data, error } = await supabase
        .from('study_plans')
        .upsert({
          user_id: profile.id,
          week_start: weekStart.toISOString().split('T')[0],
          daily_tasks: plan,
        })
        .select()
        .single()

      if (error) throw error
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['study-plan'] })
    },
  })
}
