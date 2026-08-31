import { useNavigate } from 'react-router-dom'
import { Brain, Headphones, BookOpen, PenLine, Mic, FlaskConical } from 'lucide-react'
import { useStudyPlan } from '@/hooks/useStudyPlan'
import { formatMinutes } from '@/lib/utils'
import type { DailyTask } from '@/lib/planner'
import { format } from 'date-fns'

const ICONS: Record<string, any> = {
  vocabulary: Brain,
  grammar: BookOpen,
  listening: Headphones,
  reading: BookOpen,
  writing: PenLine,
  speaking: Mic,
  mock: FlaskConical,
}

const ROUTES: Record<string, string> = {
  vocabulary: '/app/vocabulary',
  grammar: '/app/grammar',
  listening: '/app/listening',
  reading: '/app/reading',
  writing: '/app/writing',
  speaking: '/app/speaking',
  mock: '/app/mock-test',
}

export function DailyPlan({ userId }: { userId: string }) {
  const { data: plan } = useStudyPlan(userId)
  const navigate = useNavigate()

  const today = format(new Date(), 'EEE').toLowerCase().slice(0, 3)
  const tasks: DailyTask[] = plan?.daily_tasks?.[today] || []

  if (tasks.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-6 text-center">
        <p className="text-gray-400 text-sm">No plan for today yet.</p>
        <button
          onClick={() => navigate('/app/planner')}
          className="text-accent text-sm font-medium mt-2 hover:underline"
        >
          Generate a study plan →
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {tasks.map((task, i) => {
        const Icon = ICONS[task.type] || BookOpen
        const route = ROUTES[task.type] || '/app'
        return (
          <button
            key={i}
            onClick={() => navigate(route)}
            className="w-full flex items-center gap-3 rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-3 hover:border-accent transition-colors text-left"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10">
              <Icon className="h-5 w-5 text-accent" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{task.label}</p>
              <p className="text-xs text-gray-400">{formatMinutes(task.minutes)}</p>
            </div>
            <span className="text-accent text-sm">→</span>
          </button>
        )
      })}
    </div>
  )
}
