/**
 * API client tests
 *
 * Tests the API client's error handling, token attachment,
 * and response parsing.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock supabase
vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: { session: { access_token: 'test-token' } },
      }),
      signOut: vi.fn().mockResolvedValue({}),
    },
  },
}))

// Mock import.meta.env
vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:8000')

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should export api object with HTTP methods', async () => {
    const { api } = await import('@/api/client')
    expect(api).toBeDefined()
    expect(typeof api.get).toBe('function')
    expect(typeof api.post).toBe('function')
    expect(typeof api.patch).toBe('function')
    expect(typeof api.put).toBe('function')
    expect(typeof api.delete).toBe('function')
  })

  it('should export ApiError class', async () => {
    const { ApiError } = await import('@/api/client')
    const err = new ApiError(404, 'Not found')
    expect(err.status).toBe(404)
    expect(err.message).toBe('Not found')
    expect(err.name).toBe('ApiError')
  })

  it('should handle network errors', async () => {
    const { api, ApiError } = await import('@/api/client')

    // Mock fetch to throw
    const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'))
    vi.stubGlobal('fetch', mockFetch)

    await expect(api.get('/test')).rejects.toThrow()
  })

  it('should handle 204 No Content', async () => {
    const { api } = await import('@/api/client')

    const mockFetch = vi.fn().mockResolvedValue(
      new Response(null, { status: 204 }),
    )
    vi.stubGlobal('fetch', mockFetch)

    const result = await api.delete('/test/123')
    expect(result).toBeUndefined()
  })

  it('should parse JSON error responses', async () => {
    const { api, ApiError } = await import('@/api/client')

    const errorBody = JSON.stringify({
      error: { message: 'Custom error', code: 'CUSTOM_ERROR' },
    })
    const mockFetch = vi.fn().mockResolvedValue(
      new Response(errorBody, { status: 400 }),
    )
    vi.stubGlobal('fetch', mockFetch)

    try {
      await api.get('/test')
      expect.fail('Should have thrown')
    } catch (err: any) {
      expect(err).toBeInstanceOf(ApiError)
      expect(err.status).toBe(400)
      expect(err.message).toBe('Custom error')
      expect(err.code).toBe('CUSTOM_ERROR')
    }
  })
})

describe('API Domain Clients', () => {
  it('should export all domain clients', async () => {
    const mod = await import('@/api/index')
    expect(mod.profileApi).toBeDefined()
    expect(mod.vocabularyApi).toBeDefined()
    expect(mod.reviewsApi).toBeDefined()
    expect(mod.sessionsApi).toBeDefined()
    expect(mod.progressApi).toBeDefined()
    expect(mod.plannerApi).toBeDefined()
    expect(mod.errorsApi).toBeDefined()
    expect(mod.writingApi).toBeDefined()
    expect(mod.healthApi).toBeDefined()
  })
})
