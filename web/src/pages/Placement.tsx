import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  CheckCircle2, XCircle, Brain, ArrowRight, RotateCcw,
  BookOpen, Headphones, PenLine, Mic, Languages, Loader2,
} from 'lucide-react'
import {
  initCATState,
  recordAnswer,
  getEstimatedBand,
  getSkillBreakdown,
  isComplete,
  buildAdaptiveTest,
  type CATState,
  type CATQuestion,
  type CATSkill,
} from '@/lib/cat'
import { useAuthStore } from '@/stores/auth.store'
import { profileApi } from '@/api/profile'
import { updateLocalProfile, saveTestResult } from '@/lib/userStorage'
import { getSession } from '@/lib/localAuth'
import { bandToCefr, generateLearningPath } from '@/lib/learningPath'

const TOTAL_QUESTIONS = 20

const SKILL_ICONS: Record<CATSkill, typeof BookOpen> = {
  vocabulary: Languages,
  grammar: BookOpen,
  reading: BookOpen,
  listening: Headphones,
  writing: PenLine,
}

const SKILL_LABELS: Record<CATSkill, string> = {
  vocabulary: 'Vocabulary',
  grammar: 'Grammar',
  reading: 'Reading',
  listening: 'Listening',
  writing: 'Writing',
}

const levelMap: Record<string, number> = {
  A1: 2.0, A2: 3.0, B1: 4.5, B2: 5.5, C1: 7.0, C2: 8.5,
}

