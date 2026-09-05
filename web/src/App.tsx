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
  const { session, loading } = useAuthStore()
  const location = useLocation()

  if (loading) return <div className="flex items-center justify-center h-screen text-gray-400">Loading…</div>

  // Check for either a Supabase session or a local session
  const hasLocalSession = !!getSession()
  if (!session && !hasLocalSession) {
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

    // If Supabase is not configured, use demo mode
    if (!isSupabaseConfigured()) {
      setLoading(false)
      refreshProfile()
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

  // Check if any auth exists (local or Supabase)
  const hasAuth = isSupabaseConfigured() || getSession()

  return (
    <Routes>
      <Route path="/" element={hasAuth ? <Landing /> : <Navigate to="/app" replace />} />
      <Route path="/auth" element={hasAuth ? <Auth /> : <Navigate to="/app" replace />} />
      <Route path="/onboarding" element={hasAuth ? <Onboarding /> : <Navigate to="/app" replace />} />
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
