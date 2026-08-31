import { Volume2 } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { supabase, type VocabCard } from '@/lib/supabase'
import { loadVocabData } from '@/lib/seed-data'
import { useSpeech } from '@/hooks/useSpeech'

function isSupabaseConfigured(): boolean {
  const url = import.meta.env.VITE_SUPABASE_URL
  return !!url && !url.includes('placeholder')
}

export function WordOfDay() {
  const { speak } = useSpeech()

  const { data: card } = useQuery({
    queryKey: ['word-of-day'],
    queryFn: async (): Promise<VocabCard | null> => {
      if (isSupabaseConfigured()) {
        const { count } = await supabase.from('vocab_cards').select('*', { count: 'exact', head: true })
        if (count && count > 0) {
          const offset = Math.floor(Math.random() * count)
          const { data } = await supabase
            .from('vocab_cards')
            .select('*')
            .range(offset, offset)
            .single()
          return data as VocabCard
        }
      }
      // Fallback: load from local seed data
      const seed = await loadVocabData()
      if (seed.length === 0) return null
      const entry = seed[Math.floor(Math.random() * seed.length)]
      return {
        id: 'seed-wotd',
        word: entry.word,
        phonetic: entry.phonetic,
        meaning_en: entry.meaning_en,
        meaning_vi: entry.meaning_vi,
        example_sentence: entry.example_sentence,
        audio_url: null,
        exam_type: [],
        cefr_level: (entry.difficulty_level as any) || 'B1',
        category: entry.category,
      }
    },
    staleTime: 1000 * 60 * 60, // 1 hour
  })

  if (!card) {
    return (
      <div className="rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-4">
        <p className="text-sm text-gray-400">Loading word of the day…</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-border bg-gradient-to-br from-accent/10 to-transparent p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-accent">📖 Word of the Day</span>
        <button
          onClick={() => speak(card.word)}
          className="p-1.5 rounded-lg hover:bg-accent/10 transition-colors"
        >
          <Volume2 className="h-4 w-4 text-accent" />
        </button>
      </div>
      <div className="flex items-baseline gap-2 mb-1">
        <h3 className="text-xl font-bold font-heading">{card.word}</h3>
        {card.phonetic && (
          <span className="text-sm text-gray-400 font-mono">{card.phonetic}</span>
        )}
      </div>
      <p className="text-sm text-gray-300">{card.meaning_vi}</p>
      <p className="text-xs text-gray-400 mt-1">{card.meaning_en}</p>
      {card.example_sentence && (
        <p className="text-xs italic text-gray-500 mt-2">"{card.example_sentence}"</p>
      )}
    </div>
  )
}
