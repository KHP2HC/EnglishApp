import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Mic, Volume2, AlertCircle, Clock, ChevronDown } from 'lucide-react'
import { useSpeechRecognition } from '@/hooks/useSpeech'
import { loadSpeakingTests, type SpeakingTest } from '@/lib/seed-data'

export function Speaking() {
  const { speak, startListening, listening, transcript, isSupported, scorePronunciation } = useSpeechRecognition()
  const [tests, setTests] = useState<SpeakingTest[]>([])
  const [testIdx, setTestIdx] = useState(0)
  const [partIdx, setPartIdx] = useState(0)
  const [questionIdx, setQuestionIdx] = useState(0)
  const [result, setResult] = useState<{ accuracy: number; mismatches: string[] } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [secondsLeft, setSecondsLeft] = useState(0)
  const [timerActive, setTimerActive] = useState(false)
  const [loading, setLoading] = useState(true)
  const [showTestList, setShowTestList] = useState(false)

  useEffect(() => {
    loadSpeakingTests()
      .then((data) => {
        setTests(data)
        setLoading(false)
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
      setTimerActive(false)
    }
  }, [timerActive, secondsLeft])

  if (loading) return <p className="text-gray-400">Loading speaking tests…</p>
  if (tests.length === 0) return <p className="text-gray-400">No speaking tests available.</p>

  const test = tests[testIdx]
  const parts = test.parts || []
  const part = parts[partIdx]
  const question = part?.questions[questionIdx] || ''

  const fmtTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

  const startPartTimer = () => {
    setSecondsLeft(part.timeMinutes * 60)
    setTimerActive(true)
  }

  const handleRecord = async () => {
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

  const next = () => {
    setResult(null)
    setError(null)
    if (questionIdx < part.questions.length - 1) {
      setQuestionIdx((i) => i + 1)
    } else if (partIdx < parts.length - 1) {
      setPartIdx((i) => i + 1)
      setQuestionIdx(0)
    } else {
      // Move to next test, or wrap around
      const nextTestIdx = testIdx < tests.length - 1 ? testIdx + 1 : 0
      setTestIdx(nextTestIdx)
      setPartIdx(0)
      setQuestionIdx(0)
    }
    setTimerActive(false)
  }

  const selectTest = (idx: number) => {
    setTestIdx(idx)
    setPartIdx(0)
    setQuestionIdx(0)
    setResult(null)
    setError(null)
    setTimerActive(false)
    setShowTestList(false)
  }

  const words = question.split(/\s+/).filter(Boolean)

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold font-heading">🗣️ Speaking Practice</h1>
        <div className={`flex items-center gap-2 font-mono font-bold ${secondsLeft < 30 && timerActive ? 'text-error animate-pulse' : 'text-warning'}`}>
          <Clock className="h-5 w-5" />
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

      {/* Part selector */}
      <div className="flex gap-2 flex-wrap">
        {parts.map((p, i) => (
          <button
            key={p.part}
            onClick={() => { setPartIdx(i); setQuestionIdx(0); setResult(null); setTimerActive(false) }}
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

          {/* Start timer */}
          {!timerActive && (
            <Button variant="outline" className="w-full" onClick={startPartTimer}>
              <Clock className="h-4 w-4 mr-2" /> Start {part.timeMinutes}-minute Timer
            </Button>
          )}

          {/* Play correct pronunciation */}
          <Button variant="outline" onClick={() => speak(question, 0.85)} className="w-full">
            <Volume2 className="h-4 w-4 mr-2" /> Play Examiner (Correct Pronunciation)
          </Button>

          {/* Record button */}
          <Button
            onClick={handleRecord}
            disabled={listening || !isSupported}
            className="w-full"
            variant={listening ? 'destructive' : 'default'}
          >
            <Mic className="h-4 w-4 mr-2" />
            {listening ? 'Listening…' : 'Record & Evaluate'}
          </Button>

          {error && <p className="text-sm text-error">{error}</p>}

          {result && (
            <div className="space-y-3">
              <div className="text-center">
                <p className="text-3xl font-bold text-accent">{Math.round(result.accuracy)}%</p>
                <p className="text-sm text-gray-400">Pronunciation Accuracy</p>
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

      {/* IELTS Speaking Format Info */}
      <Card>
        <CardContent className="py-4 space-y-2">
          <p className="text-sm font-medium text-gray-400">IELTS Speaking Test Format:</p>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="rounded-lg border border-border p-2">
              <p className="font-medium text-accent">Part 1</p>
              <p className="text-gray-400">Introduction & Interview</p>
              <p className="text-gray-500">4-5 min</p>
            </div>
            <div className="rounded-lg border border-border p-2">
              <p className="font-medium text-accent">Part 2</p>
              <p className="text-gray-400">Long Turn (Cue Card)</p>
              <p className="text-gray-500">3-4 min</p>
            </div>
            <div className="rounded-lg border border-border p-2">
              <p className="font-medium text-accent">Part 3</p>
              <p className="text-gray-400">Discussion</p>
              <p className="text-gray-500">4-5 min</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
