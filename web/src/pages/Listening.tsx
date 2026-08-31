import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Volume2, Check, X, Timer, RotateCcw, ChevronDown } from 'lucide-react'
import { useSpeech } from '@/hooks/useSpeech'
import { loadListeningTests, type ListeningTest } from '@/lib/seed-data'
import { rawToListeningBand, bandLabel } from '@/lib/ielts-bands'

// ── Answer normalisation ─────────────────────────────────────────────

function normalise(s: string): string {
  return s.toLowerCase().trim().replace(/[.,!?;:'"]/g, '').replace(/\s+/g, ' ')
}

function checkAnswer(q: { answer: string | string[] }, userAnswer: string): boolean {
  if (!userAnswer) return false
  const answers = Array.isArray(q.answer) ? q.answer : [q.answer]
  const norm = normalise(userAnswer)
  return answers.some((a) => normalise(a) === norm)
}

// Composite key so answers persist across test switches: "testId::qId"
const aKey = (testId: string, qId: string) => `${testId}::${qId}`

export function Listening() {
  const { speak, speaking } = useSpeech()
  const [tests, setTests] = useState<ListeningTest[]>([])
  const [testIdx, setTestIdx] = useState(0)
  const [sectionIdx, setSectionIdx] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [checked, setChecked] = useState(false)
  const [loading, setLoading] = useState(true)
  const [secondsLeft, setSecondsLeft] = useState(0)
  const [timerActive, setTimerActive] = useState(false)
  const [audioPlayed, setAudioPlayed] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadListeningTests()
      .then((data) => {
        setTests(data)
        setLoading(false)
        if (data.length > 0) {
          setSecondsLeft(data[0].time_minutes * 60)
        }
      })
      .catch(() => setLoading(false))
  }, [])

  // Timer
  useEffect(() => {
    if (timerActive && secondsLeft > 0) {
      const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000)
      return () => clearTimeout(t)
    }
    if (timerActive && secondsLeft === 0) {
      setChecked(true)
      setTimerActive(false)
    }
  }, [timerActive, secondsLeft])

  if (loading) return <p className="text-gray-400">Loading listening tests…</p>
  if (tests.length === 0) return <p className="text-gray-400">No listening tests available.</p>

  const test = tests[testIdx]
  const sections = test.sections || []
  const section = sections[sectionIdx]

  if (!section) return <p className="text-gray-400">No sections in this test.</p>

  // ── Attempt tracking ────────────────────────────────────────────
  /** A test is "attempted" if any of its questions have been answered. */
  const isTestAttempted = (t: ListeningTest) =>
    t.sections.some((s) => s.questions.some((q) => answers[aKey(t.id, q.id)]))

  /** A section is "attempted" if any of its questions have been answered. */
  const isSectionAttempted = (s: typeof section) =>
    s.questions.some((q) => answers[aKey(test.id, q.id)])

  /** Count answered questions for a specific test. */
  const countAnswered = (t: ListeningTest) =>
    t.sections.flatMap((s) => s.questions).filter((q) => answers[aKey(t.id, q.id)]).length

  // Collect all questions across all sections for scoring
  const allQuestions = sections.flatMap((s) => s.questions)
  const totalQuestions = allQuestions.length
  const correctCount = allQuestions.filter((q) => checkAnswer(q, answers[aKey(test.id, q.id)] || '')).length
  const answeredCount = allQuestions.filter((q) => answers[aKey(test.id, q.id)]).length

  const startTimer = () => {
    setSecondsLeft(test.time_minutes * 60)
    setTimerActive(true)
  }

  const switchTest = (i: number) => {
    setTestIdx(i)
    setSectionIdx(0)
    setChecked(false)
    setTimerActive(false)
    setAudioPlayed(new Set())
    setSecondsLeft(tests[i].time_minutes * 60)
  }

  // Set answer using composite key (persists across test switches)
  const setAnswer = (qId: string, val: string) => {
    setAnswers((prev) => ({ ...prev, [aKey(test.id, qId)]: val }))
  }

  const playAudio = (sectionId: string, transcript: string) => {
    speak(transcript, 0.9)
    setAudioPlayed((prev) => new Set(prev).add(sectionId))
  }

  const fmtTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

  // Results view
  if (checked) {
    const band = rawToListeningBand(correctCount, totalQuestions)
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold font-heading text-center">🎧 Listening Test Results</h1>
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-sm text-gray-400">Estimated IELTS Band</p>
            <p className="text-6xl font-bold text-accent">{band.toFixed(1)}</p>
            <p className="text-sm text-gray-400 mt-1">{bandLabel(band)}</p>
            <p className="text-lg mt-4">
              Score: <span className="font-bold text-success">{correctCount}</span> / {totalQuestions}
            </p>
          </CardContent>
        </Card>

        {/* Answer Review */}
        <Card>
          <CardHeader><CardTitle>Answer Review</CardTitle></CardHeader>
          <CardContent className="space-y-3 max-h-[50vh] overflow-y-auto">
            {sections.map((sec, si) => (
              <div key={sec.id} className="space-y-2">
                <p className="text-sm font-medium text-gray-400">Section {si + 1}: {sec.title}</p>
                {sec.questions.map((q) => {
                  const userAns = answers[aKey(test.id, q.id)] || ''
                  const isRight = checkAnswer(q, userAns)
                  const correctAns = Array.isArray(q.answer) ? q.answer[0] : q.answer
                  return (
                    <div key={q.id} className={`rounded-lg border p-2 text-sm ${isRight ? 'border-success/30 bg-success/5' : 'border-error/30 bg-error/5'}`}>
                      <p className="font-medium">Q{q.number}. {q.text}</p>
                      <p className="text-xs mt-1">
                        {isRight ? (
                          <span className="text-success flex items-center gap-1"><Check className="h-3 w-3" /> Correct</span>
                        ) : (
                          <>
                            <span className="text-error flex items-center gap-1"><X className="h-3 w-3" /> Your answer: {userAns || '—'}</span>
                            <span className="text-success block">Correct: {correctAns}</span>
                          </>
                        )}
                      </p>
                      {q.explanation && <p className="text-xs text-gray-400 mt-1">{q.explanation}</p>}
                    </div>
                  )
                })}
              </div>
            ))}
          </CardContent>
        </Card>

        <Button className="w-full" onClick={() => {
          // Clear only this test's answers for retake
          setAnswers((prev) => {
            const next = { ...prev }
            allQuestions.forEach((q) => delete next[aKey(test.id, q.id)])
            return next
          })
          setChecked(false)
          setSectionIdx(0)
          setTimerActive(false)
          setAudioPlayed(new Set())
          setSecondsLeft(test.time_minutes * 60)
        }}>
          <RotateCcw className="h-4 w-4 mr-2" /> Retake Test
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold font-heading">🎧 Listening Practice</h1>
        <div className={`flex items-center gap-2 font-mono font-bold ${secondsLeft < 60 ? 'text-error animate-pulse' : 'text-warning'}`}>
          <Timer className="h-5 w-5" />
          {fmtTime(secondsLeft)}
        </div>
      </div>

      {/* Test & Section selectors */}
      <div className="flex flex-col sm:flex-row gap-3">
        {tests.length > 1 && (
          <div className="flex-1">
            <Label className="text-xs text-gray-400 mb-1 block">Test</Label>
            <div className="relative">
              <select
                value={testIdx}
                onChange={(e) => switchTest(Number(e.target.value))}
                className="w-full appearance-none rounded-lg border border-border bg-surface-dark px-3 py-2 pr-9 text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-accent cursor-pointer"
              >
                {tests.map((t, i) => {
                  const attempted = isTestAttempted(t)
                  const answered = countAnswered(t)
                  const total = t.sections.flatMap((s) => s.questions).length
                  return (
                    <option key={t.id} value={i}>
                      {attempted ? '✓ ' : ''}Test {i + 1} — {t.title}{attempted ? ` (${answered}/${total} answered)` : ''}
                    </option>
                  )
                })}
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
          </div>
        )}

        {sections.length > 1 && (
          <div className="flex-1">
            <Label className="text-xs text-gray-400 mb-1 block">Section</Label>
            <div className="relative">
              <select
                value={sectionIdx}
                onChange={(e) => setSectionIdx(Number(e.target.value))}
                className="w-full appearance-none rounded-lg border border-border bg-surface-dark px-3 py-2 pr-9 text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-accent cursor-pointer"
              >
                {sections.map((s, i) => {
                  const attempted = isSectionAttempted(s)
                  const answered = s.questions.filter((q) => answers[aKey(test.id, q.id)]).length
                  return (
                    <option key={s.id} value={i}>
                      {attempted ? '✓ ' : ''}Section {i + 1} — {s.title.replace(/^Section \d+ — /, '')}{attempted ? ` (${answered}/${s.questions.length} answered)` : ''}
                    </option>
                  )
                })}
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
          </div>
        )}
      </div>

      {/* Progress */}
      <div className="flex items-center justify-between text-sm text-gray-400">
        <span>Answered: {answeredCount}/{totalQuestions}</span>
        <span>{test.title}</span>
      </div>

      {/* Start timer button */}
      {!timerActive && secondsLeft > 0 && (
        <Button variant="outline" className="w-full" onClick={startTimer}>
          <Timer className="h-4 w-4 mr-2" /> Start {test.time_minutes}-minute Timer
        </Button>
      )}

      {/* Current section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{section.title}</CardTitle>
          <p className="text-xs text-gray-400">{section.instructions}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Audio playback */}
          <div className={`flex items-center gap-3 rounded-lg p-3 ${audioPlayed.has(section.id) ? 'bg-success/10' : 'bg-warning/10'}`}>
            <Button
              variant="outline"
              size="icon"
              onClick={() => playAudio(section.id, section.transcript)}
              disabled={speaking}
            >
              <Volume2 className="h-5 w-5" />
            </Button>
            <p className="text-sm">
              {speaking ? (
                <span className="text-warning">▶ Playing audio…</span>
              ) : audioPlayed.has(section.id) ? (
                <span className="text-success">✓ Audio played (replay available)</span>
              ) : (
                <span className="text-warning">⚠️ Click to play audio — listen carefully!</span>
              )}
            </p>
          </div>

          {/* Questions */}
          <div className="space-y-4">
            {section.questions.map((q) => {
              const options = q.options ||
                (q.type === 'tfng' ? ['TRUE', 'FALSE', 'NOT GIVEN'] :
                 q.type === 'ynng' ? ['YES', 'NO', 'NOT GIVEN'] : [])
              const userAns = answers[aKey(test.id, q.id)] || ''
              return (
                <div key={q.id}>
                  <p className="font-medium text-sm mb-2">Q{q.number}. {q.text}</p>
                  {q.type === 'completion' ? (
                    <input
                      type="text"
                      value={userAns}
                      onChange={(e) => setAnswer(q.id, e.target.value)}
                      placeholder={`Write no more than ${q.max_words || 1} word(s)…`}
                      className="w-full rounded-lg border border-border bg-transparent px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
                    />
                  ) : (
                    <div className="space-y-1.5">
                      {options.map((opt) => (
                        <button
                          key={opt}
                          onClick={() => setAnswer(q.id, opt)}
                          className={`flex items-center gap-2 w-full text-left px-3 py-1.5 rounded-lg border text-sm transition-colors ${
                            userAns === opt ? 'border-accent bg-accent/10' : 'border-border hover:border-accent'
                          }`}
                        >
                          {userAns === opt && <Check className="h-3 w-3 text-accent" />}
                          {opt}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      <Button className="w-full" variant="success" onClick={() => { setChecked(true); setTimerActive(false) }}>
        Submit All Answers
      </Button>
    </div>
  )
}
