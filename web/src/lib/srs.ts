import { addDays } from 'date-fns'

// ── Types ────────────────────────────────────────────────────────────

export type Quality = 0 | 2 | 3 | 5

export interface SRSState {
  interval_days: number
  easiness: number
  repetitions: number
  next_review: string
  last_quality: number | null
  times_seen: number
  times_correct: number
}

// ── SM-2 Algorithm ───────────────────────────────────────────────────

export function sm2Update(
  state: SRSState,
  quality: Quality
): SRSState {
  let { interval_days: interval, easiness, repetitions } = state

  if (quality < 3) {
    repetitions = 0
    interval = 1
  } else {
    if (repetitions === 0) interval = 1
    else if (repetitions === 1) interval = 6
    else interval = Math.round(interval * easiness)
    repetitions += 1
  }

  easiness = Math.max(
    1.3,
    easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
  )

  return {
    interval_days: interval,
    easiness: Math.round(easiness * 100) / 100,
    repetitions,
    next_review: addDays(new Date(), interval).toISOString().split('T')[0],
    last_quality: quality,
    times_seen: state.times_seen + 1,
    times_correct: quality >= 3 ? state.times_correct + 1 : state.times_correct,
  }
}

// ── XP Calculation ────────────────────────────────────────────────────

export function calculateXp(
  action:
    | { type: 'srs_review'; quality: Quality }
    | { type: 'exercise_correct' }
    | { type: 'exercise_wrong' }
    | { type: 'mock_test' }
    | { type: 'writing_feedback' }
    | { type: 'daily_goal' }
    | { type: 'streak_bonus' }
): number {
  switch (action.type) {
    case 'srs_review':
      return 3 + (action.quality >= 3 ? 5 : 0)
    case 'exercise_correct':
      return 10
    case 'exercise_wrong':
      return 2
    case 'mock_test':
      return 50
    case 'writing_feedback':
      return 20
    case 'daily_goal':
      return 25
    case 'streak_bonus':
      return 100
  }
}

// ── Level System ─────────────────────────────────────────────────────

export interface LevelInfo {
  name: string
  emoji: string
  level: number
  xpInLevel: number
  xpForNext: number
}

const LEVELS = [
  { threshold: 0, name: 'A1 Newcomer', emoji: '🌱' },
  { threshold: 500, name: 'A2 Explorer', emoji: '🗺️' },
  { threshold: 1500, name: 'B1 Builder', emoji: '🏗️' },
  { threshold: 3000, name: 'B2 Achiever', emoji: '🎯' },
  { threshold: 5000, name: 'C1 Expert', emoji: '💡' },
  { threshold: 8000, name: 'C2 Master', emoji: '👑' },
  { threshold: 12000, name: 'Exam Ready', emoji: '🎓' },
]

export function getLevelInfo(totalXp: number): LevelInfo {
  for (let i = LEVELS.length - 1; i >= 0; i--) {
    if (totalXp >= LEVELS[i].threshold) {
      const next = LEVELS[i + 1]
      return {
        name: LEVELS[i].name,
        emoji: LEVELS[i].emoji,
        level: i + 1,
        xpInLevel: totalXp - LEVELS[i].threshold,
        xpForNext: next ? next.threshold - LEVELS[i].threshold : 1000,
      }
    }
  }
  return { name: LEVELS[0].name, emoji: LEVELS[0].emoji, level: 1, xpInLevel: 0, xpForNext: 500 }
}

// ── Streak Helpers ───────────────────────────────────────────────────

export function getStreakBadge(streak: number): string | null {
  if (streak >= 365) return '🏆'
  if (streak >= 100) return '👑'
  if (streak >= 30) return '💎'
  if (streak >= 7) return '🔥'
  return null
}
