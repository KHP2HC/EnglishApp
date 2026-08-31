/**
 * Seed data loader — loads vocabulary, question bank, and reading tests
 * from static JSON files in /public/data/.
 *
 * These files are bundled with the app and cached by the service worker,
 * so they work fully offline.
 */

import type { VocabCard, ExamType, CEFRLevel } from './supabase'

// ── Types ────────────────────────────────────────────────────────────

export interface SeedVocabEntry {
  word: string
  phonetic: string | null
  synonym: string | string[] | null
  antonym: string | string[] | null
  meaning_en: string
  meaning_vi: string
  example_sentence: string | null
  exam_type: string
  difficulty_level: string
  category: string
}

export interface SeedQuestion {
  level: CEFRLevel
  question: string
  options: string[]
  answer: string
}

export interface ReadingTest {
  id: string
  title: string
  time_minutes: number
  passages: ReadingPassage[]
}

export interface ReadingPassage {
  id: string
  number: number
  title: string
  difficulty: string
  instructions: string
  text: string
  questions: ReadingQuestion[]
}

export interface ReadingQuestion {
  id: string
  number: number
  type: 'mcq' | 'tfng' | 'ynng' | 'matching' | 'completion'
  text: string
  options?: string[]
  answer: string | string[]
  explanation?: string
  max_words?: number
}

// ── Listening Test Types ─────────────────────────────────────────────

export interface ListeningTest {
  id: string
  title: string
  time_minutes: number
  sections: ListeningSection[]
}

export interface ListeningSection {
  id: string
  number: number
  title: string
  instructions: string
  transcript: string
  questions: ListeningQuestion[]
}

export interface ListeningQuestion {
  id: string
  number: number
  type: 'mcq' | 'tfng' | 'ynng' | 'completion' | 'matching'
  text: string
  options?: string[]
  answer: string | string[]
  explanation?: string
  max_words?: number
}

// ── Writing Task Types ───────────────────────────────────────────────

export interface WritingSubTask {
  id: string
  type: 'task1' | 'task2'
  title: string
  instructions: string
  prompt: string
  data_description?: string
  min_words: number
  time_minutes: number
  band_descriptors?: {
    task_achievement?: string
    coherence?: string
    lexical_resource?: string
    grammar?: string
  }
}

export interface WritingTest {
  id: string
  title: string
  task1: WritingSubTask
  task2: WritingSubTask
}

/** @deprecated Use WritingTest instead */
export type WritingTask = WritingSubTask

// ── Speaking Test Types ─────────────────────────────────────────────

export interface SpeakingPart {
  part: number
  title: string
  instructions: string
  timeMinutes: number
  questions: string[]
}

export interface SpeakingTest {
  id: string
  title: string
  parts: SpeakingPart[]
}

// ── Loaders ──────────────────────────────────────────────────────────

let vocabCache: SeedVocabEntry[] | null = null
let questionCache: SeedQuestion[] | null = null
let readingCache: ReadingTest[] | null = null
let listeningCache: ListeningTest[] | null = null
let writingCache: WritingTest[] | null = null
let speakingCache: SpeakingTest[] | null = null

export async function loadVocabData(): Promise<SeedVocabEntry[]> {
  if (vocabCache) return vocabCache
  const resp = await fetch('/data/vocab.json')
  if (!resp.ok) throw new Error('Failed to load vocab data')
  vocabCache = await resp.json()
  return vocabCache!
}

export async function loadQuestionBank(): Promise<SeedQuestion[]> {
  if (questionCache) return questionCache
  const resp = await fetch('/data/question_bank.json')
  if (!resp.ok) throw new Error('Failed to load question bank')
  questionCache = await resp.json()
  return questionCache!
}

export async function loadReadingTests(): Promise<ReadingTest[]> {
  if (readingCache) return readingCache
  const resp = await fetch('/data/reading_tests.json')
  if (!resp.ok) throw new Error('Failed to load reading tests')
  readingCache = await resp.json()
  return readingCache!
}

export async function loadReadingTest(id?: string): Promise<ReadingTest | null> {
  const tests = await loadReadingTests()
  if (!id) return tests[0] || null
  return tests.find((t) => t.id === id) || tests[0] || null
}

export async function loadListeningTests(): Promise<ListeningTest[]> {
  if (listeningCache) return listeningCache
  const resp = await fetch('/data/listening_tests.json')
  if (!resp.ok) throw new Error('Failed to load listening tests')
  listeningCache = await resp.json()
  return listeningCache!
}

export async function loadListeningTest(id?: string): Promise<ListeningTest | null> {
  const tests = await loadListeningTests()
  if (!id) return tests[0] || null
  return tests.find((t) => t.id === id) || tests[0] || null
}

export async function loadWritingTests(): Promise<WritingTest[]> {
  if (writingCache) return writingCache
  const resp = await fetch('/data/writing_tests.json')
  if (!resp.ok) throw new Error('Failed to load writing tests')
  writingCache = await resp.json()
  return writingCache!
}

export async function loadWritingTest(id?: string): Promise<WritingTest | null> {
  const tests = await loadWritingTests()
  if (!id) return tests[0] || null
  return tests.find((t) => t.id === id) || tests[0] || null
}

/** @deprecated Use loadWritingTests instead */
export async function loadWritingTasks(): Promise<WritingTest[]> {
  return loadWritingTests()
}

/** @deprecated Use loadWritingTest instead */
export async function loadWritingTask(id?: string): Promise<WritingTest | null> {
  return loadWritingTest(id)
}

export async function loadSpeakingTests(): Promise<SpeakingTest[]> {
  if (speakingCache) return speakingCache
  const resp = await fetch('/data/speaking_tests.json')
  if (!resp.ok) throw new Error('Failed to load speaking tests')
  speakingCache = await resp.json()
  return speakingCache!
}

export async function loadSpeakingTest(id?: string): Promise<SpeakingTest | null> {
  const tests = await loadSpeakingTests()
  if (!id) return tests[0] || null
  return tests.find((t) => t.id === id) || tests[0] || null
}

// ── Converters ──────────────────────────────────────────────────────

export function seedToVocabCard(entry: SeedVocabEntry, id: string): VocabCard {
  const examTypes: ExamType[] = []
  const raw = entry.exam_type
  if (raw) {
    const upper = raw.toUpperCase()
    if (['TOEIC', 'IELTS', 'TOEFL', 'VSTEP'].includes(upper)) {
      examTypes.push(upper as ExamType)
    }
  }
  if (examTypes.length === 0) examTypes.push('IELTS')

  return {
    id,
    word: entry.word,
    phonetic: entry.phonetic || null,
    meaning_en: entry.meaning_en || '',
    meaning_vi: entry.meaning_vi || '',
    example_sentence: entry.example_sentence || null,
    audio_url: null,
    exam_type: examTypes,
    cefr_level: (entry.difficulty_level as CEFRLevel) || 'B1',
    category: entry.category || 'general',
  }
}

export function formatSynonym(syn: string | string[] | null): string | null {
  if (!syn) return null
  if (Array.isArray(syn)) return syn.filter(Boolean).join(', ') || null
  return syn || null
}

// ── Stats ────────────────────────────────────────────────────────────

export async function getVocabStats() {
  const data = await loadVocabData()
  const byLevel: Record<string, number> = {}
  const byExam: Record<string, number> = {}
  for (const item of data) {
    const level = item.difficulty_level || 'B1'
    byLevel[level] = (byLevel[level] || 0) + 1
    const exam = item.exam_type || 'IELTS'
    byExam[exam] = (byExam[exam] || 0) + 1
  }
  return { total: data.length, byLevel, byExam }
}
