/**
 * Learning Path Engine
 *
 * Designs a personalized learning path based on the user's current band
 * (from placement test) and their target band/score.
 *
 * The path is divided into phases, each with specific goals, focus areas,
 * and recommended activities.  Progress is tracked as the user completes
 * activities and improves their band.
 */

import type { ExamType, CEFRLevel } from './supabase'

// ── Types ────────────────────────────────────────────────────────────

export interface LearningPhase {
  id: string
  name: string
  description: string
  targetBand: CEFRLevel
  weeksEstimated: number
  focusSkills: string[]
  milestones: string[]
  weeklyGoals: {
    vocabularyCards: number
    grammarExercises: number
    listeningSessions: number
    readingPassages: number
    writingTasks: number
    speakingPractices: number
    mockTests: number
  }
}

export interface LearningPath {
  currentBand: CEFRLevel
  targetBand: CEFRLevel
  examType: ExamType
  totalWeeks: number
  phases: LearningPhase[]
  gapAnalysis: {
    levelGap: number
    skillsToImprove: { skill: string; current: number; target: number }[]
    recommendation: string
  }
}

// ── CEFR Level Helpers ───────────────────────────────────────────────

const LEVEL_ORDER: CEFRLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

function levelToNumber(level: CEFRLevel): number {
  return LEVEL_ORDER.indexOf(level) + 1
}

function numberToLevel(n: number): CEFRLevel {
  return LEVEL_ORDER[Math.min(Math.max(n - 1, 0), LEVEL_ORDER.length - 1)]
}

// ── Band → CEFR conversion ──────────────────────────────────────────

export function bandToCefr(band: number, exam: ExamType): CEFRLevel {
  if (exam === 'IELTS') {
    if (band >= 8.0) return 'C2'
    if (band >= 7.0) return 'C1'
    if (band >= 5.5) return 'B2'
    if (band >= 4.5) return 'B1'
    if (band >= 3.0) return 'A2'
    return 'A1'
  }
  if (exam === 'TOEIC') {
    if (band >= 945) return 'C1'
    if (band >= 785) return 'B2'
    if (band >= 550) return 'B1'
    if (band >= 400) return 'A2'
    return 'A1'
  }
  if (exam === 'TOEFL') {
    if (band >= 105) return 'C1'
    if (band >= 90) return 'B2'
    if (band >= 70) return 'B1'
    if (band >= 50) return 'A2'
    return 'A1'
  }
  // VSTEP
  if (band >= 5) return 'C1'
  if (band >= 4) return 'B2'
  if (band >= 3) return 'B1'
  if (band >= 2) return 'A2'
  return 'A1'
}

// ── Phase Definitions ────────────────────────────────────────────────

const PHASE_TEMPLATES: Record<number, Omit<LearningPhase, 'id' | 'targetBand'>> = {
  // A1 → A2: Foundation
  1: {
    name: 'Foundation',
    description: 'Build basic vocabulary and essential grammar. Focus on everyday English.',
    weeksEstimated: 4,
    focusSkills: ['vocabulary', 'grammar', 'listening'],
    milestones: [
      'Master 500 core vocabulary words',
      'Understand present, past, and future tenses',
      'Follow simple conversations at slow speed',
      'Introduce yourself and ask basic questions',
    ],
    weeklyGoals: {
      vocabularyCards: 70,
      grammarExercises: 14,
      listeningSessions: 5,
      readingPassages: 3,
      writingTasks: 1,
      speakingPractices: 3,
      mockTests: 0,
    },
  },
  // A2 → B1: Bridge
  2: {
    name: 'Bridge',
    description: 'Expand vocabulary and learn complex grammar. Start reading short articles.',
    weeksEstimated: 4,
    focusSkills: ['vocabulary', 'grammar', 'reading', 'listening'],
    milestones: [
      'Master 1,000+ vocabulary words',
      'Use conditionals and passive voice',
      'Understand main ideas in short talks',
      'Write simple paragraphs with connectors',
    ],
    weeklyGoals: {
      vocabularyCards: 84,
      grammarExercises: 14,
      listeningSessions: 5,
      readingPassages: 5,
      writingTasks: 2,
      speakingPractices: 3,
      mockTests: 0,
    },
  },
  // B1 → B2: Intermediate
  3: {
    name: 'Intermediate',
    description: 'Develop fluency in all skills. Start exam-specific practice.',
    weeksEstimated: 5,
    focusSkills: ['vocabulary', 'listening', 'reading', 'writing', 'grammar'],
    milestones: [
      'Master 2,000+ vocabulary words',
      'Follow extended conversations and lectures',
      'Read and summarize articles',
      'Write structured essays (150+ words)',
      'Score 50%+ on mock test sections',
    ],
    weeklyGoals: {
      vocabularyCards: 98,
      grammarExercises: 10,
      listeningSessions: 7,
      readingPassages: 7,
      writingTasks: 3,
      speakingPractices: 4,
      mockTests: 1,
    },
  },
  // B2 → C1: Advanced
  4: {
    name: 'Advanced',
    description: 'Refine accuracy and speed. Heavy exam practice and error analysis.',
    weeksEstimated: 5,
    focusSkills: ['writing', 'speaking', 'listening', 'reading', 'vocabulary'],
    milestones: [
      'Master 3,000+ vocabulary words',
      'Follow fast native speech and lectures',
      'Write well-structured essays (250+ words)',
      'Speak fluently on abstract topics',
      'Score 70%+ on full mock tests',
    ],
    weeklyGoals: {
      vocabularyCards: 70,
      grammarExercises: 7,
      listeningSessions: 7,
      readingPassages: 7,
      writingTasks: 4,
      speakingPractices: 5,
      mockTests: 2,
    },
  },
  // C1 → C2: Mastery
  5: {
    name: 'Mastery',
    description: 'Polish edge cases, idiomatic language, and exam strategy.',
    weeksEstimated: 4,
    focusSkills: ['speaking', 'writing', 'reading', 'listening'],
    milestones: [
      'Use idiomatic and nuanced language',
      'Understand implicit meaning in texts',
      'Write cohesive, sophisticated essays',
      'Speak with near-native fluency',
      'Score 85%+ on full mock tests',
    ],
    weeklyGoals: {
      vocabularyCards: 50,
      grammarExercises: 5,
      listeningSessions: 7,
      readingPassages: 7,
      writingTasks: 5,
      speakingPractices: 7,
      mockTests: 2,
    },
  },
}