export function Placement() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [state, setState] = useState<CATState>(() => initCATState())
  const [question, setQuestion] = useState<CATQuestion | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [finished, setFinished] = useState(false)
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load the adaptive test on mount
  useEffect(() => {
    let cancelled = false
    buildAdaptiveTest(TOTAL_QUESTIONS)
      .then((questions) => {
        if (cancelled) return
        setState((prev) => ({ ...prev, questionQueue: questions }))
        setQuestion(questions[0] || null)
        setLoading(false)
      })
      .catch((err) => {
        if (cancelled) return
        console.error('Failed to load placement test:', err)
        setError('Failed to load test questions. Please refresh the page.')
        setLoading(false)
      })
    return () => { cancelled = true }
  }, [])

  const handleAnswer = (answer: string) => {
    if (!question || showResult) return
    setSelected(answer)
    setShowResult(true)
    const correct = answer === question.answer
    const newState = recordAnswer(state, question, correct)
    setState(newState)
  }

  const handleNext = () => {
    if (isComplete(state, TOTAL_QUESTIONS)) {
      setFinished(true)
      return
    }
    const nextQ = state.questionQueue[state.queueIndex] || null
    setQuestion(nextQ)
    setSelected(null)
    setShowResult(false)
  }

  const handleFinish = async () => {
    setSaving(true)
    const band = getEstimatedBand(state)
    const skillBreakdown = getSkillBreakdown(state)
    const skillBands: Record<string, number> = {}
    for (const s of skillBreakdown) {
      skillBands[s.skill.toLowerCase()] = levelMap[s.level] || 3
    }

    const bandScore = levelMap[band] || 4.5

    // Save to local storage
    const localSession = getSession()
    if (localSession) {
      updateLocalProfile(localSession.userId, {
        current_band: bandScore,
        skill_bands: skillBands,
        onboarded: true,
      })
      saveTestResult(localSession.userId, {
        id: `test-${Date.now()}`,
        examType: 'PLACEMENT',
        section: 'CAT',
        score: state.answeredCorrect,
        total: state.answeredTotal,
        band: bandScore,
        takenAt: new Date().toISOString(),
        details: { estimatedLevel: band, skillBreakdown },
      })
    }

    // Also try API (non-fatal)
    try {
      await profileApi.update({
        current_band: bandScore,
        skill_bands: skillBands,
      } as any)
    } catch {
      // API may be unavailable
    } finally {
      setSaving(false)
    }

    navigate('/app')
  }

  const handleRestart = async () => {
    setLoading(true)
    const fresh = initCATState()
    const questions = await buildAdaptiveTest(TOTAL_QUESTIONS)
    fresh.questionQueue = questions
    setState(fresh)
    setQuestion(questions[0] || null)
    setFinished(false)
    setSelected(null)
    setShowResult(false)
    setLoading(false)
  }

  // ── Loading screen ──
  if (loading) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold font-heading flex items-center justify-center gap-2">
            <Brain className="h-6 w-6 text-accent" /> Placement Test
          </h1>
        </div>
        <Card>
          <CardContent className="py-12 text-center">
            <Loader2 className="h-8 w-8 text-accent animate-spin mx-auto mb-3" />
            <p className="text-sm text-gray-400">Loading 20 adaptive questions across 5 skills…</p>
            <p className="text-xs text-gray-500 mt-1">Vocabulary · Grammar · Reading · Listening · Writing</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ── Error screen ──
  if (error) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-sm text-error mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ── Results screen ──
  if (finished) {
    const band = getEstimatedBand(state)
    const breakdown = getSkillBreakdown(state)
    const accuracy = state.answeredTotal > 0
      ? Math.round((state.answeredCorrect / state.answeredTotal) * 100)
      : 0

    const skillBands: Record<string, number> = {}
    const skillLevelMap: Record<string, number> = { A1: 1, A2: 2, B1: 3, B2: 4, C1: 5, C2: 6 }
    for (const s of breakdown) {
      skillBands[s.skill.toLowerCase()] = skillLevelMap[s.level] || 3
    }

    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold font-heading">🎯 Placement Test Results</h1>
          <p className="text-sm text-gray-400 mt-1">Your estimated English level</p>
        </div>

        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-6xl font-bold text-accent">{band}</p>
            <p className="text-sm text-gray-400 mt-2">
              {accuracy}% accuracy · {state.answeredCorrect}/{state.answeredTotal} correct
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Skill Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {breakdown.map((s) => {
              const skill = s.skill.toLowerCase() as CATSkill
              const Icon = SKILL_ICONS[skill] || BookOpen
              return (
                <div key={s.skill} className="flex items-center justify-between">
                  <span className="text-sm text-gray-300 flex items-center gap-2">
                    <Icon className="h-4 w-4 text-gray-400" />
                    {s.skill}
                  </span>
                  <div className="flex items-center gap-3">
                    <div className="w-32 h-2 rounded-full bg-surface-dark overflow-hidden">
                      <div
                        className="h-full rounded-full bg-accent"
                        style={{ width: `${s.accuracy}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-accent w-8 text-right">{s.level}</span>
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* Learning Path Summary */}
        {(() => {
          const targetExam = user?.target_exam || 'IELTS'
          const targetScore = user?.target_score || 6.5
          const targetCefr = bandToCefr(targetScore, targetExam)
          const path = generateLearningPath(band, targetCefr, targetExam, skillBands)

          return (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">📊 Your Learning Path</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-lg bg-black/20 p-3">
                  <p className="text-sm text-gray-300">
                    <span className="font-medium text-accent">{path.gapAnalysis.recommendation}</span>
                  </p>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Current: <span className="font-bold text-white">{band}</span></span>
                  <span className="text-gray-400">Target: <span className="font-bold text-accent">{targetCefr}</span></span>
                  <span className="text-gray-400">~{path.totalWeeks} weeks</span>
                </div>

                <div className="space-y-2">
                  {path.phases.map((phase, i) => (
                    <div key={phase.id} className="flex items-center gap-3 rounded-lg border border-border p-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/20 text-accent text-sm font-bold">
                        {i + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{phase.name}</p>
                        <p className="text-xs text-gray-400">
                          → {phase.targetBand} · {phase.weeksEstimated} weeks · {phase.focusSkills.join(', ')}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {path.gapAnalysis.skillsToImprove.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-400 mb-1">Priority skills to improve:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {path.gapAnalysis.skillsToImprove.map((s) => (
                        <span key={s.skill} className="px-2 py-0.5 rounded text-xs bg-warning/20 text-warning">
                          {s.skill} ({s.current}→{s.target})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })()}

        <div className="flex gap-3">
          <Button variant="outline" className="flex-1" onClick={handleRestart}>
            <RotateCcw className="h-4 w-4 mr-2" /> Retake Test
          </Button>
          <Button className="flex-1" onClick={handleFinish} disabled={saving}>
            {saving ? 'Saving…' : <>Start Learning <ArrowRight className="h-4 w-4 ml-2" /></>}
          </Button>
        </div>
      </div>
    )
  }

  // ── Question screen ──
  const progress = (state.answeredTotal / TOTAL_QUESTIONS) * 100
  const currentSkill = question?.skill || 'vocabulary'
  const SkillIcon = SKILL_ICONS[currentSkill] || BookOpen

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold font-heading flex items-center justify-center gap-2">
          <Brain className="h-6 w-6 text-accent" /> Placement Test
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Question {state.answeredTotal + 1} of {TOTAL_QUESTIONS} · Level: {state.currentLevel}
        </p>
      </div>

      {/* Progress bar */}
      <div className="h-2 rounded-full bg-surface-dark overflow-hidden">
        <div
          className="h-full rounded-full bg-accent transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Skill indicator */}
      <div className="flex items-center justify-center gap-2">
        <span className="px-3 py-1 rounded-full text-xs font-medium bg-accent/20 text-accent flex items-center gap-1.5">
          <SkillIcon className="h-3.5 w-3.5" />
          {SKILL_LABELS[currentSkill]}
        </span>
      </div>

      {question && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base whitespace-pre-line">{question.question}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Context (passage excerpt, transcript, etc.) */}
            {question.context && (
              <div className="rounded-lg bg-black/20 p-3 max-h-48 overflow-y-auto">
                <p className="text-xs text-gray-400 whitespace-pre-line">{question.context}</p>
              </div>
            )}

            {question.options.map((opt) => {
              const isCorrect = opt === question.answer
              const isSelected = opt === selected
              let className = 'border-border hover:border-accent'
              if (showResult && isCorrect) className = 'border-success bg-success/10'
              else if (showResult && isSelected && !isCorrect) className = 'border-error bg-error/10'
              else if (showResult) className = 'border-border opacity-50'

              return (
                <button
                  key={opt}
                  onClick={() => handleAnswer(opt)}
                  disabled={showResult}
                  className={`w-full text-left px-4 py-3 rounded-lg border-2 transition-all ${className}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm">{opt}</span>
                    {showResult && isCorrect && <CheckCircle2 className="h-4 w-4 text-success" />}
                    {showResult && isSelected && !isCorrect && <XCircle className="h-4 w-4 text-error" />}
                  </div>
                </button>
              )
            })}

            {showResult && (
              <Button className="w-full mt-4" onClick={handleNext}>
                {state.answeredTotal >= TOTAL_QUESTIONS
                  ? 'See Results →'
                  : 'Next Question →'}
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      <p className="text-xs text-gray-500 text-center">
        The test adapts to your level — questions get harder or easier based on your answers.
      </p>
    </div>
  )
}
