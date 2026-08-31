import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { supabase, type Profile } from '@/lib/supabase'

function isSupabaseConfigured(): boolean {
  const url = import.meta.env.VITE_SUPABASE_URL
  return !!url && !url.includes('placeholder')
}

// Demo user used when Supabase is not configured
const DEMO_USER: Profile = {
  id: 'demo-user',
  name: 'Learner',
  avatar_emoji: '🧑',
  target_exam: 'IELTS',
  target_score: 6.5,
  current_band: 4.5,
  skill_bands: {},
  exam_date: new Date(Date.now() + 90 * 86400000).toISOString().split('T')[0],
  free_time: { mon: 60, tue: 60, wed: 60, thu: 60, fri: 60, sat: 120, sun: 120 },
  session_time: 'MORNING',
  streak_days: 0,
  total_xp: 0,
  last_active: null,
  onboarded: true,
  created_at: new Date().toISOString(),
}

interface AuthState {
  user: Profile | null
  session: any | null
  loading: boolean
  setUser: (user: Profile | null) => void
  setSession: (session: any | null) => void
  setLoading: (loading: boolean) => void
  signOut: () => Promise<void>
  refreshProfile: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      session: null,
      loading: true,
      setUser: (user) => set({ user }),
      setSession: (session) => set({ session }),
      setLoading: (loading) => set({ loading }),
      signOut: async () => {
        if (isSupabaseConfigured()) {
          await supabase.auth.signOut()
        }
        set({ user: null, session: null })
      },
      refreshProfile: async () => {
        if (!isSupabaseConfigured()) {
          set({ user: DEMO_USER, loading: false })
          return
        }
        const session = get().session
        if (!session?.user?.id) return
        const { data } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', session.user.id)
          .single()
        if (data) set({ user: data as Profile })
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ user: state.user, session: state.session }),
    }
  )
)
