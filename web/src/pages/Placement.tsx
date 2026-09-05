import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CheckCircle2, XCircle, Brain, ArrowRight, RotateCcw } from 'lucide-react'
import {
  initCATState,
  recordAnswer,
  getQuestionForLevel,
  getEstimatedBand,
  getSkillBreakdown,
  isComplete,
  type CATState,
  type CATQuestion,
} from '@/lib/cat'
import { useAuthStore } from '@/stores/auth.store'
import { profileApi } from '@/api/profile'
import { updateLocalProfile, saveTestResult } from '@/lib/userStorage'
import { getSession } from '@/lib/localAuth'
import { bandToCefr, generateLearningPath } from '@/lib/learningPath'

const TOTAL_QUESTIONS = 20

export function Placement() {
  const navigate = useNavigate()
  const { user, refreshProfile } = useAuthStore()
  const [state, setState] = useState<CATState>(() => initCATState())
  const [question, setQuestion] = useState<CATQuestion | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [finished, setFinished] = useState(false)
  const [saving, setSaving] = useState(false)

  const loadQuestion = useCallback((s: CATState) => {
    const q = getQuestionForLevel(s.currentLevel)
    setQuestion(q)
    setSelected(null)
    setShowResult(false)
  }, [])

  useEffect(() => {
    loadQuestion(state)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

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
    loadQuestion(state)
  }

  const handleFinish = async () => {
    setSaving(true)
    const band = getEstimatedBand(state)
    const skillBreakdown = getSkillBreakdown(state)
    const skillBands: Record<string, number> = {}
    for (const s of skillBreakdown) {
      const levelMap: Record<string, number> = {
        A1: 1, A2: 2, B1: 3, B2: 4, C1: 5, C2: 6,
      }
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
      // Save as a test result
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

  const handleRestart = () => {
    const fresh = initCATState()
    setState(fresh)
    setFinished(false)
    loadQuestion(fresh)
  }

  // ── Results screen ──
  if (finished) {
    const band = getEstimatedBand(state)
    const breakdown = getSkillBreakdown(state)
    const accuracy = state.answeredTotal > 0
      ? Math.round((state.answeredCorrect / state.answeredTotal) * 100)
      : 0

    // Compute skill bands from breakdown for the learning path gap analysis
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
            {breakdown.map((s) => (
              <div key={s.skill} className="flex items-center justify-between">
                <span className="text-sm text-gray-300">{s.skill}</span>
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
            ))}
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

                {/* Phase overview */}
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

      {question && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{question.question}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
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

const levelMap: Record<string, number> = {
  A1: 2.0, A2: 3.0, B1: 4.5, B2: 5.5, C1: 7.0, C2: 8.5,
}
