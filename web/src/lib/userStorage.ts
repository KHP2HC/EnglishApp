/**
 * Per-User Local Storage
 *
 * Stores all learning data for a local user in localStorage, keyed by
 * user ID.  This includes profile, XP, streaks, SRS progress, test
 * results, error journal, and daily activity.
 */

import type { Profile, ExamType, CEFRLevel } from './supabase'

// ── Storage keys ─────────────────────────────────────────────────────

const PREFIX = 'ec_user_'

function userKey(userId: string, key: string) {
  return `${PREFIX}${userId}_${key}`
}

// ── Profile ──────────────────────────────────────────────────────────

export function loadLocalProfile(userId: string, name: string, email: string): Profile {
  const raw = localStorage.getItem(userKey(userId, 'profile'))
  if (raw) {
    try {
      return JSON.parse(raw)
    } catch { /* fall through */ }
  }

  // Create default profile
  const profile: Profile = {
    id: userId,
    name,
    avatar_emoji: '🧑',
    target_exam: 'IELTS',
    target_score: 6.5,
    current_band: 4.5,
    skill_bands: {},
    exam_date: new Date(Date.now() + 90 * 86400000).toISOString().split('T')[0],
    free_time: { mon: 60, tue: 60, wed: 60, thu: 60, fri: 60, sat: 120, sun: 120 },
    session_time: 'MORNING',
    streak_days: 0,
    total_xp: 0,
    last_active: null,
    onboarded: false,
    created_at: new Date().toISOString(),
  }

  saveLocalProfile(userId, profile)
  return profile
}

export function saveLocalProfile(userId: string, profile: Profile) {
  localStorage.setItem(userKey(userId, 'profile'), JSON.stringify(profile))
}

export function updateLocalProfile(userId: string, updates: Partial<Profile>): Profile {
  const existing = loadLocalProfile(userId, '', '')
  const updated = { ...existing, ...updates }
  saveLocalProfile(userId, updated)
  return updated
}

// ── XP & Streak ─────────────────────────────────────────────────────

export function addXp(userId: string, xp: number): number {
  const profile = loadLocalProfile(userId, '', '')
  const newTotal = (profile.total_xp || 0) + xp
  updateLocalProfile(userId, { total_xp: newTotal })
  return newTotal
}

export function updateStreak(userId: string): { streak: number; broke: boolean } {
  const profile = loadLocalProfile(userId, '', '')
  const today = new Date().toISOString().split('T')[0]
  const lastActive = profile.last_active?.split('T')[0]

  if (lastActive === today) {
    return { streak: profile.streak_days || 0, broke: false }
  }

  let newStreak = 1
  let broke = false

  if (lastActive) {
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0]
    if (lastActive === yesterday) {
      newStreak = (profile.streak_days || 0) + 1
    } else {
      broke = (profile.streak_days || 0) > 0
    }
  }

  updateLocalProfile(userId, {
    streak_days: newStreak,
    last_active: new Date().toISOString(),
  })

  return { streak: newStreak, broke }
}

// ── Daily Activity (for heatmap) ─────────────────────────────────────

export interface DailyActivity {
  date: string // yyyy-MM-dd
  studyMinutes: number
  xpEarned: number
  itemsStudied: number
}

export function recordDailyActivity(userId: string, entry: Partial<DailyActivity>) {
  const key = userKey(userId, 'daily_activity')
  const all: Record<string, DailyActivity> = (() => {
    try { return JSON.parse(localStorage.getItem(key) || '{}') } catch { return {} }
  })()

  const today = new Date().toISOString().split('T')[0]
  const existing = all[today] || { date: today, studyMinutes: 0, xpEarned: 0, itemsStudied: 0 }

  all[today] = {
    date: today,
    studyMinutes: existing.studyMinutes + (entry.studyMinutes || 0),
    xpEarned: existing.xpEarned + (entry.xpEarned || 0),
    itemsStudied: existing.itemsStudied + (entry.itemsStudied || 0),
  }

  localStorage.setItem(key, JSON.stringify(all))
}

export function getDailyActivity(userId: string, days = 365): Record<string, number> {
  const key = userKey(userId, 'daily_activity')
  try {
    const all: Record<string, DailyActivity> = JSON.parse(localStorage.getItem(key) || '{}')
    const result: Record<string, number> = {}
    for (let i = 0; i < days; i++) {
      const d = new Date(Date.now() - i * 86400000).toISOString().split('T')[0]
      result[d] = all[d]?.studyMinutes || 0
    }
    return result
  } catch {
    return {}
  }
}

// ── Study Sessions ───────────────────────────────────────────────────

export interface StudySession {
  id: string
  type: string // VOCABULARY | GRAMMAR | LISTENING | READING | WRITING | SPEAKING | MOCK
  startedAt: string
  endedAt: string | null
  durationSec: number
  xpEarned: number
  itemsStudied: number
  itemsCorrect: number
}

