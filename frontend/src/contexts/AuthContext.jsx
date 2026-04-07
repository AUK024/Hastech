import { createContext, useContext, useMemo, useState } from 'react'
import { AUTH_STORAGE_KEY } from '../utils/constants'
import { api } from '../services/api'

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
      return {
        email: parsed.email.toLowerCase(),
        role: parsed.role === 'admin' ? 'admin' : 'employee',
      }
    }
    return null
  } catch {
    return null
  }
}

const extractDomain = (email) => email.split('@')[1] || ''

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser)

  const login = async (email) => {
    const normalized = String(email || '').trim().toLowerCase()
    if (!normalized || !normalized.includes('@')) {
      return { ok: false, error: 'Geçerli bir e-posta giriniz.' }
    }

    const domain = extractDomain(normalized)
    const permittedByEmail = allowedEmails.includes(normalized)
    const permittedByDomain = allowedDomains.includes(domain)

    if (permittedByEmail || permittedByDomain) {
      const nextUser = { email: normalized, role: 'admin' }
      setUser(nextUser)
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(nextUser))
      return { ok: true, role: 'admin' }
    }

    try {
      const res = await api.post('/employee-users/authorize', { email: normalized })
      if (!res.data?.authorized || res.data?.role !== 'employee') {
        return { ok: false, error: 'Bu kullanıcı admin paneline yetkili değil.' }
      }
    } catch {
      return { ok: false, error: 'Kullanıcı doğrulanamadı. API bağlantısını kontrol edin.' }
    }

    const nextUser = { email: normalized, role: 'employee' }
    setUser(nextUser)
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(nextUser))
    return { ok: true, role: 'employee' }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem(AUTH_STORAGE_KEY)
  }

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isAdmin: user?.role === 'admin',
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
