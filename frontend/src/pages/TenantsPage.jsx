import { useEffect, useState } from 'react'
import { api } from '../services/api'

const emptyForm = {
  tenant_code: '',
  display_name: '',
  is_active: true,
  description: '',
}

export function TenantsPage() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState(null)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/tenants')
      setItems(res.data || [])
    } catch (err) {
      const status = err?.response?.status
      setItems([])
      setError(status === 403 ? 'Bu ekran sadece admin kullanıcıya açıktır.' : 'Tenant listesi alınamadı.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/tenants', {
        tenant_code: form.tenant_code,
        display_name: form.display_name,
        is_active: form.is_active,
        description: form.description || null,
      })
      setForm(emptyForm)
      await load()
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(detail || 'Tenant oluşturulamadı.')
    }
  }

  const patchRow = (id, patch) => {
    setItems((prev) => prev.map((x) => (x.id === id ? { ...x, ...patch } : x)))
  }

  const saveEdit = async (row) => {
    setError('')
    try {
      await api.put(`/tenants/${row.id}`, {
        display_name: row.display_name,
        is_active: row.is_active,
        description: row.description || null,
      })
      setEditingId(null)
      await load()
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(detail || 'Tenant güncellenemedi.')
    }
  }

  const removeItem = async (row) => {
    if (!window.confirm(`${row.tenant_code} tenant kaydı silinsin mi?`)) {
      return
    }
    setError('')
    try {
      await api.delete(`/tenants/${row.id}`)
      await load()
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(detail || 'Tenant silinemedi.')
    }
  }

  return (
    <section>
      <h2>Tenants</h2>
      <p style={{ marginTop: 0 }}>
        Farklı firma/kurumlar için tenant tanımı yaparak platformu çoklu müşteri yapısına hazırlayabilirsiniz.
      </p>

      <form onSubmit={submit} style={{ display: 'grid', gap: 8, maxWidth: 560 }}>
        <input
          placeholder="tenant_code (ornek: hascelik)"
          value={form.tenant_code}
          onChange={(e) => setForm({ ...form, tenant_code: e.target.value })}
          required
        />
        <input
          placeholder="display_name"
          value={form.display_name}
          onChange={(e) => setForm({ ...form, display_name: e.target.value })}
          required
        />
        <input
          placeholder="description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <label>
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
          />{' '}
          active
        </label>
        <button type="submit">Tenant Ekle</button>
      </form>

      {error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <table border="1" cellPadding="6" style={{ borderCollapse: 'collapse', width: '100%', marginTop: 14 }}>
          <thead>
            <tr>
              <th>Tenant Code</th>
              <th>Display Name</th>
              <th>Description</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((x) => (
              <tr key={x.id}>
                <td>{x.tenant_code}</td>
                <td>
                  {editingId === x.id ? (
                    <input value={x.display_name} onChange={(e) => patchRow(x.id, { display_name: e.target.value })} />
                  ) : (
                    x.display_name
                  )}
                </td>
                <td>
                  {editingId === x.id ? (
                    <input value={x.description || ''} onChange={(e) => patchRow(x.id, { description: e.target.value })} />
                  ) : (
                    x.description || '-'
                  )}
                </td>
                <td>
                  {editingId === x.id ? (
                    <input type="checkbox" checked={Boolean(x.is_active)} onChange={(e) => patchRow(x.id, { is_active: e.target.checked })} />
                  ) : x.is_active ? (
                    'active'
                  ) : (
                    'inactive'
                  )}
                </td>
                <td>
                  {editingId === x.id ? (
                    <button onClick={() => saveEdit(x)}>Kaydet</button>
                  ) : (
                    <button onClick={() => setEditingId(x.id)}>Düzenle</button>
                  )}
                  <button style={{ marginLeft: 8 }} onClick={() => removeItem(x)}>
                    Sil
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 ? (
              <tr>
                <td colSpan="5">Kayıt bulunamadı.</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      )}
    </section>
  )
}
