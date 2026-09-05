import { useAuthStore } from '@/stores/auth.store'
import { StreakBanner } from '@/components/dashboard/StreakBanner'
import { GoalRing } from '@/components/dashboard/GoalRing'
import { DailyPlan } from '@/components/dashboard/DailyPlan'
import { WordOfDay } from '@/components/dashboard/WordOfDay'
import { useProgressStats, useDailyActivity } from '@/hooks/useProgress'
import { useStudyPlan } from '@/hooks/useStudyPlan'
import { daysUntil, formatDate } from '@/lib/utils'
import { getLevelProgress } from '@/lib/srs'
import { format } from 'date-fns'
import { Brain, Target, Zap, Calendar } from 'lucide-react'

export function Dashboard() {
  const { user } = useAuthStore()
  const userId = user?.id
  const { data: stats } = useProgressStats(userId)
  const { data: activity } = useDailyActivity(userId, 1)
  const { data: plan } = useStudyPlan(userId)

  if (!user) return <p className="text-gray-400">Loading…</p>

  const todayKey = format(new Date(), 'yyyy-MM-dd')
  const todayMinutes = activity?.[todayKey] || 0
  const todayTarget = user.free_time?.[format(new Date(), 'EEE').toLowerCase().slice(0, 3)] || 60
  const daysLeft = user.exam_date ? daysUntil(user.exam_date) : null

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-bold font-heading">
            {greeting}, {user.name}! {hour < 12 ? '🌅' : hour < 18 ? '☀️' : '🌙'}
          </h1>
          <p className="text-sm text-gray-400">{formatDate(new Date())}</p>
        </div>
        {daysLeft !== null && (
          <div className="rounded-xl px-4 py-2 bg-accent/10 text-accent font-bold text-sm">
            {daysLeft < 0 ? '⚠️ Exam passed' : `📅 ${daysLeft} days to ${user.target_exam} ${user.target_score || ''}`}
          </div>
        )}
      </div>

      {/* Streak + XP */}
      <StreakBanner userId={user.id} streak={user.streak_days || 0} />

      {/* Level Progress */}
      {(() => {
        const lp = getLevelProgress(user.total_xp || 0)
        return (
          <div className="rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{lp.current.emoji}</span>
                <div>
                  <p className="text-sm font-bold">{lp.current.name}</p>
                  <p className="text-xs text-gray-400">{user.total_xp || 0} XP</p>
                </div>
              </div>
              {lp.next && (
                <div className="text-right">
                  <p className="text-xs text-gray-400">Next: {lp.next.emoji} {lp.next.name}</p>
                  <p className="text-xs text-gray-500">{lp.xpForNext - lp.xpIntoLevel} XP to go</p>
                </div>
              )}
            </div>
            <div className="h-2 rounded-full bg-black/20 overflow-hidden">
              <div
                className="h-full rounded-full bg-accent transition-all duration-500"
                style={{ width: `${lp.progress}%` }}
              />
            </div>
          </div>
        )
      })()}

      {/* Goal Ring + Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="flex justify-center rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-6">
          <GoalRing minutes={todayMinutes} target={todayTarget} />
        </div>
        <div className="grid grid-cols-1 gap-2">
          <StatCard icon={Brain} label="Words Learned" value={stats?.words_learned?.toString() || '0'} />
          <StatCard icon={Target} label="Current Band" value={user.current_band?.toString() || '—'} />
        </div>
        <div className="grid grid-cols-1 gap-2">
          <StatCard icon={Zap} label="XP This Week" value={(stats?.total_xp || 0).toString()} />
          <StatCard icon={Calendar} label="Days to Exam" value={daysLeft?.toString() || '—'} />
        </div>
      </div>

      {/* Daily Plan + Word of Day */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <h2 className="text-lg font-bold font-heading mb-3">📋 Today's Plan</h2>
          <DailyPlan userId={user.id} />
        </div>
        <div>
          <h2 className="text-lg font-bold font-heading mb-3">📖 Word of the Day</h2>
          <WordOfDay />
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon: Icon, label, value }: { icon: any; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-3">
      <Icon className="h-5 w-5 text-accent" />
      <div>
        <p className="text-lg font-bold">{value}</p>
        <p className="text-xs text-gray-400">{label}</p>
      </div>
    </div>
  )
}
