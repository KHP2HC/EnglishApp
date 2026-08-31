import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    'Supabase env vars missing. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in .env.local'
  )
}

export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co',
  supabaseAnonKey || 'placeholder-anon-key',
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
    },
  }
)

// ── Types ────────────────────────────────────────────────────────────

export type ExamType = 'TOEIC' | 'IELTS' | 'TOEFL' | 'VSTEP'
export type CEFRLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'
export type SessionType =
  | 'VOCABULARY' | 'GRAMMAR' | 'LISTENING' | 'READING'
  | 'WRITING' | 'SPEAKING' | 'MOCK'

export interface Profile {
  id: string
  name: string
  avatar_emoji: string
  target_exam: ExamType | null
  target_score: number | null
  current_band: number | null
  skill_bands: Record<string, number>
  exam_date: string | null
  free_time: Record<string, number>
  session_time: 'MORNING' | 'AFTERNOON' | 'EVENING'
  streak_days: number
  total_xp: number
  last_active: string | null
  onboarded: boolean
  created_at: string
}

export interface VocabCard {
  id: string
  word: string
  phonetic: string | null
  meaning_en: string
  meaning_vi: string
  example_sentence: string | null
  audio_url: string | null
  exam_type: ExamType[]
  cefr_level: CEFRLevel | null
  category: string
}

export interface VocabProgress {
  id: string
  user_id: string
  card_id: string
  interval_days: number
  easiness: number
  repetitions: number
  next_review: string
  last_quality: number | null
  times_seen: number
  times_correct: number
}

export interface StudySession {
  id: string
  user_id: string
  started_at: string
  ended_at: string | null
  session_type: SessionType
  xp_earned: number
  items_total: number
  items_correct: number
}

export interface ErrorJournalEntry {
  id: string
  user_id: string
  session_id: string | null
  error_category: string
  skill: string
  question_snapshot: string
  user_answer: string
  correct_answer: string
  created_at: string
}

export interface StudyPlan {
  id: string
  user_id: string
  week_start: string
  daily_tasks: Record<string, DailyTask[]>
  created_at: string
}

export interface DailyTask {
  type: SessionType | string
  minutes: number
  label: string
}

export interface WritingSubmission {
  id: string
  user_id: string
  task_prompt: string
  user_essay: string
  ai_feedback: any
  band_estimate: number | null
  created_at: string
}
