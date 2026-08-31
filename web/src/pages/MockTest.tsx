import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/stores/auth.store'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Timer, Play, CheckCircle, ChevronRight, Volume2 } from 'lucide-react'
import {
  loadReadingTests, loadListeningTests, loadWritingTasks,
  type ReadingTest, type ListeningTest, type WritingTask,
  type ReadingQuestion, type ListeningQuestion,
} from '@/lib/seed-data'
import { rawToReadingBand, rawToListeningBand, overallBand, bandLabel } from '@/lib/ielts-bands'
import { useSpeech } from '@/hooks/useSpeech'
import type { ExamType } from '@/lib/supabase'

// ── Types ────────────────────────────────────────────────────────────

interface SectionConfig {
  name: string
  timeMinutes: number
  description: string
}

interface MockConfig {
  title: string
  totalQuestions: number
  timeMinutes: number
  sections: SectionConfig[]
}

const MOCKS: Record<ExamType, MockConfig> = {
  IELTS: {
    title: 'IELTS Full Mock Test',
    totalQuestions: 82,
    timeMinutes: 175,
    sections: [
      { name: 'Listening', timeMinutes: 40, description: '4 sections, 40 items. Audio plays once — no replay.' },
      { name: 'Reading', timeMinutes: 60, description: '3 passages, 40 questions. Academic texts.' },
      { name: 'Writing', timeMinutes: 60, description: 'Task 1 (150 words, 20 min) + Task 2 (250 words, 40 min).' },
      { name: 'Speaking', timeMinutes: 15, description: 'Part 1 (interview), Part 2 (long turn), Part 3 (discussion).' },
    ],
  },
  TOEIC: {
    title: 'TOEIC Full Mock Test',
    totalQuestions: 200,
    timeMinutes: 120,
    sections: [
      { name: 'Listening', timeMinutes: 45, description: 'Photographs, question-response, conversations, talks.' },
      { name: 'Reading', timeMinutes: 75, description: 'Incomplete sentences, text completion, passages.' },
    ],
  },
  TOEFL: {
    title: 'TOEFL Full Mock Test',
    totalQuestions: 58,
    timeMinutes: 200,
    sections: [
      { name: 'Reading', timeMinutes: 35, description: '2-3 academic passages.' },
      { name: 'Listening', timeMinutes: 36, description: 'Lectures and conversations.' },
      { name: 'Speaking', timeMinutes: 17, description: 'Independent + integrated tasks.' },
      { name: 'Writing', timeMinutes: 50, description: 'Integrated + independent essay.' },
    ],
  },
  VSTEP: {
    title: 'VSTEP Full Mock Test',
    totalQuestions: 40,
    timeMinutes: 150,
    sections: [
      { name: 'Listening', timeMinutes: 40, description: '3 parts, 15 items.' },
      { name: 'Reading', timeMinutes: 50, description: '3 passages, 15 questions.' },
      { name: 'Writing', timeMinutes: 30, description: 'Short writing task.' },
      { name: 'Speaking', timeMinutes: 12, description: 'Interview format.' },
    ],
  },
}

// ── Answer normalisation ─────────────────────────────────────────────

