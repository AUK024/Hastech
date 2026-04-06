import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import { ConfirmModal } from '../components/ConfirmModal'
import { useUI } from '../contexts/UIContext'

const emptyForm = {
  email: '',
  display_name: '',
  mailbox_type: 'shared_mailbox',
  is_active: true,
  auto_reply_enabled: true,
  description: '',
}

export function MailboxListPage() {
  const { t } = useUI()
  const [items, setItems] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [filter, setFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedId, setSelectedId] = useState(null)
  const [editingId, setEditingId] = useState(null)

  const load = () => {
    api.get('/mailboxes').then((res) => setItems(res.data)).catch(() => setItems([]))
  }

  useEffect(() => {
    load()
  }, [])

  const filtered = useMemo(() => {
    const q = filter.toLowerCase().trim()
    return items.filter((x) => {
      const searchOk = !q || x.email?.toLowerCase().includes(q) || x.display_name?.toLowerCase().includes(q) || x.mailbox_type?.toLowerCase().includes(q)
      const statusOk = statusFilter === 'all' || (statusFilter === 'active' ? x.is_active : !x.is_active)
      return searchOk && statusOk
    })
  }, [items, filter, statusFilter])

  const submit = async (e) => {
    e.preventDefault()
    await api.post('/mailboxes', form)
    setForm(emptyForm)
    load()
  }

  const saveEdit = async (row) => {
    await api.put(`/mailboxes/${row.id}`, {
      display_name: row.display_name,
      mailbox_type: row.mailbox_type,
      is_active: row.is_active,
      auto_reply_enabled: row.auto_reply_enabled,
      description: row.description,
    })
    setEditingId(null)
    load()
  }

  const removeItem = async () => {
    if (!selectedId) return
    await api.delete(`/mailboxes/${selectedId}`)
    setSelectedId(null)
    load()
  }

  const patchRow = (id, patch) => {
    setItems((prev) => prev.map((x) => (x.id === id ? { ...x, ...patch } : x)))
  }

  return (
    <section>
      <h2>Mailbox List</h2>
      <form onSubmit={submit} style={{ display: 'grid', gap: 8, maxWidth: 560 }}>
        <input placeholder="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <input placeholder="display_name" value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })} required />
        <input placeholder="mailbox_type" value={form.mailbox_type} onChange={(e) => setForm({ ...form, mailbox_type: e.target.value })} required />
        <input placeholder="description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <label><input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /> is_active</label>
        <label><input type="checkbox" checked={form.auto_reply_enabled} onChange={(e) => setForm({ ...form, auto_reply_enabled: e.target.checked })} /> auto_reply_enabled</label>
        <button type="submit">{t('create')}</button>
      </form>

      <div style={{ marginTop: 14, marginBottom: 10, display: 'flex', gap: 8 }}>
        <input placeholder={`${t('filter')}...`} value={filter} onChange={(e) => setFilter(e.target.value)} />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">all</option>
          <option value="active">{t('active')}</option>
          <option value="inactive">{t('inactive')}</option>
        </select>
        <button onClick={() => { setFilter(''); setStatusFilter('all') }}>{t('reset')}</button>
      </div>

      <table border="1" cellPadding="6" style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr><th>Email</th><th>Name</th><th>Type</th><th>Status</th><th>Auto Reply</th><th>Actions</th></tr>
        </thead>
        <tbody>
          {filtered.map((x) => (
            <tr key={x.id}>
              <td>{x.email}</td>
              <td>{editingId === x.id ? <input value={x.display_name} onChange={(e) => patchRow(x.id, { display_name: e.target.value })} /> : x.display_name}</td>
              <td>{editingId === x.id ? <input value={x.mailbox_type} onChange={(e) => patchRow(x.id, { mailbox_type: e.target.value })} /> : x.mailbox_type}</td>
              <td>{editingId === x.id ? <input type="checkbox" checked={x.is_active} onChange={(e) => patchRow(x.id, { is_active: e.target.checked })} /> : (x.is_active ? t('active') : t('inactive'))}</td>
              <td>{editingId === x.id ? <input type="checkbox" checked={x.auto_reply_enabled} onChange={(e) => patchRow(x.id, { auto_reply_enabled: e.target.checked })} /> : String(x.auto_reply_enabled)}</td>
              <td>
                {editingId === x.id ? <button onClick={() => saveEdit(x)}>Save</button> : <button onClick={() => setEditingId(x.id)}>Edit</button>}
                <button style={{ marginLeft: 8 }} onClick={() => setSelectedId(x.id)}>{t('delete')}</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <ConfirmModal open={Boolean(selectedId)} onConfirm={removeItem} onCancel={() => setSelectedId(null)} />
    </section>
  )
}
