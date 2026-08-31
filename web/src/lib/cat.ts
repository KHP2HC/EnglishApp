import type { CEFRLevel } from './supabase'

// ── CAT (Computer Adaptive Testing) Engine ───────────────────────────

export interface CATQuestion {
  id: string
  level: CEFRLevel
  skill: 'vocabulary' | 'grammar' | 'listening' | 'reading'
  question: string
  options: string[]
  answer: string
}

export interface CATState {
  currentLevel: CEFRLevel
  answeredCorrect: number
  answeredTotal: number
  history: { level: CEFRLevel; correct: boolean }[]
  skillScores: Record<string, { correct: number; total: number }>
}

const LEVEL_ORDER: CEFRLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

export function initCATState(): CATState {
  return {
    currentLevel: 'B1',
    answeredCorrect: 0,
    answeredTotal: 0,
    history: [],
    skillScores: {
      vocabulary: { correct: 0, total: 0 },
      grammar: { correct: 0, total: 0 },
      listening: { correct: 0, total: 0 },
      reading: { correct: 0, total: 0 },
    },
  }
}

function levelUp(level: CEFRLevel): CEFRLevel {
  const idx = LEVEL_ORDER.indexOf(level)
  return idx < LEVEL_ORDER.length - 1 ? LEVEL_ORDER[idx + 1] : level
}

function levelDown(level: CEFRLevel): CEFRLevel {
  const idx = LEVEL_ORDER.indexOf(level)
  return idx > 0 ? LEVEL_ORDER[idx - 1] : level
}

export function nextLevel(state: CATState): CEFRLevel {
  const lastFive = state.history.slice(-5)
  if (lastFive.length < 3) return state.currentLevel

  const recentAccuracy = lastFive.filter((h) => h.correct).length / lastFive.length
  if (recentAccuracy > 0.8) return levelUp(state.currentLevel)
  if (recentAccuracy < 0.4) return levelDown(state.currentLevel)
  return state.currentLevel
}

export function recordAnswer(
  state: CATState,
  question: CATQuestion,
  correct: boolean
): CATState {
  const newHistory = [...state.history, { level: question.level, correct }]
  const newSkillScores = { ...state.skillScores }
  const skill = question.skill
  newSkillScores[skill] = {
    correct: newSkillScores[skill].correct + (correct ? 1 : 0),
    total: newSkillScores[skill].total + 1,
  }

  const newState: CATState = {
    ...state,
    answeredTotal: state.answeredTotal + 1,
    answeredCorrect: state.answeredCorrect + (correct ? 1 : 0),
    history: newHistory,
    skillScores: newSkillScores,
  }

  newState.currentLevel = nextLevel(newState)
  return newState
}

export function getEstimatedBand(state: CATState): CEFRLevel {
  return state.currentLevel
}

export function getSkillBreakdown(state: CATState) {
  return Object.entries(state.skillScores).map(([skill, scores]) => ({
    skill: skill.charAt(0).toUpperCase() + skill.slice(1),
    accuracy: scores.total > 0 ? (scores.correct / scores.total) * 100 : 0,
    level: estimateSkillLevel(scores.correct, scores.total),
  }))
}

function estimateSkillLevel(correct: number, total: number): CEFRLevel {
  if (total === 0) return 'B1'
  const acc = correct / total
  if (acc >= 0.8) return 'C1'
  if (acc >= 0.6) return 'B2'
  if (acc >= 0.4) return 'B1'
  if (acc >= 0.2) return 'A2'
  return 'A1'
}

export function isComplete(state: CATState, maxQuestions = 20): boolean {
  return state.answeredTotal >= maxQuestions
}

// ── Sample CAT Questions ─────────────────────────────────────────────

export const SAMPLE_QUESTIONS: CATQuestion[] = [
  // B1
  { id: 'b1-v1', level: 'B1', skill: 'vocabulary', question: 'She has a ___ for languages.', options: ['gift', 'present', 'talent', 'skill'], answer: 'gift' },
  { id: 'b1-g1', level: 'B1', skill: 'grammar', question: 'I ___ here since 2010.', options: ['live', 'have lived', 'am living', 'lived'], answer: 'have lived' },
  { id: 'b1-l1', level: 'B1', skill: 'listening', question: 'The speaker says the train arrives at ___.', options: ['3:15', '3:50', '4:15', '4:50'], answer: '3:15' },
  { id: 'b1-r1', level: 'B1', skill: 'reading', question: 'What is the main idea of the passage?', options: ['Climate change', 'Economic growth', 'Cultural exchange', 'Technology'], answer: 'Climate change' },
  // A2
  { id: 'a2-v1', level: 'A2', skill: 'vocabulary', question: 'The opposite of "expensive" is ___.', options: ['cheap', 'rich', 'beautiful', 'large'], answer: 'cheap' },
  { id: 'a2-g1', level: 'A2', skill: 'grammar', question: 'There ___ many books on the shelf.', options: ['is', 'are', 'be', 'was'], answer: 'are' },
  // B2
  { id: 'b2-v1', level: 'B2', skill: 'vocabulary', question: 'His argument was ___, but unconvincing.', options: ['eloquent', 'loud', 'angry', 'brief'], answer: 'eloquent' },
  { id: 'b2-g1', level: 'B2', skill: 'grammar', question: 'Had I known, I ___ have acted differently.', options: ['will', 'would', 'shall', 'should'], answer: 'would' },
  // C1
  { id: 'c1-v1', level: 'C1', skill: 'vocabulary', question: 'The policy was met with ___ opposition.', options: ['fierce', 'big', 'much', 'strong'], answer: 'fierce' },
  { id: 'c1-g1', level: 'C1', skill: 'grammar', question: 'Rarely ___ such an opportunity present itself.', options: ['does', 'is', 'has', 'will'], answer: 'does' },
]

export function getQuestionForLevel(level: CEFRLevel): CATQuestion | null {
  const candidates = SAMPLE_QUESTIONS.filter((q) => q.level === level)
  if (candidates.length === 0) return null
  return candidates[Math.floor(Math.random() * candidates.length)]
}
