import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Home, Brain, BookOpen, Headphones, PenLine, Mic,
  BarChart3, Calendar, FlaskConical, Settings as SettingsIcon, ChevronLeft
} from 'lucide-react'
import { useSettingsStore } from '@/stores/settings.store'
import { useAuthStore } from '@/stores/auth.store'
import { getLevelInfo } from '@/lib/srs'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/app', icon: Home, label: 'Dashboard' },
  { to: '/app/vocabulary', icon: Brain, label: 'Vocabulary' },
  { to: '/app/grammar', icon: BookOpen, label: 'Grammar' },
  { to: '/app/listening', icon: Headphones, label: 'Listening' },
  { to: '/app/reading', icon: BookOpen, label: 'Reading' },
  { to: '/app/writing', icon: PenLine, label: 'Writing' },
  { to: '/app/speaking', icon: Mic, label: 'Speaking' },
  { to: '/app/mock-test', icon: FlaskConical, label: 'Mock Test' },
  { to: '/app/progress', icon: BarChart3, label: 'Progress' },
  { to: '/app/planner', icon: Calendar, label: 'Planner' },
  { to: '/app/settings', icon: SettingsIcon, label: 'Settings' },
]

export function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useSettingsStore()
  const { user } = useAuthStore()
  const location = useLocation()

  const levelInfo = getLevelInfo(user?.total_xp || 0)

  return (
    <motion.aside
      initial={false}
      animate={{ width: sidebarCollapsed ? 64 : 240 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="hidden md:flex flex-col border-r border-border bg-surface-dark h-screen sticky top-0"
    >
      {/* Logo */}
      <div className="flex items-center gap-2 p-4 h-16 border-b border-border">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-white font-bold text-sm shrink-0">
          E
        </div>
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="font-heading font-bold text-white text-lg whitespace-nowrap"
            >
              EnglishCoach
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.to
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={cn(
                'flex items-center gap-3 px-4 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'text-accent bg-accent/10'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              )}
            >
              <item.icon className="h-5 w-5 shrink-0" />
              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.span
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    className="whitespace-nowrap"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </NavLink>
          )
        })}
      </nav>

      {/* Level badge */}
      <div className="p-3 border-t border-border">
        <div className={cn('flex items-center gap-2', sidebarCollapsed && 'justify-center')}>
          <span className="text-xl">{levelInfo.emoji}</span>
          {!sidebarCollapsed && (
            <div className="min-w-0">
              <p className="text-xs text-gray-400">Level {levelInfo.level}</p>
              <p className="text-xs font-medium text-white truncate">{levelInfo.name}</p>
            </div>
          )}
        </div>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={toggleSidebar}
        className="flex items-center justify-center p-3 border-t border-border text-gray-400 hover:text-white transition-colors"
      >
        <ChevronLeft className={cn('h-4 w-4 transition-transform', sidebarCollapsed && 'rotate-180')} />
      </button>
    </motion.aside>
  )
}
