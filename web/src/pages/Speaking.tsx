import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Mic, Volume2, AlertCircle, Clock, ChevronDown, RotateCcw, CheckCircle2, XCircle } from 'lucide-react'
import { useSpeechRecognition } from '@/hooks/useSpeech'
import { useAuthStore } from '@/stores/auth.store'
import { loadExamSpeakingTests, type SpeakingTest } from '@/lib/seed-data'

export function Speaking() {
  const { speak, stopSpeaking, startListening, stopListening, listening, transcript, isSupported, scorePronunciation } = useSpeechRecognition()
  const { user } = useAuthStore()
  const [tests, setTests] = useState<SpeakingTest[]>([])
  const [testIdx, setTestIdx] = useState(0)
  const [partIdx, setPartIdx] = useState(0)
  const [questionIdx, setQuestionIdx] = useState(0)
  const [result, setResult] = useState<{ accuracy: number; mismatches: string[]; results: { word: string; correct: boolean; suggestion: string | null }[] } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [secondsLeft, setSecondsLeft] = useState(0)
  const [timerActive, setTimerActive] = useState(false)
  const [timerMode, setTimerMode] = useState<'prep' | 'speak' | null>(null)
  const [loading, setLoading] = useState(true)
  const [showTestList, setShowTestList] = useState(false)
  const [recordSeconds, setRecordSeconds] = useState(0)
  const recordIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    loadExamSpeakingTests(user?.target_exam || undefined)
      .then((data) => {
        setTests(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [user?.target_exam])

  // Countdown timer
  useEffect(() => {
    if (timerActive && secondsLeft > 0) {
      const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000)
      return () => clearTimeout(t)
    }
    if (timerActive && secondsLeft === 0) {
      setTimerActive(false)
      if (timerMode === 'prep') {
        // Auto-switch from prep to speaking time
        setTimerMode('speak')
        setSecondsLeft(120)
        setTimerActive(true)
      } else if (timerMode === 'speak') {
        setTimerMode(null)
      }
    }
  }, [timerActive, secondsLeft, timerMode])

  // Recording duration counter
  useEffect(() => {
    if (listening) {
      setRecordSeconds(0)
      recordIntervalRef.current = setInterval(() => {
        setRecordSeconds((s) => s + 1)
      }, 1000)
    } else {
      if (recordIntervalRef.current) {
        clearInterval(recordIntervalRef.current)
        recordIntervalRef.current = null
      }
    }
    return () => {
      if (recordIntervalRef.current) clearInterval(recordIntervalRef.current)
    }
  }, [listening])

  if (loading) return <p className="text-gray-400">Loading speaking tests…</p>
  if (tests.length === 0) return <p className="text-gray-400">No speaking tests available.</p>

  const test = tests[testIdx]
  const parts = test.parts || []
  const part = parts[partIdx]
  const question = part?.questions[questionIdx] || ''

  const fmtTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

  const startPrepTimer = () => {
    setSecondsLeft(60) // 1 minute prep
    setTimerActive(true)
    setTimerMode('prep')
  }

  const startSpeakTimer = () => {
    setSecondsLeft(part.timeMinutes * 60)
    setTimerActive(true)
    setTimerMode('speak')
  }

  const stopTimer = () => {
    setTimerActive(false)
    setTimerMode(null)
  }

  const handleRecord = async () => {
    if (listening) {
      stopListening()
      return
    }
    setError(null)
    setResult(null)
    try {
      const spoken = await startListening()
      const score = scorePronunciation(question, spoken)
      setResult(score)
    } catch (err: any) {
      setError(err.message || 'Recording failed')
    }
  }

  const resetResult = () => {
    setResult(null)
    setError(null)
    stopSpeaking()
  }

  const next = () => {
    resetResult()
    stopTimer()
    if (questionIdx < part.questions.length - 1) {
      setQuestionIdx((i) => i + 1)
    } else if (partIdx < parts.length - 1) {
      setPartIdx((i) => i + 1)
      setQuestionIdx(0)
    } else {
      const nextTestIdx = testIdx < tests.length - 1 ? testIdx + 1 : 0
      setTestIdx(nextTestIdx)
      setPartIdx(0)
      setQuestionIdx(0)
    }
  }

  const selectTest = (idx: number) => {
    setTestIdx(idx)
    setPartIdx(0)
    setQuestionIdx(0)
    resetResult()
    stopTimer()
    setShowTestList(false)
  }

  const words = question.split(/\s+/).filter(Boolean)
  const isPart2 = part?.part === 2

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold font-heading">🗣️ Speaking Practice</h1>
        <div className={`flex items-center gap-2 font-mono font-bold ${secondsLeft < 30 && timerActive ? 'text-error animate-pulse' : 'text-warning'}`}>
          <Clock className="h-5 w-5" />
          {timerActive ? fmtTime(secondsLeft) : '--:--'}
          {timerMode === 'prep' && <span className="text-xs text-gray-400 ml-1">prep</span>}
          {timerMode === 'speak' && <span className="text-xs text-gray-400 ml-1">speak</span>}
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

      {/* Part selector */}
      <div className="flex gap-2 flex-wrap">
        {parts.map((p, i) => (
          <button
            key={p.part}
            onClick={() => { setPartIdx(i); setQuestionIdx(0); resetResult(); stopTimer() }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              partIdx === i ? 'bg-accent text-white' : 'bg-surface-dark text-gray-400 hover:text-white'
            }`}
          >
            Part {p.part}
          </button>
        ))}
      </div>

      {!isSupported && (
        <Card>
          <CardContent className="py-4 flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-warning" />
            <p className="text-sm text-warning">
              Pronunciation practice works best in Chrome or Edge. Your browser doesn't support speech recognition.
            </p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{part.title}</CardTitle>
          <p className="text-xs text-gray-400">{part.instructions}</p>
          <p className="text-xs text-gray-500 mt-1">
            Question {questionIdx + 1} of {part.questions.length} · Suggested time: {part.timeMinutes} min
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Target question with word highlighting */}
          <div className="rounded-xl bg-black/20 p-4">
            <p className="text-lg leading-relaxed whitespace-pre-line">
              {result ? (
                words.map((word, i) => {
                  const clean = word.toLowerCase().replace(/[^a-z']/g, '')
                  const isMismatch = result.mismatches.some(
                    (m) => m.toLowerCase().replace(/[^a-z']/g, '') === clean
                  )
                  return (
                    <span key={i} className={isMismatch ? 'text-error font-bold' : 'text-success'}>
                      {word}{' '}
                    </span>
                  )
                })
              ) : (
                question
              )}
            </p>
          </div>

          {/* Part 2: Preparation timer */}
          {isPart2 && !timerActive && (
            <Button variant="outline" className="w-full" onClick={startPrepTimer}>
              <Clock className="h-4 w-4 mr-2" /> Start 1-minute Preparation Timer
            </Button>
          )}

          {/* Speaking timer */}
          {!timerActive && !isPart2 && (
            <Button variant="outline" className="w-full" onClick={startSpeakTimer}>
              <Clock className="h-4 w-4 mr-2" /> Start {part.timeMinutes}-minute Timer
            </Button>
          )}
          {isPart2 && !timerActive && timerMode === null && (
            <Button variant="outline" className="w-full" onClick={startSpeakTimer}>
              <Clock className="h-4 w-4 mr-2" /> Start {part.timeMinutes}-minute Speaking Timer
            </Button>
          )}

          {/* Stop timer */}
          {timerActive && (
            <Button variant="outline" className="w-full" onClick={stopTimer}>
              <RotateCcw className="h-4 w-4 mr-2" /> Stop Timer
            </Button>
          )}

          {/* Play correct pronunciation */}
          <Button variant="outline" onClick={() => speak(question, 0.85)} className="w-full">
            <Volume2 className="h-4 w-4 mr-2" /> Play Examiner (Correct Pronunciation)
          </Button>

          {/* Record button */}
          <Button
            onClick={handleRecord}
            disabled={!isSupported}
            className="w-full"
            variant={listening ? 'destructive' : 'default'}
          >
            <Mic className="h-4 w-4 mr-2" />
            {listening ? `Listening… ${fmtTime(recordSeconds)}` : 'Record & Evaluate'}
          </Button>

          {error && <p className="text-sm text-error">{error}</p>}

          {result && (
            <div className="space-y-3">
              {/* Accuracy score */}
              <div className="text-center">
                <p className="text-4xl font-bold text-accent">{Math.round(result.accuracy)}%</p>
                <p className="text-sm text-gray-400">Pronunciation Accuracy</p>
              </div>

              {/* Correct / incorrect summary */}
              <div className="flex items-center justify-center gap-6 text-sm">
                <span className="flex items-center gap-1 text-success">
                  <CheckCircle2 className="h-4 w-4" />
                  {result.results.filter((r) => r.correct).length} correct
                </span>
                <span className="flex items-center gap-1 text-error">
                  <XCircle className="h-4 w-4" />
                  {result.results.filter((r) => !r.correct).length} to improve
                </span>
              </div>

              {/* Word-by-word breakdown */}
              <div className="rounded-lg border border-border p-3">
                <p className="text-xs font-medium text-gray-400 mb-2">Word-by-word breakdown:</p>
                <div className="flex flex-wrap gap-1.5">
                  {result.results.map((r, i) => (
                    <span
                      key={i}
                      className={`px-2 py-0.5 rounded text-xs ${
                        r.correct
                          ? 'bg-success/20 text-success'
                          : 'bg-error/20 text-error'
                      }`}
                      title={r.suggestion ? `Heard: ${r.suggestion}` : undefined}
                    >
                      {r.word}
                    </span>
                  ))}
                </div>
              </div>

              {result.mismatches.length > 0 && (
                <p className="text-sm text-warning">
                  Words to practice: {result.mismatches.join(', ')}
                </p>
              )}
            </div>
          )}

          {transcript && !result && (
            <p className="text-sm text-gray-400">Heard: "{transcript}"</p>
          )}

          <Button onClick={next} className="w-full">
            {questionIdx < part.questions.length - 1 || partIdx < parts.length - 1
              ? 'Next Question →'
              : testIdx < tests.length - 1
                ? 'Next Test →'
                : 'Restart from Test 1 →'}
          </Button>
        </CardContent>
      </Card>

      {/* Speaking Format Info */}
      <Card>
        <CardContent className="py-4 space-y-2">
          <p className="text-sm font-medium text-gray-400">
            {(user?.target_exam || 'IELTS') === 'VSTEP'
              ? 'VSTEP Speaking Test Format:'
              : 'IELTS Speaking Test Format:'}
          </p>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="rounded-lg border border-border p-2">
              <p className="font-medium text-accent">Part 1</p>
              <p className="text-gray-400">
                {user?.target_exam === 'VSTEP' ? 'Social Interaction' : 'Introduction & Interview'}
              </p>
              <p className="text-gray-500">{user?.target_exam === 'VSTEP' ? '4 min' : '4-5 min'}</p>
            </div>
            <div className="rounded-lg border border-border p-2">
              <p className="font-medium text-accent">Part 2</p>
              <p className="text-gray-400">
                {user?.target_exam === 'VSTEP' ? 'Solution Discussion' : 'Long Turn (Cue Card)'}
              </p>
              <p className="text-gray-500">{user?.target_exam === 'VSTEP' ? '4 min' : '3-4 min'}</p>
            </div>
            <div className="rounded-lg border border-border p-2">
              <p className="font-medium text-accent">Part 3</p>
              <p className="text-gray-400">
                {user?.target_exam === 'VSTEP' ? 'Topic Development' : 'Discussion'}
              </p>
              <p className="text-gray-500">{user?.target_exam === 'VSTEP' ? '4 min' : '4-5 min'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
