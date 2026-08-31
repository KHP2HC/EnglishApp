import { useEffect, useState, useCallback } from 'react'

// ── PWA Install Prompt ──────────────────────────────────────────────

export function useInstallPrompt() {
  const [installPrompt, setInstallPrompt] = useState<any>(null)
  const [canInstall, setCanInstall] = useState(false)

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault()
      setInstallPrompt(e)
      setCanInstall(true)
    }
    window.addEventListener('beforeinstallprompt', handler)
    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  const promptInstall = useCallback(async () => {
    if (!installPrompt) return false
    installPrompt.prompt()
    const result = await installPrompt.userChoice
    setInstallPrompt(null)
    setCanInstall(false)
    return result.outcome === 'accepted'
  }, [installPrompt])

  return { canInstall, promptInstall }
}

// ── Notifications ────────────────────────────────────────────────────

export function useNotifications() {
  const [permission, setPermission] = useState<NotificationPermission>(
    typeof Notification !== 'undefined' ? Notification.permission : 'denied'
  )

  const requestPermission = useCallback(async () => {
    if (!('Notification' in window)) return 'denied'
    const result = await Notification.requestPermission()
    setPermission(result)
    return result
  }, [])

  const notify = useCallback(
    (title: string, body: string) => {
      if (permission === 'granted') {
        const base = import.meta.env.BASE_URL || '/'
        new Notification(title, {
          body,
          icon: `${base}icon-192.png`,
          badge: `${base}favicon.svg`,
        })
      }
    },
    [permission]
  )

  return { permission, requestPermission, notify }
}

// ── Online/Offline Status ────────────────────────────────────────────

export function useOnlineStatus() {
  const [online, setOnline] = useState(navigator.onLine)

  useEffect(() => {
    const goOnline = () => setOnline(true)
    const goOffline = () => setOnline(false)
    window.addEventListener('online', goOnline)
    window.addEventListener('offline', goOffline)
    return () => {
      window.removeEventListener('online', goOnline)
      window.removeEventListener('offline', goOffline)
    }
  }, [])

  return online
}
