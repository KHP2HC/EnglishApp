import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { BottomNav } from './BottomNav'
import { useOnlineStatus } from '@/hooks/useNotifications'

export function AppLayout() {
  const online = useOnlineStatus()

  return (
    <div className="flex h-screen overflow-hidden bg-bg-light dark:bg-bg-dark">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar />
        {!online && (
          <div className="bg-warning/20 text-warning text-sm text-center py-1.5 px-4 border-b border-warning/30">
            ⚠️ Offline — vocabulary sessions still work. Other features need a connection.
          </div>
        )}
        <main className="flex-1 overflow-y-auto pb-16 md:pb-0">
          <div className="max-w-5xl mx-auto px-4 py-6">
            <Outlet />
          </div>
        </main>
        <BottomNav />
      </div>
    </div>
  )
}
