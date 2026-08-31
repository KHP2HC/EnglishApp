import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Volume2 } from 'lucide-react'
import type { VocabCard } from '@/lib/supabase'
import { useSpeech } from '@/hooks/useSpeech'

interface FlashCardProps {
  card: VocabCard
  index: number
  total: number
}

export function FlashCard({ card, index, total }: FlashCardProps) {
  const [flipped, setFlipped] = useState(false)
  const { speak } = useSpeech()

  return (
    <div className="relative w-full" style={{ perspective: '1000px' }}>
      {/* Counter */}
      <div className="flex justify-between items-center mb-3 text-sm text-gray-400">
        <span>Card {index + 1} / {total}</span>
      </div>

      {/* Card */}
      <div
        className="relative w-full min-h-[320px] cursor-pointer"
        style={{ transformStyle: 'preserve-3d' }}
        onClick={() => setFlipped(!flipped)}
      >
        <AnimatePresence mode="wait">
          {!flipped ? (
            <motion.div
              key="front"
              initial={{ rotateY: 0 }}
              animate={{ rotateY: 0 }}
              exit={{ rotateY: 180 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
              className="absolute inset-0 flex flex-col items-center justify-center rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-8"
              style={{ backfaceVisibility: 'hidden' }}
            >
              <h2 className="text-4xl font-bold font-heading mb-2">{card.word}</h2>
              {card.phonetic && (
                <p className="text-lg text-gray-400 font-mono mb-4">{card.phonetic}</p>
              )}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  speak(card.word)
                }}
                className="p-3 rounded-full bg-accent/10 hover:bg-accent/20 transition-colors"
              >
                <Volume2 className="h-6 w-6 text-accent" />
              </button>
              <p className="text-sm text-gray-400 mt-6">Tap to reveal answer</p>
            </motion.div>
          ) : (
            <motion.div
              key="back"
              initial={{ rotateY: -180 }}
              animate={{ rotateY: 0 }}
              exit={{ rotateY: 0 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
              className="absolute inset-0 flex flex-col rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-6"
              style={{ backfaceVisibility: 'hidden' }}
            >
              <p className="text-lg font-semibold mb-2">{card.meaning_vi}</p>
              <p className="text-sm text-gray-400 mb-3">{card.meaning_en}</p>
              {card.example_sentence && (
                <p className="text-sm italic text-gray-500 border-l-2 border-accent pl-3">
                  "{card.example_sentence}"
                </p>
              )}
              {(card as any).synonym && (
                <p className="text-xs text-success mt-2">Synonym: {(card as any).synonym}</p>
              )}
              {(card as any).antonym && (
                <p className="text-xs text-error">Antonym: {(card as any).antonym}</p>
              )}
              {card.category && (
                <span className="mt-auto text-xs text-gray-400">Category: {card.category}</span>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
