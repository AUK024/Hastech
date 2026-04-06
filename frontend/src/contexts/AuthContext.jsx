import { createContext, useContext, useMemo, useState } from 'react'
import { AUTH_STORAGE_KEY } from '../utils/constants'

const AuthContext = createContext(null)

const parseCsv = (value) =>
  (value || '')
    .split(',')
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean)

const configuredEmails = parseCsv(import.meta.env.VITE_ALLOWED_ADMIN_EMAILS)
const configuredDomains = parseCsv(import.meta.env.VITE_ALLOWED_ADMIN_DOMAINS)

const fallbackEmails = ['admin@hascelik.com']
const allowedEmails = configuredEmails.length ? configuredEmails : fallbackEmails
const allowedDomains = configuredDomains

const readStoredUser = () => {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) {
      return null
    }
    const parsed = JSON.parse(raw)
    if (typeof parsed?.email === 'string' && parsed.email.includes('@')) {
      return { email: parsed.email.toLowerCase() }
    }
    return null
  } catch {
    return null
  }
}

const extractDomain = (email) => email.split('@')[1] || ''

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser)

  const login = (email) => {
    const normalized = String(email || '').trim().toLowerCase()
    if (!normalized || !normalized.includes('@')) {
      return { ok: false, error: 'Geçerli bir e-posta giriniz.' }
    }

    const domain = extractDomain(normalized)
    const permittedByEmail = allowedEmails.includes(normalized)
    const permittedByDomain = allowedDomains.includes(domain)

    if (!permittedByEmail && !permittedByDomain) {
      return { ok: false, error: 'Bu kullanıcı admin paneline yetkili değil.' }
    }

    const nextUser = { email: normalized }
    setUser(nextUser)
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(nextUser))
    return { ok: true }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem(AUTH_STORAGE_KEY)
  }

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      login,
      logout,
      allowedEmails,
      allowedDomains,
    }),
    [user]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
