import { create } from 'zustand'
import type { SessionType } from '@/lib/supabase'

interface SessionState {
  active: boolean
  sessionType: SessionType | null
  startTime: number | null
  xpEarned: number
  itemsTotal: number
  itemsCorrect: number
  start: (type: SessionType) => void
  end: () => void
  addXp: (xp: number) => void
  recordItem: (correct: boolean) => void
  reset: () => void
}

export const useSessionStore = create<SessionState>((set) => ({
  active: false,
  sessionType: null,
  startTime: null,
  xpEarned: 0,
  itemsTotal: 0,
  itemsCorrect: 0,
  start: (type) =>
    set({
      active: true,
      sessionType: type,
      startTime: Date.now(),
      xpEarned: 0,
      itemsTotal: 0,
      itemsCorrect: 0,
    }),
  end: () => set({ active: false }),
  addXp: (xp) => set((s) => ({ xpEarned: s.xpEarned + xp })),
  recordItem: (correct) =>
    set((s) => ({
      itemsTotal: s.itemsTotal + 1,
      itemsCorrect: s.itemsCorrect + (correct ? 1 : 0),
    })),
  reset: () =>
    set({
      active: false,
      sessionType: null,
      startTime: null,
      xpEarned: 0,
      itemsTotal: 0,
      itemsCorrect: 0,
    }),
}))
