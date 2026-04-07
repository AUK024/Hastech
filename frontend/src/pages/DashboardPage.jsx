import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function DashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let isCancelled = false

    const loadDashboard = async () => {
      setLoading(true)
      setError('')
      try {
        const res = await api.get('/dashboard/')
        if (!isCancelled) {
          setData(res.data)
        }
      } catch (err) {
        if (!isCancelled) {
          setData(null)
          const status = err?.response?.status
          setError(
            status
              ? `Dashboard verisi alınamadı (HTTP ${status}). API bağlantısını kontrol edin.`
              : 'Dashboard verisi alınamadı. API bağlantısını kontrol edin.',
          )
        }
      } finally {
        if (!isCancelled) {
          setLoading(false)
        }
      }
    }

    loadDashboard()
    return () => {
      isCancelled = true
    }
  }, [])

  return (
    <section>
      <h2>Dashboard</h2>
      {loading && <p>Loading...</p>}
      {!loading && error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}
      {data && (
        <>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: 12,
              marginBottom: 14,
            }}
          >
            <article style={{ border: '1px solid #d1d5db', borderRadius: 10, padding: 12 }}>
              <h3 style={{ marginTop: 0, marginBottom: 6 }}>Gelen Mail Sayısı</h3>
              <strong style={{ fontSize: 28 }}>{data.incoming_mail_count ?? data.daily_incoming ?? 0}</strong>
            </article>
            <article style={{ border: '1px solid #d1d5db', borderRadius: 10, padding: 12 }}>
              <h3 style={{ marginTop: 0, marginBottom: 6 }}>Dönüş Yapılan Mail Sayısı</h3>
              <strong style={{ fontSize: 28 }}>{data.replied_mail_count ?? data.daily_auto_reply_sent ?? 0}</strong>
            </article>
          </div>

          <ul>
            <li>External mail count: {data.daily_external}</li>
            <li>Error count: {data.daily_errors}</li>
          </ul>
        </>
      )}
      {!loading && !error && !data ? <p>Dashboard verisi bulunamadı.</p> : null}
    </section>
  )
}
