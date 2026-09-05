/**
 * API client — central HTTP client for all backend communication.
 *
 * Responsibilities:
 * - Attach JWT to every request
 * - Handle 401 (redirect to auth)
 * - Handle 403 (forbidden)
 * - Handle 429 (rate limit)
 * - Parse error responses
 * - Typed responses
 * - Fast-fail when backend is unreachable (avoids long CORS hangs)
 */

import { supabase } from '@/lib/supabase'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// ── Error types ────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// ── Backend health cache ──────────────────────────────

let backendReachable: boolean | null = null
let lastHealthCheck = 0
const HEALTH_CHECK_INTERVAL = 30_000 // re-check at most every 30s
const REQUEST_TIMEOUT = 4_000 // fail fast after 4s

async function checkBackendHealth(): Promise<boolean> {
  const now = Date.now()
  if (backendReachable !== null && now - lastHealthCheck < HEALTH_CHECK_INTERVAL) {
    return backendReachable
  }

  lastHealthCheck = now
  try {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT)
    const resp = await fetch(`${API_BASE_URL}/api/v1/health`, {
      method: 'GET',
      signal: controller.signal,
    })
    clearTimeout(timer)
    backendReachable = resp.ok
  } catch {
    backendReachable = false
  }
  return backendReachable
}

// ── Token management ──────────────────────────────────

async function getAuthToken(): Promise<string | null> {
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token || null
}

// ── Core request function ──────────────────────────────

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  // Fast-fail: if we know the backend is down, don't even try
  const reachable = await checkBackendHealth()
  if (!reachable) {
    throw new ApiError(0, 'Backend is not reachable.')
  }

  const token = await getAuthToken()

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const url = `${API_BASE_URL}${path}`

  let response: Response
  try {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT)
    response = await fetch(url, { ...options, headers, signal: controller.signal })
    clearTimeout(timer)
  } catch (err) {
    backendReachable = false // mark as down so subsequent calls skip
    throw new ApiError(0, 'Network error — cannot reach the server.')
  }

  // Handle no content
  if (response.status === 204) {
    return undefined as T
  }

  // Parse JSON
  let data: any
  const text = await response.text()
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = text
  }

  if (!response.ok) {
    const message =
      data?.error?.message ||
      data?.detail ||
      `Request failed with status ${response.status}`
    const code = data?.error?.code

    if (response.status === 401) {
      // Session expired — sign out and redirect
      await supabase.auth.signOut()
    }

    throw new ApiError(response.status, message, code)
  }

  return data as T
}

// ── HTTP method helpers ────────────────────────────────

export const api = {
  get: <T>(path: string) => request<T>(path, { method: 'GET' }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
}

// ── Health management ─────────────────────────────────

/** Reset the cached backend health so the next request re-checks. */
export function resetBackendHealth() {
  backendReachable = null
  lastHealthCheck = 0
}

/** Returns true if the backend has been marked as reachable. */
export function isBackendReachable(): boolean {
  return backendReachable === true
}

export { API_BASE_URL }
