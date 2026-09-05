import { useState, useEffect, useRef } from 'react'
import { useAuthStore } from '@/stores/auth.store'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Loader2, Sparkles, Timer, ChevronDown, CheckCircle2, AlertTriangle } from 'lucide-react'
import { loadExamWritingTests, type WritingTest, type WritingSubTask } from '@/lib/seed-data'
import { writingApi } from '@/api/writing'

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

// ── Local fallback feedback (when API is unavailable) ───────────────

function generateLocalFeedback(prompt: string, essay: string, minWords: number): AIFeedback {
  const words = essay.split(/\s+/).filter(Boolean)
  const wordCount = words.length
  const sentences = essay.split(/[.!?]+/).filter((s) => s.trim().length > 0)
  const sentenceCount = sentences.length
  const avgSentenceLength = sentenceCount > 0 ? wordCount / sentenceCount : 0

  // Simple grammar checks
  const lowercaseEssay = essay.toLowerCase()
  const hasCommaSplice = /,\s+(and|but|so|because|although)\b/.test(essay) && sentenceCount < wordCount / 15
  const startsWithAnd = /^\s*(and|but|so|because)\b/i.test(essay)
  const hasRunOn = avgSentenceLength > 30

  // Vocabulary diversity
  const uniqueWords = new Set(words.map((w) => w.toLowerCase().replace(/[^a-z']/g, '')))
  const diversity = wordCount > 0 ? uniqueWords.size / wordCount : 0

  // Linking words check
  const linkers = ['however', 'therefore', 'moreover', 'furthermore', 'in addition', 'consequently', 'nevertheless', 'on the other hand', 'for instance', 'for example', 'such as', 'in contrast', 'whereas', 'while', 'although', 'despite']
  const linkerCount = linkers.filter((l) => lowercaseEssay.includes(l)).length

  // Scoring (rough estimates)
  const meetsMin = wordCount >= minWords
  const taskScore = meetsMin ? 6 : 4
  const coherenceScore = linkerCount >= 3 ? 7 : linkerCount >= 1 ? 5 : 4
  const lexicalScore = diversity > 0.6 ? 7 : diversity > 0.45 ? 6 : 5
  const grammarScore = !hasRunOn && !startsWithAnd ? 6 : 4

  const bandEstimate = Math.round(((taskScore + coherenceScore + lexicalScore + grammarScore) / 4) * 10) / 10

  const corrections: { original: string; corrected: string; explanation: string }[] = []
  if (startsWithAnd) {
    corrections.push({
      original: essay.match(/^\s*(And|But|So|Because)\b[^.]*\./)?.[0] || 'Starting sentence',
      corrected: 'Consider rewriting without starting with a conjunction',
      explanation: 'In formal writing, avoid starting sentences with "and", "but", "so", or "because". Use a more formal transition instead.',
    })
  }
  if (hasRunOn) {
    corrections.push({
      original: `Long sentence (${Math.round(avgSentenceLength)} words avg)`,
      corrected: 'Break into shorter sentences',
      explanation: 'Your average sentence length is quite long. Try to keep sentences between 15-25 words for clarity.',
    })
  }

  const suggestions: string[] = []
  if (linkerCount < 3) {
    suggestions.push('Use more linking words (however, therefore, moreover, in addition) to connect your ideas.')
  }
  if (diversity < 0.5) {
    suggestions.push('Try to use a wider range of vocabulary — avoid repeating the same words.')
  }
  if (!meetsMin) {
    suggestions.push(`Your essay is ${wordCount} words — you need at least ${minWords}. Develop your ideas further.`)
  }

  return {
    band_estimate: bandEstimate,
    task_achievement: {
      score: taskScore,
      feedback: meetsMin
        ? `Your essay meets the minimum word count (${wordCount}/${minWords} words). ${sentenceCount > 3 ? 'You have a good number of developed points.' : 'Try to develop your points more fully with examples.'}`
        : `Your essay is below the minimum word count (${wordCount}/${minWords} words). You need to write more to fully address the task.`,
    },
    coherence: {
      score: coherenceScore,
      feedback: `You used ${linkerCount} linking word(s). ${linkerCount >= 3 ? 'Good use of cohesive devices.' : 'Add more transitions to guide the reader through your arguments.'} ${sentenceCount > 0 ? `Your essay has ${sentenceCount} sentence(s) with an average of ${Math.round(avgSentenceLength)} words.` : ''}`,
    },
    lexical_resource: {
      score: lexicalScore,
      feedback: `Vocabulary diversity: ${Math.round(diversity * 100)}%. ${diversity > 0.6 ? 'Excellent range of vocabulary.' : diversity > 0.45 ? 'Good vocabulary, but could be more varied.' : 'Try to use synonyms and avoid repetition.'}`,
      suggestions: suggestions.length > 0 ? suggestions : undefined,
    },
    grammar_range: {
      score: grammarScore,
      corrections: corrections.length > 0 ? corrections : [{
        original: 'No major issues detected',
        corrected: 'Continue practicing complex structures',
        explanation: 'No obvious grammar errors were found by the local checker. For detailed grammar analysis, use the AI Feedback button when the API server is running.',
      }],
    },
    overall_tip: suggestions.length > 0
      ? suggestions[0]
      : 'Good work! Focus on developing your arguments with specific examples and varied sentence structures.',
  }
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
  const [feedbackSource, setFeedbackSource] = useState<'ai' | 'local' | null>(null)
  const autoSaveRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Load saved drafts from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('writing-drafts')
      if (saved) setEssays(JSON.parse(saved))
    } catch { /* ignore */ }
  }, [])

  // Auto-save drafts to localStorage
  const saveDraft = (taskId: string, text: string) => {
    setEssays((prev) => {
      const updated = { ...prev, [taskId]: text }
      if (autoSaveRef.current) clearTimeout(autoSaveRef.current)
      autoSaveRef.current = setTimeout(() => {
        try {
          localStorage.setItem('writing-drafts', JSON.stringify(updated))
        } catch { /* ignore */ }
      }, 1000)
      return updated
    })
  }

  useEffect(() => {
    loadExamWritingTests(user?.target_exam || undefined)
      .then((data) => {
        setTests(data)
        setDataLoading(false)
        if (data.length > 0) {
          setSecondsLeft(data[0].task1.time_minutes * 60)
        }
      })
      .catch(() => setDataLoading(false))
  }, [user?.target_exam])

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
  const wordProgress = Math.min(100, (wordCount / minWords) * 100)

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
    setFeedbackSource(null)
    setFeedback((f) => ({ ...f, [task.id]: null as any }))

    try {
      const submission = await writingApi.submit({
        exam_type: user?.target_exam || 'IELTS',
        task_prompt: task.prompt,
        user_essay: essay,
      })

      const fb = submission.ai_feedback as AIFeedback
      if (fb) {
        setFeedback((f) => ({ ...f, [task.id]: fb }))
        setFeedbackSource('ai')
      } else {
        // API returned no feedback — use local
        const localFb = generateLocalFeedback(task.prompt, essay, minWords)
        setFeedback((f) => ({ ...f, [task.id]: localFb }))
        setFeedbackSource('local')
      }
    } catch (err: any) {
      // API failed — fall back to local analysis
      const localFb = generateLocalFeedback(task.prompt, essay, minWords)
      setFeedback((f) => ({ ...f, [task.id]: localFb }))
      setFeedbackSource('local')
      setError(
        err?.message?.includes('Network error')
          ? 'API server unavailable — showing local analysis instead.'
          : err?.message || 'API server unavailable — showing local analysis instead.'
      )
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
          {timerActive ? fmtTime(secondsLeft) : '--:--'}
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
              onChange={(e) => saveDraft(task.id, e.target.value)}
              placeholder={`Write at least ${minWords} words…`}
              className="mt-1"
              rows={12}
            />
            {/* Word count progress bar */}
            <div className="mt-2 space-y-1">
              <div className="flex items-center justify-between">
                <p className={`text-xs flex items-center gap-1 ${meetsMin ? 'text-success' : 'text-warning'}`}>
                  {meetsMin && <CheckCircle2 className="h-3 w-3" />}
                  {wordCount} / {minWords} words minimum
                </p>
                <p className="text-xs text-gray-400">Suggested time: {task.time_minutes} min</p>
              </div>
              <div className="h-1.5 rounded-full bg-surface-dark overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${meetsMin ? 'bg-success' : 'bg-warning'}`}
                  style={{ width: `${wordProgress}%` }}
                />
              </div>
            </div>
          </div>

          {/* Start timer */}
          {!timerActive && (
            <Button variant="outline" className="w-full" onClick={startTimer}>
              <Timer className="h-4 w-4 mr-2" /> Start {task.time_minutes}-minute Timer
            </Button>
          )}

          {/* Submit for AI feedback */}
          <div className="space-y-2">
            <Button onClick={getFeedback} disabled={loading || !essay.trim()} className="w-full">
              {loading ? (
                <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Analyzing…</>
              ) : (
                <><Sparkles className="h-4 w-4 mr-2" /> Get AI Feedback</>
              )}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                if (!essay.trim()) return
                const localFb = generateLocalFeedback(task.prompt, essay, minWords)
                setFeedback((f) => ({ ...f, [task.id]: localFb }))
                setFeedbackSource('local')
                setError(null)
              }}
              disabled={!essay.trim() || loading}
              className="w-full"
            >
              <AlertTriangle className="h-4 w-4 mr-2" /> Quick Local Analysis (no server needed)
            </Button>
          </div>

          {error && (
            <div className="flex items-start gap-2 rounded-lg border border-warning/30 bg-warning/10 p-3">
              <AlertTriangle className="h-4 w-4 text-warning flex-shrink-0 mt-0.5" />
              <p className="text-sm text-warning">{error}</p>
            </div>
          )}

          {feedbackSource === 'local' && !error && (
            <div className="flex items-start gap-2 rounded-lg border border-info/30 bg-info/10 p-3">
              <AlertTriangle className="h-4 w-4 text-info flex-shrink-0 mt-0.5" />
              <p className="text-sm text-info">Showing local analysis. For full AI-powered feedback, ensure the API server is running.</p>
            </div>
          )}
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

      {currentFeedback && (
        <div className="space-y-4">
          {currentFeedback.band_estimate && (
            <Card>
              <CardContent className="py-4 text-center">
                <p className="text-sm text-gray-400">Estimated Band Score</p>
                <p className="text-4xl font-bold text-accent">{currentFeedback.band_estimate}</p>
                {feedbackSource === 'local' && (
                  <p className="text-xs text-gray-500 mt-1">(Local estimate — connect API for AI scoring)</p>
                )}
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
