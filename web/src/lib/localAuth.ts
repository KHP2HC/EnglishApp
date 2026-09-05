/**
 * Local Authentication System
 *
 * Provides email + password account creation and login without requiring
 * Supabase or any external service.  Accounts and all learning data are
 * stored in localStorage, keyed by user ID.
 *
 * Passwords are hashed with SHA-256 (via Web Crypto API) — never stored
 * in plain text.
 */

// ── Types ────────────────────────────────────────────────────────────

export interface LocalAccount {
  id: string
  email: string
  name: string
  passwordHash: string
  createdAt: string
}

export interface LocalSession {
  userId: string
  email: string
  loginAt: string
}

// ── Storage keys ─────────────────────────────────────────────────────

const ACCOUNTS_KEY = 'ec_accounts'
const SESSION_KEY = 'ec_session'

// ── Helpers ──────────────────────────────────────────────────────────

async function hashPassword(password: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(password + 'ec_salt_2026') // light salting
  const hash = await crypto.subtle.digest('SHA-256', data)
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}

function generateId(): string {
  return 'local-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8)
}

function loadAccounts(): Record<string, LocalAccount> {
  try {
    const raw = localStorage.getItem(ACCOUNTS_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function saveAccounts(accounts: Record<string, LocalAccount>) {
  localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts))
}

function findAccountByEmail(accounts: Record<string, LocalAccount>, email: string): LocalAccount | undefined {
  const lower = email.toLowerCase().trim()
  return Object.values(accounts).find((a) => a.email.toLowerCase() === lower)
}

// ── Public API ───────────────────────────────────────────────────────

export async function signUp(email: string, password: string, name?: string): Promise<LocalAccount> {
  const accounts = loadAccounts()

  if (findAccountByEmail(accounts, email)) {
    throw new Error('An account with this email already exists')
  }

  if (password.length < 6) {
    throw new Error('Password must be at least 6 characters')
  }

  const account: LocalAccount = {
    id: generateId(),
    email: email.toLowerCase().trim(),
    name: name || email.split('@')[0],
    passwordHash: await hashPassword(password),
    createdAt: new Date().toISOString(),
  }

  accounts[account.id] = account
  saveAccounts(accounts)

  // Auto-login after signup
  setSession(account)

  return account
}

export async function signIn(email: string, password: string): Promise<LocalAccount> {
  const accounts = loadAccounts()
  const account = findAccountByEmail(accounts, email)

  if (!account) {
    throw new Error('No account found with this email. Please sign up first.')
  }

  const hash = await hashPassword(password)
  if (hash !== account.passwordHash) {
    throw new Error('Incorrect password')
  }

  setSession(account)
  return account
}

export function signOutLocal() {
  localStorage.removeItem(SESSION_KEY)
}

export function getSession(): LocalSession | null {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function getCurrentAccount(): LocalAccount | null {
  const session = getSession()
  if (!session) return null
  const accounts = loadAccounts()
  return accounts[session.userId] || null
}

function setSession(account: LocalAccount) {
  const session: LocalSession = {
    userId: account.id,
    email: account.email,
    loginAt: new Date().toISOString(),
  }
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function updateAccountName(userId: string, name: string) {
  const accounts = loadAccounts()
  if (accounts[userId]) {
    accounts[userId].name = name
    saveAccounts(accounts)
  }
}

export function hasAnyAccount(): boolean {
  return Object.keys(loadAccounts()).length > 0
}
