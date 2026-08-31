import { useState, useEffect } from 'react'
import { supabase, type SessionType } from '@/lib/supabase'
import { useAuthStore } from '@/stores/auth.store'
import { useDueCards, useRateCard, useStartCard } from '@/hooks/useVocab'
import { FlashCard } from '@/components/vocab/FlashCard'
import { QualityButtons } from '@/components/vocab/QualityButtons'
import { SessionSummary } from '@/components/vocab/SessionSummary'
import { useSessionStore } from '@/stores/session.store'
import { calculateXp, type Quality } from '@/lib/srs'
import { Button } from '@/components/ui/button'
import { Timer } from 'lucide-react'

function isSupabaseConfigured(): boolean {
  const url = import.meta.env.VITE_SUPABASE_URL
  return !!url && !url.includes('placeholder')
}

export function Vocabulary() {
  const { user } = useAuthStore()
  const { data, isLoading } = useDueCards(user?.id)
  const rateCard = useRateCard(user?.id)
  const startCard = useStartCard(user?.id)
  const { start, addXp, recordItem, reset, xpEarned, itemsTotal, itemsCorrect } = useSessionStore()

  const [index, setIndex] = useState(0)
  const [showQuality, setShowQuality] = useState(false)
  const [sessionActive, setSessionActive] = useState(false)
  const [sessionEnded, setSessionEnded] = useState(false)
  const [secondsLeft, setSecondsLeft] = useState(25 * 60)
  const [sessionId, setSessionId] = useState<string | null>(null)

  // Build queue: review cards first, then new cards
  const queue = [
    ...(data?.reviewCards?.map((p) => ({ type: 'review' as const, progress: p, card: p.card })) || []),
    ...(data?.newCards?.map((c) => ({ type: 'new' as const, progress: null, card: c })) || []),
  ]

  useEffect(() => {
    if (sessionActive && secondsLeft > 0) {
      const timer = setTimeout(() => setSecondsLeft((s) => s - 1), 1000)
      return () => clearTimeout(timer)
    }
    if (sessionActive && secondsLeft === 0) {
      endSession()
    }
  }, [sessionActive, secondsLeft])

  const startSession = async () => {
    setSessionActive(true)
    start('VOCABULARY')
    if (isSupabaseConfigured() && user) {
      const { data: s } = await supabase
        .from('study_sessions')
        .insert({ user_id: user.id, session_type: 'VOCABULARY' as SessionType })
        .select()
        .single()
      setSessionId(s?.id || null)
    }
  }

  const endSession = async () => {
    setSessionActive(false)
    setSessionEnded(true)
    if (isSupabaseConfigured() && sessionId && user) {
      await supabase
        .from('study_sessions')
        .update({
          ended_at: new Date().toISOString(),
          xp_earned: xpEarned,
          items_total: itemsTotal,
          items_correct: itemsCorrect,
        })
        .eq('id', sessionId)
      await supabase
        .from('profiles')
        .update({ total_xp: (user.total_xp || 0) + xpEarned })
        .eq('id', user.id)
    }
  }

  const handleRate = async (quality: Quality) => {
    const current = queue[index]
    if (!current) return

    if (current.type === 'new' && current.card) {
      await startCard.mutateAsync(current.card.id)
    } else if (current.progress) {
      await rateCard.mutateAsync({ progress: current.progress, quality })
    }

    const xp = calculateXp({ type: 'srs_review', quality })
    addXp(xp)
    recordItem(quality >= 3)

    setShowQuality(false)
    if (index + 1 >= queue.length) {
      endSession()
    } else {
      setIndex((i) => i + 1)
    }
  }

  if (isLoading) return <p className="text-gray-400">Loading vocabulary…</p>

  if (!sessionActive && !sessionEnded) {
    return (
      <div className="max-w-md mx-auto text-center py-12">
        <h1 className="text-2xl font-bold font-heading mb-2">🧠 Vocabulary Session</h1>
        <p className="text-gray-400 mb-6">
          {queue.length} cards ready for review
        </p>
        <Button size="lg" onClick={startSession} disabled={queue.length === 0}>
          Start Session
        </Button>
      </div>
    )
  }

  if (sessionEnded) {
    return (
      <SessionSummary
        reviewed={itemsTotal}
        correct={itemsCorrect}
        xpEarned={xpEarned}
        nextReview={null}
      />
    )
  }

  const current = queue[index]
  if (!current?.card) return <p>No cards available.</p>

  const m = Math.floor(secondsLeft / 60)
  const s = secondsLeft % 60

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Timer */}
      <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
        <Timer className="h-4 w-4" />
        <span className="font-mono">{String(m).padStart(2, '0')}:{String(s).padStart(2, '0')}</span>
      </div>

      <FlashCard card={current.card} index={index} total={queue.length} />

      {!showQuality ? (
        <Button className="w-full" onClick={() => setShowQuality(true)}>
          Show Answer
        </Button>
      ) : (
        <QualityButtons onRate={handleRate} disabled={rateCard.isPending || startCard.isPending} />
      )}
    </div>
  )
}
