import { Flame, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth.store'
import { useOnlineStatus } from '@/hooks/useNotifications'
import { getLevel } from '@/lib/srs'

export function TopBar() {
  const { user, signOut } = useAuthStore()
  const online = useOnlineStatus()
  const navigate = useNavigate()
  const level = user ? getLevel(user.total_xp || 0) : null

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Sign out error:', error)
    } finally {
      navigate('/auth', { replace: true })
    }
  }

  return (
    <header className="flex items-center justify-between px-4 h-16 border-b border-border bg-surface-dark md:hidden">
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-white font-bold text-sm">
          E
        </div>
        <span className="font-heading font-bold text-white">EnglishCoach</span>
      </div>
      <div className="flex items-center gap-3">
        {!online && (
          <span className="text-xs text-warning">Offline</span>
        )}
        {level && (
          <span className="text-xs text-gray-400 hidden sm:inline">{level.emoji} {level.name}</span>
        )}
        {user && (
          <div className="flex items-center gap-1 text-sm text-white">
            <Flame className="h-4 w-4 text-xp" />
            <span className="font-bold">{user.streak_days || 0}</span>
          </div>
        )}
        <button
          onClick={handleSignOut}
          className="text-gray-500 hover:text-error transition-colors"
          title="Sign out"
        >
          <LogOut className="h-4 w-4" />
        </button>
        <span className="text-2xl">{user?.avatar_emoji || '🧑'}</span>
      </div>
    </header>
  )
}
