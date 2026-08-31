import { NavLink, useLocation } from 'react-router-dom'
import {
  Home, Brain, BarChart3, Settings as SettingsIcon, BookOpen,
  Headphones, PenLine, Mic, FlaskConical,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const tabs = [
  { to: '/app', icon: Home, label: 'Home' },
  { to: '/app/vocabulary', icon: Brain, label: 'Vocab' },
  { to: '/app/reading', icon: BookOpen, label: 'Reading' },
  { to: '/app/listening', icon: Headphones, label: 'Listening' },
  { to: '/app/writing', icon: PenLine, label: 'Writing' },
  { to: '/app/speaking', icon: Mic, label: 'Speaking' },
  { to: '/app/mock-test', icon: FlaskConical, label: 'Mock' },
  { to: '/app/progress', icon: BarChart3, label: 'Progress' },
  { to: '/app/settings', icon: SettingsIcon, label: 'Settings' },
]

export function BottomNav() {
  const location = useLocation()

  return (
    <nav className="flex items-center justify-around h-16 border-t border-border bg-surface-dark md:hidden fixed bottom-0 left-0 right-0 z-50 overflow-x-auto">
      {tabs.map((tab) => {
        const isActive = location.pathname === tab.to
        return (
          <NavLink
            key={tab.to}
            to={tab.to}
            className={cn(
              'flex flex-col items-center justify-center gap-0.5 min-w-[64px] h-full text-[10px] transition-colors',
              isActive ? 'text-accent' : 'text-gray-400'
            )}
          >
            <tab.icon className="h-5 w-5" />
            <span>{tab.label}</span>
          </NavLink>
        )
      })}
    </nav>
  )
}
