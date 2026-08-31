import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/stores/auth.store'
import type { ExamType, CEFRLevel } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Card } from '@/components/ui/card'
import { daysUntil } from '@/lib/utils'

const EMOJIS = ['🧑', '👩', '👨', '🧑‍🎓', '👩‍🎓', '👨‍🎓', '🧑‍💼', '👩‍💼', '👨‍💼', '🌟', '🔥', '💎', '🎯', '🏆', '🚀', '📚', '🧠', '💡', '✨', '🌈']

const EXAM_SCORES: Record<ExamType, { min: number; max: number; step: number; default: number }> = {
  TOEIC: { min: 10, max: 990, step: 5, default: 600 },
  IELTS: { min: 1, max: 9, step: 0.5, default: 6.5 },
  TOEFL: { min: 0, max: 120, step: 1, default: 80 },
  VSTEP: { min: 1, max: 6, step: 1, default: 3 },
}

const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] as const
const SLOTS = ['morning', 'afternoon', 'evening'] as const

export function Onboarding() {
  const navigate = useNavigate()
  const { user, refreshProfile } = useAuthStore()
  const [step, setStep] = useState(1)
  const [name, setName] = useState(user?.name || '')
  const [avatar, setAvatar] = useState(user?.avatar_emoji || '🧑')
  const [exam, setExam] = useState<ExamType>('IELTS')
  const [score, setScore] = useState(6.5)
  const [examDate, setExamDate] = useState(() => {
    const d = new Date()
    d.setDate(d.getDate() + 90)
    return d.toISOString().split('T')[0]
  })
  const [freeTime, setFreeTime] = useState<Record<string, Record<string, number>>>({
    mon: { morning: 30, afternoon: 0, evening: 30 },
    tue: { morning: 30, afternoon: 0, evening: 30 },
    wed: { morning: 30, afternoon: 0, evening: 30 },
    thu: { morning: 30, afternoon: 0, evening: 30 },
    fri: { morning: 30, afternoon: 0, evening: 30 },
    sat: { morning: 60, afternoon: 60, evening: 0 },
    sun: { morning: 60, afternoon: 60, evening: 0 },
  })

  const totalMinutes = Object.values(freeTime).reduce(
    (sum, day) => sum + Object.values(day).reduce((s, v) => s + v, 0),
    0
  )

  const handleExamChange = (e: ExamType) => {
    setExam(e)
    setScore(EXAM_SCORES[e].default)
  }

  const finish = async (skipPlacement: boolean) => {
    if (!user) return
    const flatFreeTime: Record<string, number> = {}
    for (const day of DAYS) {
      flatFreeTime[day] = Object.values(freeTime[day]).reduce((s, v) => s + v, 0)
    }

    await supabase
      .from('profiles')
      .update({
        name,
        avatar_emoji: avatar,
        target_exam: exam,
        target_score: score,
        exam_date: examDate,
        free_time: flatFreeTime,
        onboarded: true,
      })
      .eq('id', user.id)

    await refreshProfile()
    navigate(skipPlacement ? '/app' : '/app/placement')
  }

  const next = () => setStep((s) => Math.min(5, s + 1))

  return (
    <div className="min-h-screen bg-bg-dark text-white flex items-center justify-center px-4 py-8">
      <Card className="w-full max-w-2xl p-6 md:p-8">
        {/* Progress dots */}
        <div className="flex justify-center gap-2 mb-8">
          {[1, 2, 3, 4, 5].map((s) => (
            <div
              key={s}
              className={`h-2 w-2 rounded-full transition-colors ${
                s <= step ? 'bg-accent' : 'bg-gray-600'
              }`}
            />
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="s1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 className="text-2xl font-bold font-heading mb-2">Welcome! Let's set up your profile</h2>
              <p className="text-gray-400 mb-6">Step 1 of 5 — Profile</p>
              <div className="space-y-4">
                <div>
                  <Label>Your name</Label>
                  <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Enter your name" />
                </div>
                <div>
                  <Label>Pick an avatar</Label>
                  <div className="grid grid-cols-10 gap-2 mt-2">
                    {EMOJIS.map((e) => (
                      <button
                        key={e}
                        onClick={() => setAvatar(e)}
                        className={`text-2xl p-2 rounded-lg transition-colors ${
                          avatar === e ? 'bg-accent/20 ring-2 ring-accent' : 'hover:bg-white/5'
                        }`}
                      >
                        {e}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <Button className="w-full mt-6" onClick={next} disabled={!name}>Next →</Button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="s2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 className="text-2xl font-bold font-heading mb-2">Set your exam target</h2>
              <p className="text-gray-400 mb-6">Step 2 of 5 — Exam Target</p>
              <div className="space-y-4">
                <div>
                  <Label>Exam type</Label>
                  <div className="grid grid-cols-4 gap-2 mt-2">
                    {(['TOEIC', 'IELTS', 'TOEFL', 'VSTEP'] as ExamType[]).map((e) => (
                      <button
                        key={e}
                        onClick={() => handleExamChange(e)}
                        className={`p-3 rounded-xl border transition-colors text-sm font-medium ${
                          exam === e ? 'border-accent bg-accent/10 text-accent' : 'border-border text-gray-400'
                        }`}
                      >
                        {e}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <Label>Target score: <span className="text-accent font-bold">{score}</span></Label>
                  <Slider
                    value={[score]}
                    min={EXAM_SCORES[exam].min}
                    max={EXAM_SCORES[exam].max}
                    step={EXAM_SCORES[exam].step}
                    onValueChange={(v) => setScore(v[0])}
                    className="mt-3"
                  />
                </div>
              </div>
              <Button className="w-full mt-6" onClick={next}>Next →</Button>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div key="s3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 className="text-2xl font-bold font-heading mb-2">When is your exam?</h2>
              <p className="text-gray-400 mb-6">Step 3 of 5 — Exam Date</p>
              <div className="space-y-4">
                <div>
                  <Label>Exam date</Label>
                  <Input
                    type="date"
                    value={examDate}
                    min={new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0]}
                    onChange={(e) => setExamDate(e.target.value)}
                  />
                </div>
                {examDate && (
                  <div className="rounded-xl bg-accent/10 p-4 text-center">
                    <p className="text-3xl font-bold text-accent">{daysUntil(examDate)}</p>
                    <p className="text-sm text-gray-400">days to go</p>
                    {daysUntil(examDate) < 45 && (
                      <p className="text-xs text-warning mt-2">
                        ⚠️ That's a tight timeline! We'll focus on your highest-impact areas.
                      </p>
                    )}
                  </div>
                )}
              </div>
              <Button className="w-full mt-6" onClick={next}>Next →</Button>
            </motion.div>
          )}

          {step === 4 && (
            <motion.div key="s4" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 className="text-2xl font-bold font-heading mb-2">Weekly availability</h2>
              <p className="text-gray-400 mb-4">Step 4 of 5 — Free Time</p>
              <p className="text-sm text-accent mb-4">Total this week: {Math.floor(totalMinutes / 60)}h {totalMinutes % 60}m</p>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {DAYS.map((day) => (
                  <div key={day} className="flex items-center gap-2">
                    <span className="w-10 text-sm capitalize">{day}</span>
                    {SLOTS.map((slot) => (
                      <div key={slot} className="flex-1">
                        <Label className="text-xs capitalize">{slot}</Label>
                        <Input
                          type="number"
                          min={0}
                          max={120}
                          value={freeTime[day][slot]}
                          onChange={(e) =>
                            setFreeTime((prev) => ({
                              ...prev,
                              [day]: { ...prev[day], [slot]: parseInt(e.target.value) || 0 },
                            }))
                          }
                          className="h-8 text-sm"
                        />
                      </div>
                    ))}
                  </div>
                ))}
              </div>
              <Button className="w-full mt-6" onClick={next}>Next →</Button>
            </motion.div>
          )}

          {step === 5 && (
            <motion.div key="s5" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="text-center">
              <h2 className="text-2xl font-bold font-heading mb-2">Ready to start!</h2>
              <p className="text-gray-400 mb-6">Step 5 of 5 — Placement Test</p>
              <p className="text-sm mb-6">
                Take a 20-minute placement test to get your current English level,
                or skip if you already know your level.
              </p>
              <div className="space-y-3">
                <Button className="w-full" onClick={() => finish(false)}>
                  Take the 20-min placement test →
                </Button>
                <Button variant="outline" className="w-full" onClick={() => finish(true)}>
                  Skip — I know my level
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </div>
  )
}
