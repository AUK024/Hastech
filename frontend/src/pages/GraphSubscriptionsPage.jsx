import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'

export function GraphSubscriptionsPage() {
  const [subscriptions, setSubscriptions] = useState([])
  const [mailboxes, setMailboxes] = useState([])
  const [selectedMailboxId, setSelectedMailboxId] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [actionLoading, setActionLoading] = useState(false)
  const [lastBatch, setLastBatch] = useState(null)

  const mailboxById = useMemo(
    () =>
      mailboxes.reduce((acc, item) => {
        acc[item.id] = item
        return acc
      }, {}),
    [mailboxes],
  )

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [subscriptionsRes, mailboxesRes] = await Promise.all([
        api.get('/graph-subscriptions'),
        api.get('/mailboxes'),
      ])
      setSubscriptions(subscriptionsRes.data || [])
      const activeMailboxes = (mailboxesRes.data || []).filter((item) => item.is_active)
      setMailboxes(activeMailboxes)
      if (!selectedMailboxId && activeMailboxes.length > 0) {
        setSelectedMailboxId(String(activeMailboxes[0].id))
      }
    } catch (err) {
      const status = err?.response?.status
      setError(status === 403 ? 'Bu ekran sadece admin kullanıcıya açıktır.' : 'Graph subscription verisi alınamadı.')
      setSubscriptions([])
      setMailboxes([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const runBatch = async (endpoint) => {
    setActionLoading(true)
    setError('')
    setNotice('')
    try {
      const res = await api.post(endpoint)
      const payload = res.data || {}
      setLastBatch(payload)
      setNotice(`İşlem tamamlandı: ${payload.success || 0}/${payload.total || 0} başarılı`)
      await load()
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(detail || 'Batch işlem başarısız oldu.')
    } finally {
      setActionLoading(false)
    }
  }

  const runMailboxAction = async (action) => {
    if (!selectedMailboxId) {
      setError('Önce mailbox seçin.')
      return
    }

    setActionLoading(true)
    setError('')
    setNotice('')
    try {
      if (action === 'subscribe') {
        await api.post(`/graph-subscriptions/mailboxes/${selectedMailboxId}/subscribe`)
        setNotice('Mailbox subscription güncellendi.')
      } else if (action === 'force-recreate') {
        await api.post(`/graph-subscriptions/mailboxes/${selectedMailboxId}/subscribe?force_recreate=true`)
        setNotice('Mailbox subscription yeniden oluşturuldu.')
      } else if (action === 'renew') {
        await api.post(`/graph-subscriptions/mailboxes/${selectedMailboxId}/renew`)
        setNotice('Mailbox subscription yenilendi.')
      } else if (action === 'delete') {
        await api.delete(`/graph-subscriptions/mailboxes/${selectedMailboxId}`)
        setNotice('Mailbox subscription kaldırıldı.')
      }
      await load()
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(detail || 'Mailbox aksiyonu başarısız oldu.')
    } finally {
      setActionLoading(false)
    }
  }

  return (
    <section>
      <h2>Graph Subscriptions</h2>
      <p style={{ marginTop: 0 }}>
        Aktif mailboxlar için Microsoft Graph subscription kayıtlarını bu ekrandan oluşturup yenileyebilirsiniz.
      </p>

      <div style={{ display: 'grid', gap: 8, maxWidth: 760 }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button disabled={actionLoading} onClick={() => runBatch('/graph-subscriptions/sync')}>
            Aktif Mailboxları Senkronize Et
          </button>
          <button disabled={actionLoading} onClick={() => runBatch('/graph-subscriptions/renew-due')}>
            Süresi Yakın Olanları Yenile
          </button>
        </div>

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <select value={selectedMailboxId} onChange={(e) => setSelectedMailboxId(e.target.value)}>
            {mailboxes.map((mailbox) => (
              <option key={mailbox.id} value={mailbox.id}>
                {mailbox.email}
              </option>
            ))}
            {mailboxes.length === 0 ? <option value="">Aktif mailbox bulunamadı</option> : null}
          </select>
          <button disabled={actionLoading || !selectedMailboxId} onClick={() => runMailboxAction('subscribe')}>
            Subscribe / Renew
          </button>
          <button disabled={actionLoading || !selectedMailboxId} onClick={() => runMailboxAction('force-recreate')}>
            Yeniden Oluştur
          </button>
          <button disabled={actionLoading || !selectedMailboxId} onClick={() => runMailboxAction('renew')}>
            Sadece Yenile
          </button>
          <button disabled={actionLoading || !selectedMailboxId} onClick={() => runMailboxAction('delete')}>
            Kaldır
          </button>
        </div>
      </div>

      {notice ? <p style={{ color: '#0f766e' }}>{notice}</p> : null}
      {error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table border="1" cellPadding="6" style={{ borderCollapse: 'collapse', width: '100%', marginTop: 12 }}>
          <thead>
            <tr>
              <th>Mailbox</th>
              <th>Subscription ID</th>
              <th>Resource</th>
              <th>Active</th>
              <th>Expiration</th>
              <th>Last Renew</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {subscriptions.map((item) => (
              <tr key={item.id}>
                <td>{mailboxById[item.mailbox_id]?.email || `mailbox:${item.mailbox_id}`}</td>
                <td>{item.graph_subscription_id || '-'}</td>
                <td>{item.resource}</td>
                <td>{item.is_active ? 'yes' : 'no'}</td>
                <td>{item.expiration_datetime || '-'}</td>
                <td>{item.last_renewed_at || '-'}</td>
                <td>{item.error_message || '-'}</td>
              </tr>
            ))}
            {subscriptions.length === 0 ? (
              <tr>
                <td colSpan="7">Kayıt bulunamadı.</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      )}

      {lastBatch?.results?.length ? (
        <>
          <h3 style={{ marginTop: 16 }}>Son Batch Sonucu</h3>
          <table border="1" cellPadding="6" style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr>
                <th>Mailbox</th>
                <th>Durum</th>
                <th>Subscription</th>
                <th>Expiration</th>
                <th>Hata</th>
              </tr>
            </thead>
            <tbody>
              {lastBatch.results.map((row, idx) => (
                <tr key={`${row.mailbox_id}-${idx}`}>
                  <td>{row.mailbox_email}</td>
                  <td>{row.status}</td>
                  <td>{row.subscription_id || '-'}</td>
                  <td>{row.expiration_datetime || '-'}</td>
                  <td>{row.error || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : null}
    </section>
  )
}
