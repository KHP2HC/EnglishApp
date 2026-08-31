import { differenceInDays, addDays, format } from 'date-fns'
import type { ExamType, CEFRLevel } from './supabase'

// ── Types ────────────────────────────────────────────────────────────

export interface UserProfile {
  target_exam: ExamType
  target_score: number
  current_band: number
  skill_bands: Record<string, number>
  exam_date: string
  free_time: Record<string, number>
}

export interface DailyTask {
  type: string
  minutes: number
  label: string
}

export type DailyTasks = Record<string, DailyTask[]>

// ── Skill Allocation per Exam Type ───────────────────────────────────

const BASE_ALLOCATION: Record<ExamType, Record<string, number>> = {
  TOEIC: { vocabulary: 0.35, grammar: 0.25, listening: 0.30, reading: 0.10 },
  IELTS: { vocabulary: 0.25, grammar: 0.20, listening: 0.20, reading: 0.20, writing: 0.15 },
  TOEFL: { vocabulary: 0.20, grammar: 0.20, listening: 0.20, reading: 0.20, writing: 0.10, speaking: 0.10 },
  VSTEP: { vocabulary: 0.30, grammar: 0.20, listening: 0.20, reading: 0.20, writing: 0.10 },
}

const SKILL_LABELS: Record<string, string> = {
  vocabulary: 'SRS Vocabulary',
  grammar: 'Grammar Practice',
  listening: 'Listening Exercise',
  reading: 'Reading Practice',
  writing: 'Writing Task',
  speaking: 'Speaking Practice',
  mock: 'Mock Test',
}

// ── CEFR ↔ Score Conversion ──────────────────────────────────────────

export function cefrToScore(level: CEFRLevel, exam: ExamType): number {
  const map: Record<CEFRLevel, number> = { A1: 1, A2: 2, B1: 3, B2: 4, C1: 5, C2: 6 }
  const band = map[level]
  if (exam === 'TOEIC') {
    return Math.round([0, 250, 400, 550, 785, 945, 990][band] || 500)
  }
  if (exam === 'IELTS') {
    return [0, 2, 3.5, 4.5, 5.5, 7, 8.5][band] || 5
  }
  if (exam === 'TOEFL') {
    return Math.round([0, 30, 50, 70, 90, 105, 115][band] || 70)
  }
  return band
}

export function scoreToCefr(score: number, exam: ExamType): CEFRLevel {
  if (exam === 'TOEIC') {
    if (score >= 945) return 'C1'
    if (score >= 785) return 'B2'
    if (score >= 550) return 'B1'
    if (score >= 400) return 'A2'
    return 'A1'
  }
  if (exam === 'IELTS') {
    if (score >= 7) return 'C1'
    if (score >= 5.5) return 'B2'
    if (score >= 4.5) return 'B1'
    if (score >= 3.5) return 'A2'
    return 'A1'
  }
  if (exam === 'TOEFL') {
    if (score >= 105) return 'C1'
    if (score >= 90) return 'B2'
    if (score >= 70) return 'B1'
    if (score >= 50) return 'A2'
    return 'A1'
  }
  return 'B1'
}

// ── Plan Generator ───────────────────────────────────────────────────

export function generateWeeklyPlan(profile: UserProfile): DailyTasks {
  const daysLeft = differenceInDays(new Date(profile.exam_date), new Date())
  const allocation = { ...BASE_ALLOCATION[profile.target_exam] }

  // Adjust: boost weakest skill by 10%, reduce strongest
  const skillEntries = Object.entries(allocation)
  if (skillEntries.length >= 2) {
    const sorted = [...skillEntries].sort((a, b) => a[1] - b[1])
    const weakest = sorted[0][0]
    const strongest = sorted[sorted.length - 1][0]
    allocation[weakest] += 0.05
    allocation[strongest] -= 0.05
  }

  // Add mock tests in final 4 weeks
  if (daysLeft <= 28) {
    allocation.mock = 0.10
    // Reduce others proportionally
    const others = Object.keys(allocation).filter((k) => k !== 'mock')
    const factor = 0.9
    others.forEach((k) => (allocation[k] *= factor))
  }

  const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
  const plan: DailyTasks = {}
  const weekStart = new Date()

  for (const day of days) {
    const minutes = profile.free_time[day] || 60
    if (minutes <= 0) {
      plan[day] = []
      continue
    }

    const tasks: DailyTask[] = []
    for (const [skill, weight] of Object.entries(allocation)) {
      const allocated = Math.max(5, Math.round(minutes * weight))
      tasks.push({
        type: skill,
        minutes: allocated,
        label: SKILL_LABELS[skill] || skill,
      })
    }

    // Add mock test on Saturday if in final 4 weeks
    if (day === 'sat' && daysLeft <= 28 && allocation.mock) {
      tasks.push({
        type: 'mock',
        minutes: Math.max(30, Math.round(minutes * 0.3)),
        label: 'Full Mock Test',
      })
    }

    plan[day] = tasks
  }

  return plan
}

export function getTodayTasks(plan: DailyTasks): DailyTask[] {
  const today = format(new Date(), 'EEE').toLowerCase().slice(0, 3)
  return plan[today] || []
}

export function getWeekTotalMinutes(plan: DailyTasks): number {
  return Object.values(plan).reduce(
    (sum, tasks) => sum + tasks.reduce((s, t) => s + t.minutes, 0),
    0
  )
}
