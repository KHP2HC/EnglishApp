import { motion } from 'framer-motion'
import { Check, X, Zap, Calendar } from 'lucide-react'

interface SessionSummaryProps {
  reviewed: number
  correct: number
  xpEarned: number
  nextReview: string | null
}

export function SessionSummary({ reviewed, correct, xpEarned, nextReview }: SessionSummaryProps) {
  const accuracy = reviewed > 0 ? Math.round((correct / reviewed) * 100) : 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-md mx-auto text-center space-y-6 py-8"
    >
      <h2 className="text-2xl font-bold font-heading">Session Complete! 🎉</h2>

      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-4">
          <Check className="h-6 w-6 text-success mx-auto mb-1" />
          <p className="text-2xl font-bold">{reviewed}</p>
          <p className="text-xs text-gray-400">Reviewed</p>
        </div>
        <div className="rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-4">
          <span className="block text-2xl font-bold text-accent mb-1">{accuracy}%</span>
          <p className="text-xs text-gray-400">Accuracy</p>
        </div>
        <div className="rounded-xl border border-border bg-surface-light dark:bg-surface-dark p-4">
          <Zap className="h-6 w-6 text-xp mx-auto mb-1" />
          <motion.span
            initial={{ scale: 1 }}
            animate={{ scale: [1, 1.4, 1] }}
            transition={{ duration: 0.3 }}
            className="block text-2xl font-bold text-xp"
          >
            +{xpEarned}
          </motion.span>
          <p className="text-xs text-gray-400">XP Earned</p>
        </div>
      </div>

      {nextReview && (
        <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
          <Calendar className="h-4 w-4" />
          Next review: {nextReview}
        </div>
      )}
    </motion.div>
  )
}
