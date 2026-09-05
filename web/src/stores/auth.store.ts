import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { supabase, type Profile } from '@/lib/supabase'
import { profileApi } from '@/api/profile'
import { getSession, getCurrentAccount, signOutLocal } from '@/lib/localAuth'
import { loadLocalProfile } from '@/lib/userStorage'

function isApiConfigured(): boolean {
  const url = import.meta.env.VITE_API_BASE_URL
  return !!url && !url.includes('placeholder')
}

function isSupabaseConfigured(): boolean {
  const url = import.meta.env.VITE_SUPABASE_URL
  return !!url && !url.includes('placeholder')
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
  onLocalAuth: (userId: string, name: string, email: string) => Promise<void>
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
        try {
          if (isSupabaseConfigured()) {
            try {
              await supabase.auth.signOut()
            } catch {
              // Supabase sign-out may fail if session already expired —
              // continue with local cleanup regardless.
            }
          }
          signOutLocal()
        } catch (error) {
          console.error('Error during signOut:', error)
        } finally {
          // Always clear state synchronously so the UI can redirect.
          set({ user: null, session: null, loading: false })
        }
      },
      onLocalAuth: async (userId: string, name: string, email: string) => {
        // Load or create local profile
        const profile = loadLocalProfile(userId, name, email)
        set({ user: profile, session: { user: { id: userId, email } } })
      },
      refreshProfile: async () => {
        // Check for local session first
        const localSession = getSession()
        const localAccount = getCurrentAccount()

        if (localSession && localAccount) {
          const profile = loadLocalProfile(localAccount.id, localAccount.name, localAccount.email)
          set({ user: profile, loading: false })
          return
        }

        // If Supabase is not configured, don't set a demo user —
        // the caller should redirect to /auth instead.
        if (!isSupabaseConfigured()) {
          set({ loading: false })
          return
        }

        const session = get().session
        if (!session?.user?.id) return

        // Use API client for profile data
        if (isApiConfigured()) {
          try {
            const profile = await profileApi.get()
            if (profile) {
              set({ user: profile as Profile })
              return
            }
          } catch {
            // API unavailable — fall through to basic session data
          }
        }

        // Fallback: use session user data
        set({
          user: {
            id: session.user.id,
            email: session.user.email || '',
            name: session.user.user_metadata?.name || '',
            avatar_emoji: session.user.user_metadata?.avatar_emoji || '',
            target_exam: session.user.user_metadata?.target_exam || null,
            target_score: session.user.user_metadata?.target_score || null,
            current_band: session.user.user_metadata?.current_band || null,
            skill_bands: {},
            exam_date: null,
            free_time: {},
            session_time: 'EVENING',
            streak_days: 0,
            total_xp: 0,
            last_active: null,
            onboarded: false,
            created_at: new Date().toISOString(),
          } as unknown as Profile,
        })
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ user: state.user, session: state.session }),
    }
  )
)
