/**
 * Progress Tracker
 *
 * Central hub for recording learning activities.  When a user is logged
 * in locally, all data is saved to localStorage via userStorage.  When
 * the API is available, data is also synced to the backend.
 */

import {
  addXp,
  updateStreak,
  recordDailyActivity,
  saveSession,
  saveTestResult,
  saveError,
  type StudySession,
  type TestResult,
  type ErrorEntry,
} from './userStorage'
import { calculateXp, type Quality } from './srs'

// ── Session Tracking ─────────────────────────────────────────────────

const activeSessions = new Map<string, { type: string; startTime: number; xp: number; items: number; correct: number }>()

export function startSession(userId: string, type: StudySession['type']) {
  activeSessions.set(userId, {
    type,
    startTime: Date.now(),
    xp: 0,
    items: 0,
    correct: 0,
  })
}

export function recordSessionItem(userId: string, correct: boolean) {
  const session = activeSessions.get(userId)
  if (!session) return
  session.items++
  if (correct) session.correct++
  const xp = calculateXp(correct ? { type: 'exercise_correct' } : { type: 'exercise_wrong' })
  session.xp += xp
  addXp(userId, xp)
}

export function endSession(userId: string): StudySession | null {
  const session = activeSessions.get(userId)
  if (!session) return null

  const durationSec = Math.round((Date.now() - session.startTime) / 1000)
  const studyMinutes = Math.max(1, Math.round(durationSec / 60))

  const studySession: StudySession = {
    id: `session-${Date.now()}`,
    type: session.type,
    startedAt: new Date(session.startTime).toISOString(),
    endedAt: new Date().toISOString(),
    durationSec,
    xpEarned: session.xp,
    itemsStudied: session.items,
    itemsCorrect: session.correct,
  }

  saveSession(userId, studySession)
  recordDailyActivity(userId, {
    studyMinutes,
    xpEarned: session.xp,
    itemsStudied: session.items,
  })
  updateStreak(userId)

  activeSessions.delete(userId)
  return studySession
}

// ── SRS Card Review ─────────────────────────────────────────────────

export function recordSrsReview(userId: string, _cardId: string, quality: Quality) {
  const xp = calculateXp({ type: 'srs_review', quality })
  addXp(userId, xp)
  recordDailyActivity(userId, { xpEarned: xp, itemsStudied: 1 })

  const session = activeSessions.get(userId)
  if (session) {
    session.items++
    if (quality >= 3) session.correct++
    session.xp += xp
  }
}

// ── Test Results ────────────────────────────────────────────────────

export function recordTestResult(
  userId: string,
  result: Omit<TestResult, 'id' | 'takenAt'>
) {
  const full: TestResult = {
    ...result,
    id: `test-${Date.now()}`,
    takenAt: new Date().toISOString(),
  }
  saveTestResult(userId, full)

  // Award XP for completing a test
  const xp = calculateXp({ type: 'mock_test' })
  addXp(userId, xp)
  recordDailyActivity(userId, { xpEarned: xp, itemsStudied: result.total })
  updateStreak(userId)

  return full
}

// ── Writing Feedback ────────────────────────────────────────────────

export function recordWritingSubmission(
  userId: string,
  submission: {
    taskPrompt: string
    essay: string
    feedback: any
    bandEstimate: number | null
  }
) {
  const xp = calculateXp({ type: 'writing_feedback' })
  addXp(userId, xp)
  recordDailyActivity(userId, { xpEarned: xp, itemsStudied: 1 })

  // Also save to writing submissions
  import('./userStorage').then(({ saveWritingSubmission }) => {
    saveWritingSubmission(userId, {
      id: `writing-${Date.now()}`,
      taskPrompt: submission.taskPrompt,
      essay: submission.essay,
      wordCount: submission.essay.split(/\s+/).filter(Boolean).length,
      feedback: submission.feedback,
      bandEstimate: submission.bandEstimate,
      createdAt: new Date().toISOString(),
    })
  })
}

// ── Error Journal ───────────────────────────────────────────────────

export function recordError(
  userId: string,
  error: Omit<ErrorEntry, 'id' | 'createdAt' | 'reviewed'>
) {
  const full: ErrorEntry = {
    ...error,
    id: `error-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
    reviewed: false,
    createdAt: new Date().toISOString(),
  }
  saveError(userId, full)
  return full
}

// ── Daily Goal ──────────────────────────────────────────────────────

export function checkDailyGoal(userId: string, targetMinutes: number): boolean {
  import('./userStorage').then(({ getDailyActivity }) => {
    const today = new Date().toISOString().split('T')[0]
    const activity = getDailyActivity(userId, 1)
    if (activity[today] >= targetMinutes) {
      const xp = calculateXp({ type: 'daily_goal' })
      addXp(userId, xp)
    }
  })
  return false
}