function normalise(s: string): string {
  return s.toLowerCase().trim().replace(/[.,!?;:'"]/g, '').replace(/\s+/g, ' ')
}

function isCorrect(q: { answer: string | string[] }, userAnswer: string): boolean {
  if (!userAnswer) return false
  const answers = Array.isArray(q.answer) ? q.answer : [q.answer]
  const norm = normalise(userAnswer)
  return answers.some((a) => normalise(a) === norm)
}

// ── Component ────────────────────────────────────────────────────────

export function MockTest() {
  const { user } = useAuthStore()
  const examType = (user?.target_exam || 'IELTS') as ExamType
  const config = MOCKS[examType]
  const { speak } = useSpeech()

  const [phase, setPhase] = useState<'intro' | 'section-intro' | 'test' | 'results'>('intro')
  const [sectionIdx, setSectionIdx] = useState(0)
  const [secondsLeft, setSecondsLeft] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [writingAnswers, setWritingAnswers] = useState<Record<string, string>>({})

  // Loaded test data
  const [readingTests, setReadingTests] = useState<ReadingTest[]>([])
  const [listeningTests, setListeningTests] = useState<ListeningTest[]>([])
  const [writingTasks, setWritingTasks] = useState<WritingTask[]>([])
  const [dataLoaded, setDataLoaded] = useState(false)

  // Results
  const [results, setResults] = useState<{
    listening: { raw: number; total: number; band: number }
    reading: { raw: number; total: number; band: number }
    writing: { submitted: boolean; wordCount: number }
    speaking: { attempted: boolean }
    overall: number
  } | null>(null)

  // ── Load data ──────────────────────────────────────────────────────

  useEffect(() => {
    Promise.all([loadReadingTests(), loadListeningTests(), loadWritingTasks()])
      .then(([rt, lt, wt]) => {
        setReadingTests(rt)
        setListeningTests(lt)
        setWritingTasks(wt)
        setDataLoaded(true)
      })
      .catch(() => setDataLoaded(true))
  }, [])

  // ── Timer ─────────────────────────────────────────────────────────

  useEffect(() => {
    if (phase === 'test' && secondsLeft > 0) {
      const t = setTimeout(() => setSecondsLeft((s) => s - 1), 1000)
      return () => clearTimeout(t)
    }
    if (phase === 'test' && secondsLeft === 0) {
      // Auto-advance
      if (sectionIdx < config.sections.length - 1) {
        setSectionIdx((i) => i + 1)
        setPhase('section-intro')
      } else {
        computeResults()
      }
    }
  }, [phase, secondsLeft])

  // ── Section management ────────────────────────────────────────────

  const startTest = () => {
    setSectionIdx(0)
    setAnswers({})
    setWritingAnswers({})
    setResults(null)
    setPhase('section-intro')
  }

  const beginSection = () => {
    setSecondsLeft(config.sections[sectionIdx].timeMinutes * 60)
    setPhase('test')
  }

  const goToNextSection = () => {
    if (sectionIdx < config.sections.length - 1) {
      setSectionIdx((i) => i + 1)
      setPhase('section-intro')
    } else {
      computeResults()
    }
  }

  function computeResults() {
    // Listening
    let listeningRaw = 0
    let listeningTotal = 0
    for (const lt of listeningTests) {
      for (const sec of lt.sections) {
        for (const q of sec.questions) {
          listeningTotal++
          if (isCorrect(q as any, answers[q.id])) listeningRaw++
        }
      }
    }

    // Reading
    let readingRaw = 0
    let readingTotal = 0
    for (const rt of readingTests) {
      for (const p of rt.passages) {
        for (const q of p.questions) {
          readingTotal++
          if (isCorrect(q as any, answers[q.id])) readingRaw++
        }
      }
    }

    // Writing
    const writingWordCount = Object.values(writingAnswers).reduce(
      (sum, essay) => sum + essay.split(/\s+/).filter(Boolean).length, 0
    )

    // Speaking
    const speakingAttempted = Object.keys(answers).some((k) => k.startsWith('speaking-'))

    const listenBand = listeningTotal > 0 ? rawToListeningBand(listeningRaw, listeningTotal) : 0
    const readBand = readingTotal > 0 ? rawToReadingBand(readingRaw, readingTotal) : 0
    const overall = overallBand([listenBand, readBand])

    setResults({
      listening: { raw: listeningRaw, total: listeningTotal, band: listenBand },
      reading: { raw: readingRaw, total: readingTotal, band: readBand },
      writing: { submitted: writingWordCount > 0, wordCount: writingWordCount },
      speaking: { attempted: speakingAttempted },
      overall,
    })
    setPhase('results')

    // Save session
    if (user) {
      const totalCorrect = listeningRaw + readingRaw
      const totalQ = listeningTotal + readingTotal
      supabase.from('study_sessions').insert({
        user_id: user.id,
        session_type: 'MOCK',
        ended_at: new Date().toISOString(),
        xp_earned: 50,
        items_total: totalQ,
        items_correct: totalCorrect,
      }).then(() => {})
      supabase
        .from('profiles')
        .update({ total_xp: (user.total_xp || 0) + 50 })
        .eq('id', user.id)
        .then(() => {})
    }
  }

  // ── Helpers ────────────────────────────────────────────────────────

  const fmtTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

  const currentSection = config.sections[sectionIdx]

  // ── Render: Intro ──────────────────────────────────────────────────

  if (phase === 'intro') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold font-heading">🧪 Mock Test — {examType}</h1>
        <Card>
          <CardHeader><CardTitle>{config.title}</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-400">
              {config.totalQuestions} questions · {config.timeMinutes} minutes total
            </p>
            <div className="space-y-2">
              {config.sections.map((sec, i) => (
                <div key={i} className="rounded-lg border border-border p-3">
                  <p className="font-medium text-sm">Section {i + 1}: {sec.name}</p>
                  <p className="text-xs text-gray-400">{sec.timeMinutes} min</p>
                  <p className="text-xs text-gray-500 mt-1">{sec.description}</p>
                </div>
              ))}
            </div>
            <div className="rounded-lg border border-warning/30 bg-warning/5 p-3 space-y-1">
              <p className="text-sm text-warning font-medium">⚠️ Important:</p>
              <p className="text-xs text-gray-400">• Each section has its own timer and auto-submits when time expires.</p>
              <p className="text-xs text-gray-400">• You cannot return to a previous section once completed.</p>
              {examType === 'IELTS' && <p className="text-xs text-gray-400">• Listening audio plays only once — pay close attention.</p>}
            </div>
            <Button size="lg" className="w-full" onClick={startTest} disabled={!dataLoaded}>
              <Play className="h-4 w-4 mr-2" /> {dataLoaded ? 'Start Mock Test' : 'Loading test data…'}
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ── Render: Section Intro ─────────────────────────────────────────

  if (phase === 'section-intro') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold font-heading">Section {sectionIdx + 1} of {config.sections.length}</h1>
        <Card>
          <CardHeader><CardTitle>{currentSection.name}</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-400">{currentSection.description}</p>
            <p className="text-sm">
              Time allowed: <span className="font-bold text-accent">{currentSection.timeMinutes} minutes</span>
            </p>
            {sectionIdx > 0 && (
              <p className="text-xs text-gray-500">
                Previous section has been submitted. You cannot go back.
              </p>
            )}
            <Button size="lg" className="w-full" onClick={beginSection}>
              <Play className="h-4 w-4 mr-2" /> Start {currentSection.name} Section
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ── Render: Results ────────────────────────────────────────────────

  if (phase === 'results' && results) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold font-heading text-center">📊 Mock Test Results</h1>

        {/* Overall Band */}
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-sm text-gray-400">Overall IELTS Band Score</p>
            <p className="text-6xl font-bold text-accent">{results.overall.toFixed(1)}</p>
            <p className="text-sm text-gray-400 mt-1">{bandLabel(results.overall)}</p>
          </CardContent>
        </Card>

        {/* Section Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader><CardTitle>🎧 Listening</CardTitle></CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-accent">{results.listening.band.toFixed(1)}</p>
              <p className="text-sm text-gray-400">
                Raw: {results.listening.raw}/{results.listening.total}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>📖 Reading</CardTitle></CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-accent">{results.reading.band.toFixed(1)}</p>
              <p className="text-sm text-gray-400">
                Raw: {results.reading.raw}/{results.reading.total}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>✍️ Writing</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-gray-400">
                {results.writing.submitted
                  ? `Submitted (${results.writing.wordCount} words). AI feedback available in Writing practice.`
                  : 'Not submitted'}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>🗣️ Speaking</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-gray-400">
                {results.speaking.attempted
                  ? 'Practice completed. Use Speaking practice for detailed feedback.'
                  : 'Not attempted'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Improvement Tips */}
        <Card>
          <CardHeader><CardTitle>Improvement Tips</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm text-left">
            {results.overall >= 7 ? (
              <>
                <p>💡 Excellent! You're at a competent level. Focus on exam technique and time management.</p>
                <p>💡 Practice the hardest question types (matching headings, Yes/No/Not Given) to push higher.</p>
              </>
            ) : results.overall >= 5 ? (
              <>
                <p>💡 Good progress! Your weakest section needs the most attention.</p>
                <p>💡 Build vocabulary daily with SRS and practice timed reading passages.</p>
                <p>💡 For listening, practice with BBC Learning English or IELTS-style audio.</p>
              </>
            ) : (
              <>
                <p>💡 Build your foundation: focus on core vocabulary and grammar first.</p>
                <p>💡 Practice individual skills before attempting full mock tests.</p>
                <p>💡 Use the SRS vocabulary screen daily to expand your word bank.</p>
              </>
            )}
          </CardContent>
        </Card>

        <Button className="w-full" onClick={() => setPhase('intro')}>Back to Mock Test</Button>
      </div>
    )
  }

  // ── Render: Test (section-specific) ────────────────────────────────

  const sectionName = currentSection.name.toLowerCase()

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      {/* Header with timer */}
      <div className="flex items-center justify-between sticky top-0 z-10 bg-background/95 backdrop-blur py-2">
        <div>
          <h1 className="text-lg font-bold font-heading">
            {currentSection.name}
            <span className="text-sm text-gray-400 ml-2">({sectionIdx + 1}/{config.sections.length})</span>
          </h1>
        </div>
        <div className={`flex items-center gap-2 font-mono font-bold ${secondsLeft < 60 ? 'text-error animate-pulse' : 'text-warning'}`}>
          <Timer className="h-5 w-5" />
          {fmtTime(secondsLeft)}
        </div>
      </div>

      {/* ── Listening Section ── */}
      {sectionName === 'listening' && (
        <ListeningSection
          tests={listeningTests}
          answers={answers}
          setAnswers={setAnswers}
          speak={speak}
        />
      )}

      {/* ── Reading Section ── */}
      {sectionName === 'reading' && (
        <ReadingSection
          tests={readingTests}
          answers={answers}
          setAnswers={setAnswers}
        />
      )}

      {/* ── Writing Section ── */}
      {sectionName === 'writing' && (
        <WritingSection
          tasks={writingTasks}
          answers={writingAnswers}
          setAnswers={setWritingAnswers}
        />
      )}

      {/* ── Speaking Section ── */}
      {sectionName === 'speaking' && (
        <SpeakingSection
          answers={answers}
          setAnswers={setAnswers}
          speak={speak}
        />
      )}

      {/* Submit button */}
      <Button className="w-full" variant="success" onClick={goToNextSection}>
        {sectionIdx < config.sections.length - 1 ? (
          <><ChevronRight className="h-4 w-4 mr-2" /> Submit & Go to Next Section</>
        ) : (
          <><CheckCircle className="h-4 w-4 mr-2" /> Submit Final Section</>
        )}
      </Button>
    </div>
  )
}

