import { Flame } from 'lucide-react'
import { useProgressStats } from '@/hooks/useProgress'
import { useDailyActivity } from '@/hooks/useProgress'
import { format, subDays } from 'date-fns'
import { cn } from '@/lib/utils'

export function StreakBanner({ userId, streak }: { userId: string; streak: number }) {
  const { data: activity } = useDailyActivity(userId, 14)

  const days = Array.from({ length: 14 }, (_, i) => {
    const d = subDays(new Date(), 13 - i)
    const iso = format(d, 'yyyy-MM-dd')
    return { date: d, minutes: activity?.[iso] || 0 }
  })

  return (
    <div className="flex items-center gap-4 rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-4">
      <div className="flex items-center gap-2">
        <Flame className="h-8 w-8 text-xp" />
        <div>
          <p className="text-2xl font-bold font-heading">{streak}</p>
          <p className="text-xs text-gray-400">day streak</p>
        </div>
      </div>
      <div className="flex-1 flex items-end gap-1 h-12">
        {days.map((d, i) => (
          <div
            key={i}
            title={`${format(d.date, 'EEE MMM d')}: ${d.minutes}m`}
            className={cn(
              'flex-1 rounded-sm transition-colors',
              d.minutes === 0 && 'bg-gray-200 dark:bg-gray-700',
              d.minutes > 0 && d.minutes < 15 && 'bg-green-200 dark:bg-green-900',
              d.minutes >= 15 && d.minutes < 30 && 'bg-green-400 dark:bg-green-700',
              d.minutes >= 30 && d.minutes < 60 && 'bg-green-500 dark:bg-green-600',
              d.minutes >= 60 && 'bg-green-600 dark:bg-green-500'
            )}
            style={{ height: `${Math.min(100, (d.minutes / 60) * 100)}%` }}
          />
        ))}
      </div>
    </div>
  )
}
