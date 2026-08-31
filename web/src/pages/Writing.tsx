import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/stores/auth.store'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Loader2, Sparkles, Timer, ChevronDown } from 'lucide-react'
import { loadWritingTests, type WritingTest, type WritingSubTask } from '@/lib/seed-data'

interface AIFeedback {
  band_estimate?: number
  task_achievement?: { score: number; feedback: string }
  coherence?: { score: number; feedback: string }
  lexical_resource?: { score: number; feedback: string; suggestions?: string[] }
  grammar_range?: { score: number; corrections: { original: string; corrected: string; explanation: string }[] }
  rewritten_paragraph?: string
  overall_tip?: string
  raw_feedback?: string
}

export function Writing() {
  const { user } = useAuthStore()
  const [tests, setTests] = useState<WritingTest[]>([])
  const [testIdx, setTestIdx] = useState(0)
  const [activeTask, setActiveTask] = useState<'task1' | 'task2'>('task1')
  const [essays, setEssays] = useState<Record<string, string>>({})
  const [feedback, setFeedback] = useState<Record<string, AIFeedback>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dataLoading, setDataLoading] = useState(true)
  const [secondsLeft, setSecondsLeft] = useState(0)
  const [timerActive, setTimerActive] = useState(false)
  const [showTestList, setShowTestList] = useState(false)

  useEffect(() => {
    loadWritingTests()
      .then((data) => {
        setTests(data)
        setDataLoading(false)
        if (data.length > 0) {
          setSecondsLeft(data[0].task1.time_minutes * 60)
        }
      })
      .catch(() => setDataLoading(false))
  }, [])

  // Timer
  useEffect(() => {
    if (timerActive && secondsLeft > 0) {
      const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000)
      return () => clearTimeout(t)
    }
    if (timerActive && secondsLeft === 0) {
      setTimerActive(false)
    }
  }, [timerActive, secondsLeft])

  if (dataLoading) return <p className="text-gray-400">Loading writing tests…</p>
  if (tests.length === 0) return <p className="text-gray-400">No writing tests available.</p>

  const test = tests[testIdx]
  const task: WritingSubTask = activeTask === 'task1' ? test.task1 : test.task2
  const essay = essays[task.id] || ''
  const wordCount = essay.split(/\s+/).filter(Boolean).length
  const minWords = task.min_words || 150
  const meetsMin = wordCount >= minWords

  const fmtTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

  const switchTask = (t: 'task1' | 'task2') => {
    setActiveTask(t)
    const nextTask = t === 'task1' ? test.task1 : test.task2
    setSecondsLeft(nextTask.time_minutes * 60)
    setTimerActive(false)
  }

  const selectTest = (i: number) => {
    setTestIdx(i)
    setActiveTask('task1')
    setSecondsLeft(tests[i].task1.time_minutes * 60)
    setTimerActive(false)
    setShowTestList(false)
  }

  const startTimer = () => {
    setSecondsLeft(task.time_minutes * 60)
    setTimerActive(true)
  }

  const getFeedback = async () => {
    if (!essay.trim()) return
    setLoading(true)
    setError(null)
    setFeedback((f) => ({ ...f, [task.id]: null as any }))

    try {
      const { data, error: fnError } = await supabase.functions.invoke('ai-feedback', {
        body: {
          exam_type: user?.target_exam || 'IELTS',
          task_prompt: task.prompt,
          essay,
        },
      })

      if (fnError) throw fnError
      const fb = data as AIFeedback
      setFeedback((f) => ({ ...f, [task.id]: fb }))

      // Save submission
      if (user) {
        await supabase.from('writing_submissions').insert({
          user_id: user.id,
          task_prompt: task.prompt,
          user_essay: essay,
          ai_feedback: data,
          band_estimate: fb?.band_estimate || null,
        })
      }
    } catch (err: any) {
      setError(err.message || 'Failed to get feedback. Make sure the AI service is configured.')
    } finally {
      setLoading(false)
    }
  }

  const currentFeedback = feedback[task.id]

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold font-heading">✍️ Writing Practice</h1>
        <div className={`flex items-center gap-2 font-mono font-bold ${secondsLeft < 60 && timerActive ? 'text-error animate-pulse' : 'text-warning'}`}>
          <Timer className="h-5 w-5" />
          {fmtTime(secondsLeft)}
        </div>
      </div>

      {/* Test selector */}
      <div className="relative">
        <button
          onClick={() => setShowTestList((s) => !s)}
          className="w-full flex items-center justify-between px-4 py-2.5 rounded-lg bg-surface-dark text-sm font-medium hover:bg-surface transition-colors"
        >
          <span>{test.title}</span>
          <span className="flex items-center gap-2 text-gray-400">
            <span className="text-xs">Test {testIdx + 1} of {tests.length}</span>
            <ChevronDown className="h-4 w-4" />
          </span>
        </button>
        {showTestList && (
          <div className="absolute z-20 mt-1 w-full max-h-64 overflow-y-auto rounded-lg border border-border bg-surface shadow-lg">
            {tests.map((t, i) => (
              <button
                key={t.id}
                onClick={() => selectTest(i)}
                className={`w-full text-left px-4 py-2 text-sm hover:bg-surface-dark transition-colors ${
                  i === testIdx ? 'bg-accent/20 text-accent font-medium' : 'text-gray-300'
                }`}
              >
                {t.title}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Task 1 / Task 2 toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => switchTask('task1')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTask === 'task1' ? 'bg-accent text-white' : 'bg-surface-dark text-gray-400 hover:text-white'
          }`}
        >
          Task 1 (20 min)
        </button>
        <button
          onClick={() => switchTask('task2')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTask === 'task2' ? 'bg-accent text-white' : 'bg-surface-dark text-gray-400 hover:text-white'
          }`}
        >
          Task 2 (40 min)
        </button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{task.title}</CardTitle>
          <p className="text-xs text-gray-400">{task.instructions}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Prompt */}
          <div className="rounded-lg bg-black/20 p-4">
            <Label>Task Prompt</Label>
            <p className="text-sm text-gray-200 mt-1">{task.prompt}</p>
            {task.data_description && (
              <p className="text-xs text-gray-400 mt-2 italic">📊 {task.data_description}</p>
            )}
          </div>

          {/* Essay input */}
          <div>
            <Label>Your Essay</Label>
            <Textarea
              value={essay}
              onChange={(e) => setEssays((prev) => ({ ...prev, [task.id]: e.target.value }))}
              placeholder={`Write at least ${minWords} words…`}
              className="mt-1"
              rows={12}
            />
            <div className="flex items-center justify-between mt-1">
              <p className={`text-xs ${meetsMin ? 'text-success' : 'text-warning'}`}>
                {wordCount} / {minWords} words minimum {meetsMin && '✓'}
              </p>
              <p className="text-xs text-gray-400">Suggested time: {task.time_minutes} min</p>
            </div>
          </div>

          {/* Start timer */}
          {!timerActive && (
            <Button variant="outline" className="w-full" onClick={startTimer}>
              <Timer className="h-4 w-4 mr-2" /> Start {task.time_minutes}-minute Timer
            </Button>
          )}

          {/* Submit for AI feedback */}
          <Button onClick={getFeedback} disabled={loading || !essay.trim()}>
            {loading ? (
              <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Analyzing…</>
            ) : (
              <><Sparkles className="h-4 w-4 mr-2" /> Get AI Feedback</>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Band descriptors */}
      {task.band_descriptors && (
        <Card>
          <CardHeader><CardTitle className="text-base">Assessment Criteria</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {task.band_descriptors.task_achievement && (
              <div className="text-sm">
                <span className="font-medium text-accent">Task Achievement:</span>
                <span className="text-gray-400"> {task.band_descriptors.task_achievement}</span>
              </div>
            )}
            {task.band_descriptors.coherence && (
              <div className="text-sm">
                <span className="font-medium text-accent">Coherence & Cohesion:</span>
                <span className="text-gray-400"> {task.band_descriptors.coherence}</span>
              </div>
            )}
            {task.band_descriptors.lexical_resource && (
              <div className="text-sm">
                <span className="font-medium text-accent">Lexical Resource:</span>
                <span className="text-gray-400"> {task.band_descriptors.lexical_resource}</span>
              </div>
            )}
            {task.band_descriptors.grammar && (
              <div className="text-sm">
                <span className="font-medium text-accent">Grammar Range & Accuracy:</span>
                <span className="text-gray-400"> {task.band_descriptors.grammar}</span>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {error && (
        <Card>
          <CardContent className="py-4">
            <p className="text-sm text-error">{error}</p>
          </CardContent>
        </Card>
      )}

      {currentFeedback && (
        <div className="space-y-4">
          {currentFeedback.band_estimate && (
            <Card>
              <CardContent className="py-4 text-center">
                <p className="text-sm text-gray-400">Estimated Band Score</p>
                <p className="text-4xl font-bold text-accent">{currentFeedback.band_estimate}</p>
              </CardContent>
            </Card>
          )}

          {currentFeedback.task_achievement && (
            <FeedbackCard title="Task Achievement" score={currentFeedback.task_achievement.score} feedback={currentFeedback.task_achievement.feedback} />
          )}
          {currentFeedback.coherence && (
            <FeedbackCard title="Coherence & Cohesion" score={currentFeedback.coherence.score} feedback={currentFeedback.coherence.feedback} />
          )}
          {currentFeedback.lexical_resource && (
            <FeedbackCard
              title="Lexical Resource"
              score={currentFeedback.lexical_resource.score}
              feedback={currentFeedback.lexical_resource.feedback}
              suggestions={currentFeedback.lexical_resource.suggestions}
            />
          )}
          {currentFeedback.grammar_range && (
            <Card>
              <CardHeader><CardTitle>Grammar Range & Accuracy</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm text-gray-300">Score: {currentFeedback.grammar_range.score}/9</p>
                {currentFeedback.grammar_range.corrections?.map((c, i) => (
                  <div key={i} className="rounded-lg border border-border p-3 text-sm">
                    <p><span className="text-error line-through">{c.original}</span> → <span className="text-success">{c.corrected}</span></p>
                    <p className="text-xs text-gray-400 mt-1">{c.explanation}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
          {currentFeedback.rewritten_paragraph && (
            <Card>
              <CardHeader><CardTitle>Rewritten Paragraph</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-gray-300 italic">{currentFeedback.rewritten_paragraph}</p>
              </CardContent>
            </Card>
          )}
          {currentFeedback.overall_tip && (
            <Card>
              <CardContent className="py-4">
                <p className="text-sm"><span className="font-medium text-accent">💡 Tip: </span>{currentFeedback.overall_tip}</p>
              </CardContent>
            </Card>
          )}
          {currentFeedback.raw_feedback && !currentFeedback.band_estimate && (
            <Card>
              <CardContent className="py-4">
                <pre className="text-sm whitespace-pre-wrap text-gray-300">{currentFeedback.raw_feedback}</pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

function FeedbackCard({ title, score, feedback, suggestions }: { title: string; score?: number; feedback: string; suggestions?: string[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          {title}
          {score !== undefined && <span className="text-accent text-lg">{score}/9</span>}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-sm text-gray-300">{feedback}</p>
        {suggestions && suggestions.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs font-medium text-gray-400">Suggestions:</p>
            {suggestions.map((s, i) => (
              <p key={i} className="text-xs text-gray-300">• {s}</p>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
