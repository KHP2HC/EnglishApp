import type { CEFRLevel } from './supabase'
import {
  loadVocabData,
  loadQuestionBank,
  loadReadingTests,
  loadListeningTests,
  loadWritingTests,
  type SeedVocabEntry,
  type SeedQuestion,
  type ReadingTest,
  type ListeningTest,
  type WritingTest,
} from './seed-data'

// ── CAT (Computer Adaptive Testing) Engine ───────────────────────────

export type CATSkill = 'vocabulary' | 'grammar' | 'reading' | 'listening' | 'writing'

export interface CATQuestion {
  id: string
  level: CEFRLevel
  skill: CATSkill
  question: string
  context?: string // optional passage or transcript excerpt
  options: string[]
  answer: string
}

export interface CATState {
  currentLevel: CEFRLevel
  answeredCorrect: number
  answeredTotal: number
  history: { level: CEFRLevel; correct: boolean; skill: CATSkill }[]
  skillScores: Record<string, { correct: number; total: number }>
  questionQueue: CATQuestion[]
  queueIndex: number
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
      reading: { correct: 0, total: 0 },
      listening: { correct: 0, total: 0 },
      writing: { correct: 0, total: 0 },
    },
    questionQueue: [],
    queueIndex: 0,
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
  const newHistory = [...state.history, { level: question.level, correct, skill: question.skill }]
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
    queueIndex: state.queueIndex + 1,
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

// ── Question Pool Builders ──────────────────────────────────────────
// Each builder converts real seed data (vocab, reading, listening, etc.)
// into CATQuestion objects with 4 options + 1 answer.

function shuffle<T>(arr: T[]): T[] {
  const copy = [...arr]
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy
}

function pickRandom<T>(arr: T[], n: number): T[] {
  return shuffle(arr).slice(0, n)
}

/** Build vocabulary questions from the 5,000+ vocab entries. */
function buildVocabQuestions(entries: SeedVocabEntry[]): CATQuestion[] {
  const byLevel: Record<string, SeedVocabEntry[]> = {}
  for (const e of entries) {
    const lvl = e.difficulty_level || 'B1'
    if (!byLevel[lvl]) byLevel[lvl] = []
    byLevel[lvl].push(e)
  }

  const questions: CATQuestion[] = []

  for (const level of LEVEL_ORDER) {
    const pool = byLevel[level]
    if (!pool || pool.length < 4) continue

    const picked = pickRandom(pool, 6)
    for (const entry of picked) {
      const correctAnswer = entry.meaning_en
      const distractors = pickRandom(
        entries.filter((e) => e.word !== entry.word && e.meaning_en !== correctAnswer),
        3
      ).map((d) => d.meaning_en)

      const options = shuffle([correctAnswer, ...distractors])

      questions.push({
        id: `vocab-${level}-${entry.word}`,
        level,
        skill: 'vocabulary',
        question: `What does "${entry.word}" mean?`,
        context: entry.example_sentence || undefined,
        options,
        answer: correctAnswer,
      })
    }
  }

  return questions
}

/** Build grammar questions from the question bank. */
function buildGrammarQuestions(bank: SeedQuestion[]): CATQuestion[] {
  const questions: CATQuestion[] = []

  for (const q of bank) {
    questions.push({
      id: `grammar-bank-${q.level}`,
      level: q.level,
      skill: 'grammar',
      question: q.question,
      options: q.options,
      answer: q.answer,
    })
  }

  return questions
}

/** Build reading comprehension questions from the 500 reading tests. */
function buildReadingQuestions(tests: ReadingTest[]): CATQuestion[] {
  const questions: CATQuestion[] = []

  for (const test of tests) {
    for (const passage of test.passages) {
      const level = (passage.difficulty as CEFRLevel) || 'B1'
      const mcqQuestions = passage.questions.filter(
        (q) => q.type === 'mcq' && q.options && q.options.length >= 2
      )
      for (const q of mcqQuestions) {
        const rawOpts: string[] = Array.isArray(q.options) ? q.options : (q.options ? [q.options] : [])
        const opts: string[] = rawOpts.slice(0, 4)
        while (opts.length < 4) {
          opts.push('(none of the above)')
        }
        questions.push({
          id: `reading-${test.id}-${q.id}`,
          level,
          skill: 'reading',
          question: q.text,
          context: passage.text.length > 500 ? passage.text.substring(0, 500) + '…' : passage.text,
          options: opts,
          answer: Array.isArray(q.answer) ? q.answer[0] : q.answer,
        })
      }
    }
  }

  return questions
}

/** Build listening comprehension questions from the 500 listening tests. */
function buildListeningQuestions(tests: ListeningTest[]): CATQuestion[] {
  const questions: CATQuestion[] = []

  for (const test of tests) {
    for (const section of test.sections) {
      const level: CEFRLevel = 'B1'
      const mcqQuestions = section.questions.filter(
        (q) => q.type === 'mcq' && q.options && q.options.length >= 2
      )
      for (const q of mcqQuestions) {
        const rawOpts: string[] = Array.isArray(q.options) ? q.options : (q.options ? [q.options] : [])
        const opts: string[] = rawOpts.slice(0, 4)
        while (opts.length < 4) {
          opts.push('(none of the above)')
        }
        const transcript = section.transcript || ''
        const context = transcript.length > 400 ? transcript.substring(0, 400) + '…' : transcript

        questions.push({
          id: `listening-${test.id}-${q.id}`,
          level,
          skill: 'listening',
          question: q.text,
          context,
          options: opts,
          answer: Array.isArray(q.answer) ? q.answer[0] : q.answer,
        })
      }
    }
  }

  return questions
}

