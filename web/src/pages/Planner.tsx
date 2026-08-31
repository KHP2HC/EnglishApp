import { useAuthStore } from '@/stores/auth.store'
import { useStudyPlan, useGeneratePlan } from '@/hooks/useStudyPlan'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatMinutes } from '@/lib/utils'
import { format } from 'date-fns'
import { Brain, Headphones, BookOpen, PenLine, Mic, FlaskConical, Calendar } from 'lucide-react'

const ICONS: Record<string, any> = {
  vocabulary: Brain,
  grammar: BookOpen,
  listening: Headphones,
  reading: BookOpen,
  writing: PenLine,
  speaking: Mic,
  mock: FlaskConical,
}

const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

export function Planner() {
  const { user } = useAuthStore()
  const { data: plan, isLoading } = useStudyPlan(user?.id)
  const generate = useGeneratePlan()

  if (!user) return <p>Loading…</p>

  const handleGenerate = () => generate.mutate(user)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold font-heading">🗓️ Study Planner</h1>
        <Button onClick={handleGenerate} disabled={generate.isPending}>
          {generate.isPending ? 'Generating…' : plan ? 'Regenerate Plan' : 'Generate Plan'}
        </Button>
      </div>

      {isLoading && <p className="text-gray-400">Loading plan…</p>}

      {plan?.daily_tasks && (
        <div className="space-y-3">
          {DAYS.map((day) => {
            const tasks = plan.daily_tasks[day] || []
            if (tasks.length === 0) return null
            return (
              <Card key={day}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Calendar className="h-4 w-4 text-accent" />
                    {day.charAt(0).toUpperCase() + day.slice(1)}
                    <span className="text-sm text-gray-400 font-normal">
                      · {formatMinutes(tasks.reduce((s, t) => s + t.minutes, 0))}
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {tasks.map((t, i) => {
                      const Icon = ICONS[t.type] || BookOpen
                      return (
                        <div key={i} className="flex items-center gap-2 rounded-lg border border-border p-2">
                          <Icon className="h-4 w-4 text-accent shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{t.label}</p>
                            <p className="text-xs text-gray-400">{formatMinutes(t.minutes)}</p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {!plan && !isLoading && (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-gray-400 text-sm mb-4">
              No study plan yet. Generate a personalized weekly plan based on your exam date and free time.
            </p>
            <Button onClick={handleGenerate} disabled={generate.isPending}>
              {generate.isPending ? 'Generating…' : 'Generate Study Plan'}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
