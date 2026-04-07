import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const location = useLocation()
  const { login, allowedEmails, allowedDomains } = useAuth()

  const nextPath = location.state?.from?.pathname || '/'

  const allowlistLabel = useMemo(() => {
    const parts = []
    if (allowedEmails.length) {
      parts.push(`E-posta: ${allowedEmails.join(', ')}`)
    }
    if (allowedDomains.length) {
      parts.push(`Domain: ${allowedDomains.join(', ')}`)
    }
    return parts.join(' | ')
  }, [allowedEmails, allowedDomains])

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    const result = await login(email)
    if (!result.ok) {
      setError(result.error)
      return
    }
    navigate(nextPath, { replace: true })
  }

  return (
    <section style={{ maxWidth: 520, margin: '0 auto', padding: 8 }}>
      <h2 style={{ marginTop: 0 }}>Admin Giriş</h2>
      <p style={{ marginTop: 0 }}>
        Admin paneline erişim için izinli kullanıcı e-postası ile giriş yapın.
      </p>
      <form onSubmit={onSubmit} style={{ display: 'grid', gap: 10 }}>
        <label htmlFor="email">E-posta</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="admin@hascelik.com"
          autoComplete="email"
          required
        />
        <button type="submit">Giriş Yap</button>
      </form>
      {error ? (
        <p style={{ marginTop: 12, color: '#dc2626' }}>{error}</p>
      ) : null}
      <p style={{ marginTop: 12, fontSize: 13, opacity: 0.8 }}>
        İzin listesi: {allowlistLabel}
      </p>
      <p style={{ marginTop: 4, fontSize: 13, opacity: 0.8 }}>
        Domain bilgisi geldiğinde `.env` üzerinden `VITE_ALLOWED_ADMIN_DOMAINS` ile yönetebiliriz.
      </p>
    </section>
  )
}