/** Build writing questions from the 500 writing tests. */
function buildWritingQuestions(tests: WritingTest[]): CATQuestion[] {
  const questions: CATQuestion[] = []

  for (const test of tests) {
    const task = test.task2
    let level: CEFRLevel = 'B1'
    if (task.min_words >= 250) level = 'B2'
    else if (task.min_words >= 200) level = 'B1'
    else level = 'A2'

    const correctAnswer = 'Write a discursive essay discussing both views'
    const distractors = [
      'Write a formal letter of complaint',
      'Describe a chart or graph',
      'Write a personal narrative story',
    ]
    const options = shuffle([correctAnswer, ...distractors])

    questions.push({
      id: `writing-${test.id}`,
      level,
      skill: 'writing',
      question: `Read this task: "${task.prompt.substring(0, 200)}${task.prompt.length > 200 ? '…' : ''}"\n\nWhat type of writing is required?`,
      context: task.instructions,
      options,
      answer: correctAnswer,
    })
  }

  return questions
}

// ── Question Pool Loader ─────────────────────────────────────────────

let poolCache: CATQuestion[] | null = null

/**
 * Load and build the full question pool from all seed data files.
 * The pool includes questions from:
 *  - 5,000+ vocabulary entries (meaning questions)
 *  - 6 grammar questions (question bank)
 *  - 500 reading tests (MCQ comprehension)
 *  - 500 listening tests (MCQ comprehension)
 *  - 500 writing tests (task identification)
 */
export async function loadQuestionPool(): Promise<CATQuestion[]> {
  if (poolCache) return poolCache

  const [vocab, bank, reading, listening, writing] = await Promise.all([
    loadVocabData(),
    loadQuestionBank(),
    loadReadingTests(),
    loadListeningTests(),
    loadWritingTests(),
  ])

  const pool: CATQuestion[] = [
    ...buildVocabQuestions(vocab),
    ...buildGrammarQuestions(bank),
    ...buildReadingQuestions(reading),
    ...buildListeningQuestions(listening),
    ...buildWritingQuestions(writing),
  ]

  poolCache = pool
  return pool
}

/**
 * Build a 20-question adaptive test from the pool.
 * The test covers all 5 skills, with questions that start at B1 and
 * adapt up/down based on accuracy.
 */
export async function buildAdaptiveTest(totalQuestions = 20): Promise<CATQuestion[]> {
  const pool = await loadQuestionPool()

  // Group by skill
  const bySkill: Record<string, CATQuestion[]> = {}
  for (const q of pool) {
    if (!bySkill[q.skill]) bySkill[q.skill] = []
    bySkill[q.skill].push(q)
  }

  // Distribute questions across skills:
  // 4 vocabulary, 4 grammar, 4 reading, 4 listening, 4 writing = 20
  const perSkill = Math.floor(totalQuestions / 5)
  const remainder = totalQuestions - perSkill * 5

  const skills: CATSkill[] = ['vocabulary', 'grammar', 'reading', 'listening', 'writing']
  const test: CATQuestion[] = []

  for (let i = 0; i < skills.length; i++) {
    const skill = skills[i]
    const count = perSkill + (i < remainder ? 1 : 0)
    const skillPool = bySkill[skill] || []

    // Try to get a mix of levels, starting around B1
    const targetLevels: CEFRLevel[] = ['B1', 'B2', 'A2', 'C1', 'A1', 'C2']
    const used = new Set<string>()

    for (const targetLevel of targetLevels) {
      const currentCount = test.filter((q) => q.skill === skill).length
      if (currentCount >= count) break
      const candidates = skillPool.filter(
        (q) => q.level === targetLevel && !used.has(q.id)
      )
      const picked = pickRandom(candidates, count - currentCount)
      for (const q of picked) {
        const cc = test.filter((qq) => qq.skill === skill).length
        if (cc >= count) break
        test.push(q)
        used.add(q.id)
      }
    }

    // If we still don't have enough, pick any from the skill
    const currentCount = test.filter((q) => q.skill === skill).length
    if (currentCount < count) {
      const remaining = skillPool.filter((q) => !used.has(q.id))
      const picked = pickRandom(remaining, count - currentCount)
      for (const q of picked) {
        test.push(q)
        used.add(q.id)
      }
    }
  }

  // Shuffle the final test so skills are interleaved
  return shuffle(test)
}

// ── Legacy compatibility ────────────────────────────────────────────

export const SAMPLE_QUESTIONS: CATQuestion[] = []

export function getQuestionForLevel(_level: CEFRLevel): CATQuestion | null {
  return null
}
