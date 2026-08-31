import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { format, subDays } from 'date-fns'

// ── Daily activity for heatmap ───────────────────────────────────────

export function useDailyActivity(userId: string | undefined, days = 365) {
  return useQuery({
    queryKey: ['progress', 'activity', userId, days],
    queryFn: async () => {
      if (!userId) return {}
      const startDate = subDays(new Date(), days)

      const { data, error } = await supabase
        .from('study_sessions')
        .select('started_at, ended_at')
        .eq('user_id', userId)
        .gte('started_at', startDate.toISOString())

      if (error) throw error

      const activity: Record<string, number> = {}
      for (let i = 0; i < days; i++) {
        const d = subDays(new Date(), i)
        activity[format(d, 'yyyy-MM-dd')] = 0
      }

      for (const s of data || []) {
        if (!s.started_at) continue
        const day = format(new Date(s.started_at), 'yyyy-MM-dd')
        let mins = 0
        if (s.ended_at) {
          mins = Math.round(
            (new Date(s.ended_at).getTime() - new Date(s.started_at).getTime()) / 60000
          )
        } else {
          mins = 25 // assume 25-min Pomodoro
        }
        activity[day] = (activity[day] || 0) + Math.max(0, mins)
      }

      return activity
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

      const [vocabRes, sessionsRes, errorsRes] = await Promise.all([
        supabase
          .from('vocab_progress')
          .select('times_seen, times_correct')
          .eq('user_id', userId),
        supabase
          .from('study_sessions')
          .select('*')
          .eq('user_id', userId)
          .order('started_at', { ascending: false })
          .limit(100),
        supabase
          .from('error_journal')
          .select('*')
          .eq('user_id', userId)
          .order('created_at', { ascending: false })
          .limit(200),
      ])

      const vocab = vocabRes.data || []
      const sessions = sessionsRes.data || []
      const errors = errorsRes.data || []

      const wordsLearned = vocab.filter((v) => v.times_seen > 0).length
      const wordsMastered = vocab.filter((v) => v.times_correct >= 3).length
      const totalXp = sessions.reduce((sum, s) => sum + (s.xp_earned || 0), 0)

      // Time per skill (last 30 days)
      const thirtyAgo = subDays(new Date(), 30)
      const recentSessions = sessions.filter(
        (s) => new Date(s.started_at) >= thirtyAgo
      )
      const timeBySkill: Record<string, number> = {}
      for (const s of recentSessions) {
        const mins = s.ended_at
          ? Math.round(
              (new Date(s.ended_at).getTime() - new Date(s.started_at).getTime()) / 60000
            )
          : 25
        timeBySkill[s.session_type] = (timeBySkill[s.session_type] || 0) + Math.max(0, mins)
      }

      // Accuracy per skill
      const skillAccuracy: Record<string, { correct: number; total: number }> = {}
      for (const s of recentSessions) {
        if (!skillAccuracy[s.session_type]) {
          skillAccuracy[s.session_type] = { correct: 0, total: 0 }
        }
        skillAccuracy[s.session_type].total += s.items_total || 0
        skillAccuracy[s.session_type].correct += s.items_correct || 0
      }

      return {
        wordsLearned,
        wordsMastered,
        totalXp,
        totalSessions: sessions.length,
        timeBySkill,
        skillAccuracy,
        errors,
        recentSessions,
      }
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
      const { data, error } = await supabase
        .from('error_journal')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(200)

      if (error) throw error
      return data || []
    },
    enabled: !!userId,
  })
}