// ── Path Generator ──────────────────────────────────────────────────

export function generateLearningPath(
  currentBand: CEFRLevel,
  targetBand: CEFRLevel,
  examType: ExamType,
  skillBands?: Record<string, number>
): LearningPath {
  const currentNum = levelToNumber(currentBand)
  const targetNum = levelToNumber(targetBand)
  const gap = Math.max(0, targetNum - currentNum)

  const phases: LearningPhase[] = []
  let totalWeeks = 0

  for (let i = 0; i < gap; i++) {
    const fromLevel = currentNum + i
    const toLevel = fromLevel + 1
    const template = PHASE_TEMPLATES[fromLevel] || PHASE_TEMPLATES[4] // fallback to Advanced

    phases.push({
      ...template,
      id: `phase-${i + 1}`,
      targetBand: numberToLevel(toLevel),
    })
    totalWeeks += template.weeksEstimated
  }

  // If no gap (already at or above target), create a maintenance phase
  if (phases.length === 0) {
    phases.push({
      ...PHASE_TEMPLATES[5],
      id: 'phase-1',
      targetBand: currentBand,
    })
    totalWeeks = PHASE_TEMPLATES[5].weeksEstimated
  }

  // Gap analysis
  const skillsToImprove: { skill: string; current: number; target: number }[] = []
  const skillNames = ['vocabulary', 'grammar', 'listening', 'reading', 'writing', 'speaking']
  for (const skill of skillNames) {
    const current = skillBands?.[skill] || currentNum
    const target = targetNum
    if (current < target) {
      skillsToImprove.push({ skill, current, target })
    }
  }

  // Sort by gap descending — biggest gaps first
  skillsToImprove.sort((a, b) => (b.target - b.current) - (a.target - a.current))

  let recommendation: string
  if (gap === 0) {
    recommendation = `You're already at ${currentBand} level. Focus on maintaining your skills and polishing exam technique.`
  } else if (gap === 1) {
    recommendation = `You need to improve from ${currentBand} to ${targetBand}. This is achievable in about ${totalWeeks} weeks with consistent practice.`
  } else if (gap === 2) {
    recommendation = `You need to improve from ${currentBand} to ${targetBand} — a 2-level jump. Plan for about ${totalWeeks} weeks. Focus on your weakest skills first: ${skillsToImprove.slice(0, 2).map((s) => s.skill).join(', ')}.`
  } else {
    recommendation = `You need to improve from ${currentBand} to ${targetBand} — a ${gap}-level jump. This is ambitious and will take about ${totalWeeks} weeks. Consider adjusting your target or exam date. Priority skills: ${skillsToImprove.slice(0, 3).map((s) => s.skill).join(', ')}.`
  }

  return {
    currentBand,
    targetBand,
    examType,
    totalWeeks,
    phases,
    gapAnalysis: {
      levelGap: gap,
      skillsToImprove,
      recommendation,
    },
  }
}

// ── Progress Tracking ───────────────────────────────────────────────

export function getPhaseProgress(
  path: LearningPath,
  currentBand: CEFRLevel
): { currentPhaseIndex: number; phasesCompleted: number; overallProgress: number } {
  const currentNum = levelToNumber(currentBand)
  const startNum = levelToNumber(path.currentBand)
  const targetNum = levelToNumber(path.targetBand)
  const totalGap = Math.max(1, targetNum - startNum)
  const completed = Math.max(0, currentNum - startNum)
  const currentPhaseIndex = Math.min(completed, path.phases.length - 1)
  const overallProgress = Math.min(100, (completed / totalGap) * 100)

  return {
    currentPhaseIndex,
    phasesCompleted: completed,
    overallProgress,
  }
}
