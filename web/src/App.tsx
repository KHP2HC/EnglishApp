import { useEffect } from 'react'
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/stores/auth.store'
import { getSession } from '@/lib/localAuth'
import { AppLayout } from '@/components/layout/AppLayout'
import { Landing } from '@/pages/Landing'
import { Auth } from '@/pages/Auth'
import { Onboarding } from '@/pages/Onboarding'
import { Placement } from '@/pages/Placement'
import { Dashboard } from '@/pages/Dashboard'
import { Vocabulary } from '@/pages/Vocabulary'
import { Grammar } from '@/pages/Grammar'
import { Listening } from '@/pages/Listening'
import { Reading } from '@/pages/Reading'
import { Writing } from '@/pages/Writing'
import { Speaking } from '@/pages/Speaking'
import { MockTest } from '@/pages/MockTest'
import { Progress } from '@/pages/Progress'
import { Planner } from '@/pages/Planner'
import { Settings } from '@/pages/Settings'

function isSupabaseConfigured(): boolean {
  const url = import.meta.env.VITE_SUPABASE_URL
  return !!url && !url.includes('placeholder')
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, session, loading } = useAuthStore()
  const location = useLocation()

  // Show loading screen while auth state is being determined.
  if (loading) {
    return <div className="flex items-center justify-center h-screen text-gray-400">Loading…</div>
  }

  // Check for either a Supabase session, a local session, or a populated
  // user profile.  Using the store's `user` (in addition to getSession())
  // makes the component reactive — when signOut clears the store, this
  // re-renders and redirects immediately without waiting for a page reload.
  const hasLocalSession = !!getSession()
  const isAuthenticated = !!session || hasLocalSession || !!user

  if (!isAuthenticated) {
    return <Navigate to="/auth" state={{ from: location }} replace />
  }

  return <>{children}</>
}

export default function App() {
  const { setSession, setUser, setLoading, refreshProfile } = useAuthStore()

  useEffect(() => {
    // Check for local session first (works without Supabase)
    const localSession = getSession()
    if (localSession) {
      refreshProfile().then(() => setLoading(false))
      return
    }

    // If Supabase is not configured, don't auto-login — let ProtectedRoute
    // redirect to /auth so the user can create an account or sign in.
    if (!isSupabaseConfigured()) {
      setLoading(false)
      return
    }

    setLoading(true)
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      if (session) {
        refreshProfile().then(() => setLoading(false))
      } else {
        setLoading(false)
      }
    })

    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      if (session) {
        refreshProfile()
      } else {
        setUser(null)
      }
    })

    return () => listener.subscription.unsubscribe()
  }, [])

  // Auth pages are always accessible
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/auth" element={<Auth />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="vocabulary" element={<Vocabulary />} />
        <Route path="grammar" element={<Grammar />} />
        <Route path="listening" element={<Listening />} />
        <Route path="reading" element={<Reading />} />
        <Route path="writing" element={<Writing />} />
        <Route path="speaking" element={<Speaking />} />
        <Route path="mock-test" element={<MockTest />} />
        <Route path="progress" element={<Progress />} />
        <Route path="planner" element={<Planner />} />
        <Route path="placement" element={<Placement />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/app" replace />} />
    </Routes>
  )
}
