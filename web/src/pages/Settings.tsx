import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth.store'
import { useSettingsStore } from '@/stores/settings.store'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useNotifications } from '@/hooks/useNotifications'
import { getLevel } from '@/lib/srs'
import { profileApi } from '@/api/profile'

export function Settings() {
  const { user, signOut, refreshProfile } = useAuthStore()
  const { theme, setTheme, language, setLanguage } = useSettingsStore()
  const { permission, requestPermission } = useNotifications()
  const navigate = useNavigate()
  const [name, setName] = useState(user?.name || '')
  const [avatar, setAvatar] = useState(user?.avatar_emoji || '🧑')
  const [saved, setSaved] = useState(false)

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Sign out error:', error)
    } finally {
      navigate('/auth', { replace: true })
    }
  }

  if (!user) return <p>Loading…</p>

  const levelInfo = getLevel(user.total_xp || 0)

  const save = async () => {
    try {
      await profileApi.update({ name, avatar_emoji: avatar })
      await refreshProfile()
    } catch {
      // Non-fatal in demo mode
    }
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold font-heading">⚙️ Settings</h1>

      {/* Profile */}
      <Card>
        <CardHeader><CardTitle>Profile</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <span className="text-4xl">{avatar}</span>
            <div className="flex-1">
              <Label>Name</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </div>
          </div>
          <div>
            <Label>Avatar emoji</Label>
            <Input value={avatar} onChange={(e) => setAvatar(e.target.value)} maxLength={4} />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-2xl">{levelInfo.emoji}</span>
            <span>Level — {levelInfo.name}</span>
            <span className="text-gray-400">({user.total_xp || 0} XP)</span>
          </div>
          <Button onClick={save}>{saved ? '✅ Saved!' : 'Save Changes'}</Button>
        </CardContent>
      </Card>

      {/* Appearance */}
      <Card>
        <CardHeader><CardTitle>Appearance</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Theme</Label>
            <div className="flex gap-2 mt-2">
              {(['dark', 'light'] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTheme(t)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                    theme === t ? 'bg-accent text-white' : 'bg-surface-dark text-gray-400'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <div>
            <Label>Language / Ngôn ngữ</Label>
            <div className="flex gap-2 mt-2">
              {(['en', 'vi'] as const).map((l) => (
                <button
                  key={l}
                  onClick={() => setLanguage(l)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    language === l ? 'bg-accent text-white' : 'bg-surface-dark text-gray-400'
                  }`}
                >
                  {l === 'en' ? 'English' : 'Tiếng Việt'}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader><CardTitle>Notifications</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-gray-400">
            Get daily streak reminders and word-of-the-day notifications.
          </p>
          <p className="text-sm">
            Status: <span className={permission === 'granted' ? 'text-success' : 'text-warning'}>
              {permission === 'granted' ? '✅ Enabled' : 'Not enabled'}
            </span>
          </p>
          {permission !== 'granted' && (
            <Button variant="outline" onClick={requestPermission}>
              Enable Notifications
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Exam Info */}
      <Card>
        <CardHeader><CardTitle>Exam Target</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-gray-400">Exam:</span><span>{user.target_exam || 'Not set'}</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Target Score:</span><span>{user.target_score || '—'}</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Current Band:</span><span>{user.current_band || '—'}</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Exam Date:</span><span>{user.exam_date || '—'}</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Streak:</span><span>🔥 {user.streak_days || 0} days</span></div>
        </CardContent>
      </Card>

      {/* Sign out */}
      <Button variant="destructive" className="w-full" onClick={handleSignOut}>
        Sign Out
      </Button>
    </div>
  )
}
