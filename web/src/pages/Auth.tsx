import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/stores/auth.store'
import { signUp, signIn, hasAnyAccount } from '@/lib/localAuth'

export function Auth() {
  const navigate = useNavigate()
  const { onLocalAuth } = useAuthStore()
  const [mode, setMode] = useState<'signin' | 'signup'>(() =>
    hasAnyAccount() ? 'signin' : 'signup'
  )
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      if (mode === 'signup') {
        const account = await signUp(email, password, name || undefined)
        await onLocalAuth(account.id, account.name, account.email)
        navigate('/onboarding')
      } else {
        const account = await signIn(email, password)
        await onLocalAuth(account.id, account.name, account.email)
        navigate('/app')
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-dark px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">
            {mode === 'signup' ? 'Create your account' : 'Welcome back'}
          </CardTitle>
          <p className="text-center text-xs text-gray-400 mt-1">
            {mode === 'signup'
              ? 'Sign up to track your learning progress'
              : 'Sign in to continue your learning journey'}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSubmit} className="space-y-3">
            {mode === 'signup' && (
              <div className="space-y-1">
                <Label htmlFor="name">Name (optional)</Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="Your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            )}
            <div className="space-y-1">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="At least 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && <p className="text-sm text-error">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Loading…' : mode === 'signup' ? 'Create Account' : 'Sign In'}
            </Button>
          </form>

          <p className="text-center text-sm text-gray-400">
            {mode === 'signup' ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => setMode(mode === 'signup' ? 'signin' : 'signup')}
              className="text-accent hover:underline"
            >
              {mode === 'signup' ? 'Sign in' : 'Sign up'}
            </button>
          </p>

          <p className="text-center text-xs text-gray-500">
            <Link to="/" className="hover:underline">← Back to home</Link>
          </p>

          <p className="text-center text-xs text-gray-600">
            🔒 Your account and progress are stored securely on this device.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