export function saveSession(userId: string, session: StudySession) {
  const key = userKey(userId, 'sessions')
  const all: StudySession[] = (() => {
    try { return JSON.parse(localStorage.getItem(key) || '[]') } catch { return [] }
  })()
  all.unshift(session)
  // Keep last 200 sessions
  localStorage.setItem(key, JSON.stringify(all.slice(0, 200)))
}

export function getSessions(userId: string): StudySession[] {
  const key = userKey(userId, 'sessions')
  try {
    return JSON.parse(localStorage.getItem(key) || '[]')
  } catch {
    return []
  }
}

// ── Test Results ────────────────────────────────────────────────────

export interface TestResult {
  id: string
  examType: string
  section: string
  score: number
  total: number
  band: number | null
  takenAt: string
  details?: Record<string, any>
}

export function saveTestResult(userId: string, result: TestResult) {
  const key = userKey(userId, 'test_results')
  const all: TestResult[] = (() => {
    try { return JSON.parse(localStorage.getItem(key) || '[]') } catch { return [] }
  })()
  all.unshift(result)
  localStorage.setItem(key, JSON.stringify(all.slice(0, 100)))
}

export function getTestResults(userId: string): TestResult[] {
  const key = userKey(userId, 'test_results')
  try {
    return JSON.parse(localStorage.getItem(key) || '[]')
  } catch {
    return []
  }
}

// ── Error Journal ───────────────────────────────────────────────────

export interface ErrorEntry {
  id: string
  skill: string
  category: string
  question: string
  userAnswer: string
  correctAnswer: string
  reviewed: boolean
  createdAt: string
}

export function saveError(userId: string, entry: ErrorEntry) {
  const key = userKey(userId, 'error_journal')
  const all: ErrorEntry[] = (() => {
    try { return JSON.parse(localStorage.getItem(key) || '[]') } catch { return [] }
  })()
  all.unshift(entry)
  localStorage.setItem(key, JSON.stringify(all.slice(0, 500)))
}

export function getErrors(userId: string): ErrorEntry[] {
  const key = userKey(userId, 'error_journal')
  try {
    return JSON.parse(localStorage.getItem(key) || '[]')
  } catch {
    return []
  }
}

// ── SRS Progress (local) ─────────────────────────────────────────────

export interface LocalSRSState {
  cardId: string
  intervalDays: number
  easiness: number
  repetitions: number
  nextReview: string
  lastQuality: number | null
  timesSeen: number
  timesCorrect: number
}

export function getSRSState(userId: string): Record<string, LocalSRSState> {
  const key = userKey(userId, 'srs_state')
  try {
    return JSON.parse(localStorage.getItem(key) || '{}')
  } catch {
    return {}
  }
}

export function updateSRSState(userId: string, cardId: string, state: LocalSRSState) {
  const all = getSRSState(userId)
  all[cardId] = state
  localStorage.setItem(userKey(userId, 'srs_state'), JSON.stringify(all))
}

export function getDueCards(userId: string): string[] {
  const all = getSRSState(userId)
  const today = new Date().toISOString().split('T')[0]
  return Object.entries(all)
    .filter(([, s]) => s.nextReview <= today)
    .map(([cardId]) => cardId)
}

// ── Writing Submissions ─────────────────────────────────────────────

export interface LocalWritingSubmission {
  id: string
  taskPrompt: string
  essay: string
  wordCount: number
  feedback: any | null
  bandEstimate: number | null
  createdAt: string
}

export function saveWritingSubmission(userId: string, sub: LocalWritingSubmission) {
  const key = userKey(userId, 'writing_submissions')
  const all: LocalWritingSubmission[] = (() => {
    try { return JSON.parse(localStorage.getItem(key) || '[]') } catch { return [] }
  })()
  all.unshift(sub)
  localStorage.setItem(key, JSON.stringify(all.slice(0, 50)))
}

export function getWritingSubmissions(userId: string): LocalWritingSubmission[] {
  const key = userKey(userId, 'writing_submissions')
  try {
    return JSON.parse(localStorage.getItem(key) || '[]')
  } catch {
    return []
  }
}

// ── Stats Summary ───────────────────────────────────────────────────

export function getLocalStats(userId: string) {
  const sessions = getSessions(userId)
  const testResults = getTestResults(userId)
  const errors = getErrors(userId)
  const srsState = getSRSState(userId)
  const activity = getDailyActivity(userId, 365)

  const totalStudyMinutes = Object.values(activity).reduce((a, b) => a + b, 0)
  const wordsLearned = Object.values(srsState).filter((s) => s.timesCorrect >= 3).length
  const totalXp = sessions.reduce((sum, s) => sum + s.xpEarned, 0)
  const sessionCount = sessions.length
  const testCount = testResults.length

  // XP this week
  const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().split('T')[0]
  const xpThisWeek = sessions
    .filter((s) => s.startedAt.split('T')[0] >= weekAgo)
    .reduce((sum, s) => sum + s.xpEarned, 0)

  return {
    words_learned: wordsLearned,
    total_xp: totalXp,
    total_study_minutes: totalStudyMinutes,
    session_count: sessionCount,
    test_count: testCount,
    error_count: errors.length,
    xp_this_week: xpThisWeek,
  }
}
