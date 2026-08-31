/**
 * API client barrel export
 *
 * All application data access goes through these typed clients.
 * Direct Supabase CRUD is not allowed — only Supabase Auth operations.
 */

export { api, ApiError, API_BASE_URL } from './client'
export { profileApi } from './profile'
export { vocabularyApi } from './vocabulary'
export type { VocabListResponse } from './vocabulary'
export { reviewsApi } from './reviews'
export type { DueCardsResponse, RateCardResponse } from './reviews'
export { sessionsApi } from './sessions'
export { progressApi } from './progress'
export type { ProgressStats } from './progress'
export { plannerApi } from './planner'
export type { StudyPlan } from './planner'
export { errorsApi } from './errors'
export { writingApi } from './writing'
export { healthApi } from './health'
