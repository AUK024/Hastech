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
              <h3 style={{ marginTop: 0, marginBottom: 6 }}>Günlük Gelen Mail</h3>
              <strong style={{ fontSize: 28 }}>{data.daily_incoming ?? 0}</strong>
            </article>
            <article style={{ border: '1px solid #d1d5db', borderRadius: 10, padding: 12 }}>
              <h3 style={{ marginTop: 0, marginBottom: 6 }}>Günlük Cevaplanan Mail</h3>
              <strong style={{ fontSize: 28 }}>{data.daily_auto_reply_sent ?? 0}</strong>
            </article>
            <article style={{ border: '1px solid #d1d5db', borderRadius: 10, padding: 12 }}>
              <h3 style={{ marginTop: 0, marginBottom: 6 }}>Toplam Gelen Mail</h3>
              <strong style={{ fontSize: 28 }}>{data.incoming_mail_count ?? 0}</strong>
            </article>
            <article style={{ border: '1px solid #d1d5db', borderRadius: 10, padding: 12 }}>
              <h3 style={{ marginTop: 0, marginBottom: 6 }}>Toplam Cevaplanan Mail</h3>
              <strong style={{ fontSize: 28 }}>{data.replied_mail_count ?? 0}</strong>
            </article>
          </div>

          <ul>
            <li>External mail count: {data.daily_external}</li>
            <li>Error count: {data.daily_errors}</li>
          </ul>

          <h3>Son 14 Gün Trendi</h3>
          <table border="1" cellPadding="6" style={{ borderCollapse: 'collapse', width: '100%', marginBottom: 12 }}>
            <thead>
              <tr>
                <th>Tarih</th>
                <th>Gelen</th>
                <th>Cevaplanan</th>
              </tr>
            </thead>
            <tbody>
              {(data.daily_trend || []).map((row) => (
                <tr key={row.date}>
                  <td>{row.date}</td>
                  <td>{row.incoming_count}</td>
                  <td>{row.replied_count}</td>
                </tr>
              ))}
              {(data.daily_trend || []).length === 0 ? (
                <tr>
                  <td colSpan="3">Veri yok</td>
                </tr>
              ) : null}
            </tbody>
          </table>

          <h3>Günlük Dil Performansı</h3>
          <table border="1" cellPadding="6" style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr>
                <th>Dil</th>
                <th>Gelen</th>
                <th>Cevaplanan</th>
              </tr>
            </thead>
            <tbody>
              {(data.language_performance || []).map((row) => (
                <tr key={row.lang}>
                  <td>{row.lang}</td>
                  <td>{row.incoming_count}</td>
                  <td>{row.replied_count}</td>
                </tr>
              ))}
              {(data.language_performance || []).length === 0 ? (
                <tr>
                  <td colSpan="3">Veri yok</td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </>
      )}
      {!loading && !error && !data ? <p>Dashboard verisi bulunamadı.</p> : null}
    </section>
  )
}
