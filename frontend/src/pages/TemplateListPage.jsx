import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import { ConfirmModal } from '../components/ConfirmModal'
import { useUI } from '../contexts/UIContext'

const emptyForm = {
  name: '',
  source_language: 'en',
  subject_template: '',
  body_template: '',
  signature_template: '',
  is_active: true,
}

export function TemplateListPage() {
  const { t } = useUI()
  const [items, setItems] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [filter, setFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedId, setSelectedId] = useState(null)
  const [editingId, setEditingId] = useState(null)

  const load = () => {
    api.get('/templates').then((res) => setItems(res.data)).catch(() => setItems([]))
  }

  useEffect(() => { load() }, [])

  const filtered = useMemo(() => {
    const q = filter.toLowerCase().trim()
    return items.filter((x) => {
      const searchOk = !q || x.name?.toLowerCase().includes(q) || x.source_language?.toLowerCase().includes(q) || x.subject_template?.toLowerCase().includes(q)
      const statusOk = statusFilter === 'all' || (statusFilter === 'active' ? x.is_active : !x.is_active)
      return searchOk && statusOk
    })
  }, [items, filter, statusFilter])

  const submit = async (e) => {
    e.preventDefault()
    await api.post('/templates', form)
    setForm(emptyForm)
    load()
  }

  const saveEdit = async (row) => {
    await api.put(`/templates/${row.id}`, {
      name: row.name,
      source_language: row.source_language,
      subject_template: row.subject_template,
      body_template: row.body_template,
      signature_template: row.signature_template,
      is_active: row.is_active,
    })
    setEditingId(null)
    load()
  }

  const removeItem = async () => {
    if (!selectedId) return
    await api.delete(`/templates/${selectedId}`)
    setSelectedId(null)
    load()
  }

  const patchRow = (id, patch) => setItems((prev) => prev.map((x) => (x.id === id ? { ...x, ...patch } : x)))

  return (
    <section>
      <h2>Template List</h2>
      <form onSubmit={submit} style={{ display: 'grid', gap: 8, maxWidth: 640 }}>
        <input placeholder="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <input placeholder="source_language" value={form.source_language} onChange={(e) => setForm({ ...form, source_language: e.target.value })} required />
        <input placeholder="subject_template" value={form.subject_template} onChange={(e) => setForm({ ...form, subject_template: e.target.value })} required />
        <textarea placeholder="body_template" value={form.body_template} onChange={(e) => setForm({ ...form, body_template: e.target.value })} required />
        <textarea placeholder="signature_template" value={form.signature_template} onChange={(e) => setForm({ ...form, signature_template: e.target.value })} />
        <label><input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /> is_active</label>
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
        <thead><tr><th>Name</th><th>Lang</th><th>Subject</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {filtered.map((x) => (
            <tr key={x.id}>
              <td>{editingId === x.id ? <input value={x.name} onChange={(e) => patchRow(x.id, { name: e.target.value })} /> : x.name}</td>
              <td>{editingId === x.id ? <input value={x.source_language} onChange={(e) => patchRow(x.id, { source_language: e.target.value })} /> : x.source_language}</td>
              <td>{editingId === x.id ? <input value={x.subject_template} onChange={(e) => patchRow(x.id, { subject_template: e.target.value })} /> : x.subject_template}</td>
              <td>{editingId === x.id ? <input type="checkbox" checked={x.is_active} onChange={(e) => patchRow(x.id, { is_active: e.target.checked })} /> : (x.is_active ? t('active') : t('inactive'))}</td>
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
