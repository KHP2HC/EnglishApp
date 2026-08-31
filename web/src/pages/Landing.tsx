import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Brain, Calendar, BarChart3, FlaskConical, Zap, Globe } from 'lucide-react'
import { Button } from '@/components/ui/button'

const features = [
  { icon: Brain, title: 'SRS Flashcards', desc: 'SM-2 spaced repetition with 50,000+ words' },
  { icon: Calendar, title: 'Smart Planner', desc: 'AI-generated study plans from your deadline' },
  { icon: FlaskConical, title: 'Mock Tests', desc: 'Full TOEIC, IELTS, TOEFL & VSTEP simulation' },
  { icon: BarChart3, title: 'Progress Tracking', desc: 'Heatmaps, charts, and error journal' },
  { icon: Zap, title: 'AI Writing Coach', desc: 'Claude-powered essay feedback' },
  { icon: Globe, title: 'Works Offline', desc: 'PWA — study vocabulary without internet' },
]

export function Landing() {
  return (
    <div className="min-h-screen bg-bg-dark text-white">
      {/* Hero */}
      <section className="max-w-5xl mx-auto px-4 pt-20 pb-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-5xl md:text-6xl font-bold font-heading mb-4">
            EnglishCoach Pro
          </h1>
          <p className="text-xl text-gray-400 mb-2">
            Your personal AI English exam coach.
          </p>
          <p className="text-lg text-gray-500 mb-8">
            TOEIC · IELTS · TOEFL · VSTEP — Free, no download, works on any device.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/auth">
              <Button size="lg" className="w-full sm:w-auto">
                Start for free — no credit card
              </Button>
            </Link>
            <a href="#features">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                See features
              </Button>
            </a>
          </div>
        </motion.div>

        {/* Animated score counter */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-12 flex justify-center gap-8 text-center"
        >
          <div>
            <motion.p
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5, type: 'spring' }}
              className="text-4xl font-bold text-accent"
            >
              990
            </motion.p>
            <p className="text-sm text-gray-400">TOEIC</p>
          </div>
          <div>
            <motion.p
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.7, type: 'spring' }}
              className="text-4xl font-bold text-accent"
            >
              8.0
            </motion.p>
            <p className="text-sm text-gray-400">IELTS</p>
          </div>
          <div>
            <motion.p
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.9, type: 'spring' }}
              className="text-4xl font-bold text-accent"
            >
              120
            </motion.p>
            <p className="text-sm text-gray-400">TOEFL</p>
          </div>
        </motion.div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-5xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold font-heading text-center mb-12">
          Everything you need to ace your exam
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="rounded-xl border border-border bg-surface-dark p-6"
            >
              <f.icon className="h-8 w-8 text-accent mb-3" />
              <h3 className="font-semibold text-lg mb-1">{f.title}</h3>
              <p className="text-sm text-gray-400">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-3xl mx-auto px-4 py-16 text-center">
        <h2 className="text-3xl font-bold font-heading mb-4">
          Study for free · No app download · Works on any device
        </h2>
        <Link to="/auth">
          <Button size="lg" className="mt-4">
            Get started now →
          </Button>
        </Link>
      </section>

      <footer className="border-t border-border py-8 text-center text-sm text-gray-500">
        EnglishCoach Pro · MIT License · Built with React + Supabase
      </footer>
    </div>
  )
}
