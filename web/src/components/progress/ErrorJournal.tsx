import { useErrorJournal } from '@/hooks/useProgress'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { format } from 'date-fns'

export function ErrorJournal({ userId }: { userId: string }) {
  const { data: errors, isLoading } = useErrorJournal(userId)

  if (isLoading) {
    return <p className="text-gray-400 text-sm">Loading errors…</p>
  }

  if (!errors || errors.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <p className="text-gray-400 text-sm">
            No errors logged yet. Complete exercises to build your error journal.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-2">
      {errors.map((err) => (
        <Card key={err.id}>
          <CardContent className="py-3">
            <div className="flex items-start justify-between gap-2 mb-1">
              <span className="text-xs font-medium text-error">
                {err.error_category || err.skill || 'Unknown'}
              </span>
              <span className="text-xs text-gray-400">
                {format(new Date(err.created_at), 'MMM d, yyyy')}
              </span>
            </div>
            <p className="text-sm mb-1">{err.question_snapshot}</p>
            <div className="flex gap-4 text-xs">
              <span className="text-error">You: {err.user_answer}</span>
              <span className="text-success">Correct: {err.correct_answer}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
