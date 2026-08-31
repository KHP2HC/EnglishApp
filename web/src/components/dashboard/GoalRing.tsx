import { motion } from 'framer-motion'

export function GoalRing({ minutes, target }: { minutes: number; target: number }) {
  const pct = Math.min(100, (minutes / Math.max(1, target)) * 100)
  const radius = 52
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (pct / 100) * circumference

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle
            cx="60" cy="60" r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            className="text-gray-200 dark:text-gray-700"
          />
          <motion.circle
            cx="60" cy="60" r={radius}
            fill="none"
            stroke="#4A90E2"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold font-heading">{minutes}</span>
          <span className="text-xs text-gray-400">/ {target} min</span>
        </div>
      </div>
      <p className="text-sm text-gray-400 mt-2">Daily Goal</p>
    </div>
  )
}