// ══════════════════════════════════════════════════════════════════════
// LISTENING SECTION
// ══════════════════════════════════════════════════════════════════════

function ListeningSection({
  tests, answers, setAnswers, speak,
}: {
  tests: ListeningTest[]
  answers: Record<string, string>
  setAnswers: React.Dispatch<React.SetStateAction<Record<string, string>>>
  speak: (text: string, rate?: number) => void
}) {
  if (tests.length === 0) {
    return <p className="text-gray-400 text-center py-8">No listening tests available.</p>
  }

  return (
    <div className="space-y-6">
      {tests.flatMap((test) =>
        test.sections.map((sec) => (
          <Card key={sec.id}>
            <CardHeader>
              <CardTitle className="text-base">{sec.title}</CardTitle>
              <p className="text-xs text-gray-400">{sec.instructions}</p>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Audio playback via TTS */}
              <div className="flex items-center gap-3 rounded-lg bg-black/20 p-3">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => speak(sec.transcript, 0.9)}
                >
                  <Volume2 className="h-5 w-5" />
                </Button>
                <p className="text-sm text-gray-400">
                  Click to play audio (plays once — listen carefully!)
                </p>
              </div>

              {/* Questions */}
              <div className="space-y-3">
                {sec.questions.map((q) => (
                  <QuestionRenderer
                    key={q.id}
                    q={q}
                    answer={answers[q.id] || ''}
                    onAnswer={(val) => setAnswers((a) => ({ ...a, [q.id]: val }))}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  )
}

// ══════════════════════════════════════════════════════════════════════
// READING SECTION
// ══════════════════════════════════════════════════════════════════════

function ReadingSection({
  tests, answers, setAnswers,
}: {
  tests: ReadingTest[]
  answers: Record<string, string>
  setAnswers: React.Dispatch<React.SetStateAction<Record<string, string>>>
}) {
  const [activePassage, setActivePassage] = useState(0)

  if (tests.length === 0) {
    return <p className="text-gray-400 text-center py-8">No reading tests available.</p>
  }

  // Flatten all passages across all tests
  const allPassages = tests.flatMap((t) => t.passages)
  const passage = allPassages[activePassage]

  return (
    <div className="space-y-4">
      {/* Passage selector */}
      <div className="flex gap-2 flex-wrap">
        {allPassages.map((p, i) => (
          <button
            key={p.id}
            onClick={() => setActivePassage(i)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activePassage === i ? 'bg-accent text-white' : 'bg-surface-dark text-gray-400 hover:text-white'
            }`}
          >
            Passage {i + 1}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Passage text */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{passage.title}</CardTitle>
            <p className="text-xs text-gray-400">[{passage.difficulty}] {passage.instructions}</p>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-gray-300 space-y-3 max-h-[60vh] overflow-y-auto">
              {passage.text.split('\n\n').map((p, i) => (
                <p key={i}>{p}</p>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Questions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Questions ({passage.questions.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 max-h-[60vh] overflow-y-auto">
            {passage.questions.map((q) => (
              <QuestionRenderer
                key={q.id}
                q={q}
                answer={answers[q.id] || ''}
                onAnswer={(val) => setAnswers((a) => ({ ...a, [q.id]: val }))}
              />
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// ══════════════════════════════════════════════════════════════════════
// WRITING SECTION
// ══════════════════════════════════════════════════════════════════════

function WritingSection({
  tasks, answers, setAnswers,
}: {
  tasks: WritingTask[]
  answers: Record<string, string>
  setAnswers: React.Dispatch<React.SetStateAction<Record<string, string>>>
}) {
  const [activeTask, setActiveTask] = useState(0)

  if (tasks.length === 0) {
    return <p className="text-gray-400 text-center py-8">No writing tasks available.</p>
  }

  const task = tasks[activeTask]
  const essay = answers[task.id] || ''
  const wordCount = essay.split(/\s+/).filter(Boolean).length
  const minWords = task.min_words || 150

  return (
    <div className="space-y-4">
      {/* Task selector */}
      <div className="flex gap-2 flex-wrap">
        {tasks.map((t, i) => (
          <button
            key={t.id}
            onClick={() => setActiveTask(i)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeTask === i ? 'bg-accent text-white' : 'bg-surface-dark text-gray-400 hover:text-white'
            }`}
          >
            {t.type === 'task1' ? 'Task 1' : 'Task 2'}
          </button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{task.title}</CardTitle>
          <p className="text-xs text-gray-400">{task.instructions}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Prompt */}
          <div className="rounded-lg bg-black/20 p-4">
            <p className="text-sm text-gray-200">{task.prompt}</p>
            {task.data_description && (
              <p className="text-xs text-gray-400 mt-2 italic">📊 {task.data_description}</p>
            )}
          </div>

          {/* Essay input */}
          <div>
            <textarea
              value={essay}
              onChange={(e) => setAnswers((a) => ({ ...a, [task.id]: e.target.value }))}
              placeholder={`Write at least ${minWords} words…`}
              className="w-full min-h-[300px] rounded-xl border border-border bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
            />
            <div className="flex items-center justify-between mt-1">
              <p className={`text-xs ${wordCount >= minWords ? 'text-success' : 'text-warning'}`}>
                {wordCount} / {minWords} words minimum
              </p>
              {task.time_minutes && (
                <p className="text-xs text-gray-400">Suggested: {task.time_minutes} min</p>
              )}
            </div>
          </div>

          {/* Band descriptors */}
          {task.band_descriptors && (
            <div className="rounded-lg border border-border p-3 space-y-1">
              <p className="text-xs font-medium text-gray-400">Assessment Criteria:</p>
              {task.band_descriptors.task_achievement && <p className="text-xs text-gray-500">• Task Achievement: {task.band_descriptors.task_achievement}</p>}
              {task.band_descriptors.coherence && <p className="text-xs text-gray-500">• Coherence: {task.band_descriptors.coherence}</p>}
              {task.band_descriptors.lexical_resource && <p className="text-xs text-gray-500">• Lexical Resource: {task.band_descriptors.lexical_resource}</p>}
              {task.band_descriptors.grammar && <p className="text-xs text-gray-500">• Grammar: {task.band_descriptors.grammar}</p>}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// ══════════════════════════════════════════════════════════════════════
// SPEAKING SECTION
// ══════════════════════════════════════════════════════════════════════

const SPEAKING_PARTS = [
  {
    part: 1,
    title: 'Part 1 — Introduction & Interview',
    instructions: 'The examiner asks general questions about yourself, your home, work/studies, and familiar topics. Answer in 1-2 sentences each.',
    questions: [
      "Let's talk about your hometown. Where is it, and what do you like most about it?",
      'What do you enjoy doing in your free time?',
      'Do you prefer reading books or watching films? Why?',
      'Is there anything you would like to change about your daily routine?',
    ],
  },
  {
    part: 2,
    title: 'Part 2 — Long Turn (Cue Card)',
    instructions: 'You have 1 minute to prepare and 2 minutes to speak. Describe the topic below in detail.',
    questions: [
      'Describe a memorable journey you have taken. You should say: where you went, who you went with, what you did there, and explain why it was memorable.',
    ],
  },
  {
    part: 3,
    title: 'Part 3 — Discussion',
    instructions: 'The examiner asks abstract questions related to the Part 2 topic. Give extended answers with reasons and examples.',
    questions: [
      'How has travel changed over the past few decades?',
      'Do you think technology has made people more or less connected? Why?',
      'What are the benefits of experiencing different cultures?',
      'Some people say travel broadens the mind. Do you agree?',
    ],
  },
]

function SpeakingSection({
  answers, setAnswers, speak,
}: {
  answers: Record<string, string>
  setAnswers: React.Dispatch<React.SetStateAction<Record<string, string>>>
  speak: (text: string, rate?: number) => void
}) {
  return (
    <div className="space-y-4">
      {SPEAKING_PARTS.map((part) => (
        <Card key={part.part}>
          <CardHeader>
            <CardTitle className="text-base">{part.title}</CardTitle>
            <p className="text-xs text-gray-400">{part.instructions}</p>
          </CardHeader>
          <CardContent className="space-y-4">
            {part.questions.map((q, qi) => {
              const key = `speaking-${part.part}-${qi}`
              return (
                <div key={qi} className="space-y-2">
                  <div className="flex items-start gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => speak(q, 0.85)}
                    >
                      <Volume2 className="h-4 w-4" />
                    </Button>
                    <p className="text-sm text-gray-200 flex-1">{q}</p>
                  </div>
                  <textarea
                    value={answers[key] || ''}
                    onChange={(e) => setAnswers((a) => ({ ...a, [key]: e.target.value }))}
                    placeholder="Type or record your answer…"
                    className="w-full min-h-[80px] rounded-lg border border-border bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
                  />
                </div>
              )
            })}
          </CardContent>
        </Card>
      ))}
      <p className="text-xs text-gray-400 text-center">
        💡 Tip: Use the Speaking Practice page for pronunciation scoring with speech recognition.
      </p>
    </div>
  )
}

// ══════════════════════════════════════════════════════════════════════
// SHARED QUESTION RENDERER
// ══════════════════════════════════════════════════════════════════════

function QuestionRenderer({
  q, answer, onAnswer,
}: {
  q: ReadingQuestion | ListeningQuestion
  answer: string
  onAnswer: (val: string) => void
}) {
  const options = q.options ||
    (q.type === 'tfng' ? ['TRUE', 'FALSE', 'NOT GIVEN'] :
     q.type === 'ynng' ? ['YES', 'NO', 'NOT GIVEN'] : [])

  return (
    <div>
      <p className="font-medium text-sm mb-2">Q{q.number}. {q.text}</p>
      {q.type === 'completion' ? (
        <input
          type="text"
          value={answer}
          onChange={(e) => onAnswer(e.target.value)}
          placeholder={`Write no more than ${q.max_words || 1} word(s)…`}
          className="w-full rounded-lg border border-border bg-transparent px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        />
      ) : (
        <div className="space-y-1.5">
          {options.map((opt) => (
            <button
              key={opt}
              onClick={() => onAnswer(opt)}
              className={`flex items-center gap-2 w-full text-left px-3 py-1.5 rounded-lg border text-sm transition-colors ${
                answer === opt ? 'border-accent bg-accent/10' : 'border-border hover:border-accent'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
