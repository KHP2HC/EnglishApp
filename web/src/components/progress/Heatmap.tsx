import { format, subDays } from 'date-fns'
import { cn } from '@/lib/utils'

interface HeatmapProps {
  activity: Record<string, number>
  weeks?: number
}

export function Heatmap({ activity, weeks = 52 }: HeatmapProps) {
  const days = Array.from({ length: weeks * 7 }, (_, i) => {
    const d = subDays(new Date(), weeks * 7 - 1 - i)
    return { date: d, minutes: activity[format(d, 'yyyy-MM-dd')] || 0 }
  })

  // Group into weeks
  const weekGroups: typeof days[] = []
  for (let i = 0; i < days.length; i += 7) {
    weekGroups.push(days.slice(i, i + 7))
  }

  const getColor = (minutes: number) => {
    if (minutes === 0) return 'bg-gray-200 dark:bg-gray-800'
    if (minutes < 15) return 'bg-green-200 dark:bg-green-900'
    if (minutes < 30) return 'bg-green-400 dark:bg-green-700'
    if (minutes < 60) return 'bg-green-500 dark:bg-green-600'
    return 'bg-green-600 dark:bg-green-500'
  }

  return (
    <div className="overflow-x-auto">
      <div className="flex gap-1 min-w-max">
        {weekGroups.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-1">
            {week.map((day, di) => (
              <div
                key={di}
                title={`${format(day.date, 'MMM d, yyyy')}: ${day.minutes}m`}
                className={cn('w-3 h-3 rounded-sm transition-colors', getColor(day.minutes))}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 mt-2 text-xs text-gray-400">
        <span>Less</span>
        <div className="w-3 h-3 rounded-sm bg-gray-200 dark:bg-gray-800" />
        <div className="w-3 h-3 rounded-sm bg-green-200 dark:bg-green-900" />
        <div className="w-3 h-3 rounded-sm bg-green-400 dark:bg-green-700" />
        <div className="w-3 h-3 rounded-sm bg-green-500 dark:bg-green-600" />
        <div className="w-3 h-3 rounded-sm bg-green-600 dark:bg-green-500" />
        <span>More</span>
      </div>
    </div>
  )
}
