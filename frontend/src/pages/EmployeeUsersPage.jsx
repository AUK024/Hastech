import { useEffect, useState } from 'react'
import { api } from '../services/api'

const emptyForm = {
  email: '',
  full_name: '',
  is_active: true,
}

export function EmployeeUsersPage() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [editingId, setEditingId] = useState(null)

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/employee-users')
      setItems(res.data)
    } catch (err) {
      const status = err?.response?.status
      setItems([])
      setError(status === 403 ? 'Bu ekran sadece admin kullanıcıya açıktır.' : 'Employee kullanıcı listesi alınamadı.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      await api.post('/employee-users', {
        email: form.email,
        full_name: form.full_name || null,
        is_active: form.is_active,
      })
      setForm(emptyForm)
      await load()
    } catch (err) {
      const status = err?.response?.status
      const detail = err?.response?.data?.detail
      if (status === 409) {
        setError(detail || 'Bu e-posta zaten kayıtlı.')
      } else if (status === 403) {
        setError('Bu işlem sadece admin kullanıcıya açıktır.')
      } else {
        setError('Employee kullanıcı oluşturulamadı.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  const patchRow = (id, patch) => {
    setItems((prev) => prev.map((x) => (x.id === id ? { ...x, ...patch } : x)))
  }

  const saveEdit = async (row) => {
    setError('')
    try {
      await api.put(`/employee-users/${row.id}`, {
        full_name: row.full_name || null,
        is_active: row.is_active,
      })
      setEditingId(null)
      await load()
    } catch (err) {
      const status = err?.response?.status
      setError(status === 403 ? 'Bu işlem sadece admin kullanıcıya açıktır.' : 'Employee kullanıcı güncellenemedi.')
    }
  }

  const removeItem = async (row) => {
    if (!window.confirm(`${row.email} kullanıcısını silmek istiyor musunuz?`)) {
      return
    }
    setError('')
    try {
      await api.delete(`/employee-users/${row.id}`)
      await load()
    } catch (err) {
      const status = err?.response?.status
      setError(status === 403 ? 'Bu işlem sadece admin kullanıcıya açıktır.' : 'Employee kullanıcı silinemedi.')
    }
  }

  return (
    <section>
      <h2>Employee Users</h2>
      <p style={{ marginTop: 0 }}>
        Admin kullanıcı bu ekrandan employee kullanıcı ekler. Employee panel erişimi yalnızca bu listede aktif olan e-postalara verilir.
      </p>

      <form onSubmit={submit} style={{ display: 'grid', gap: 8, maxWidth: 560 }}>
        <input
          type="email"
          placeholder="employee@hascelik.com"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          required
        />
        <input
          placeholder="Ad Soyad (opsiyonel)"
          value={form.full_name}
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
        />
        <label>
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
          />{' '}
          active
        </label>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Kaydediliyor...' : 'Employee Ekle'}
        </button>
      </form>

      {error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <table border="1" cellPadding="6" style={{ borderCollapse: 'collapse', width: '100%', marginTop: 14 }}>
          <thead>
            <tr>
              <th>Email</th>
              <th>Ad Soyad</th>
              <th>Durum</th>
              <th>Oluşturan Admin</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {items.map((x) => (
              <tr key={x.id}>
                <td>{x.email}</td>
                <td>
                  {editingId === x.id ? (
                    <input
                      value={x.full_name || ''}
                      onChange={(e) => patchRow(x.id, { full_name: e.target.value })}
                    />
                  ) : (
                    x.full_name || '-'
                  )}
                </td>
                <td>
                  {editingId === x.id ? (
                    <input
                      type="checkbox"
                      checked={Boolean(x.is_active)}
                      onChange={(e) => patchRow(x.id, { is_active: e.target.checked })}
                    />
                  ) : x.is_active ? (
                    'active'
                  ) : (
                    'inactive'
                  )}
                </td>
                <td>{x.created_by}</td>
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
