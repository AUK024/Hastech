import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import { ConfirmModal } from '../components/ConfirmModal'
import { useUI } from '../contexts/UIContext'

const emptyForm = {
  rule_type: 'domain',
  rule_value: '',
  description: '',
  is_active: true,
}

export function BlockedRulesListPage() {
  const { t } = useUI()
  const [items, setItems] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [filter, setFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedId, setSelectedId] = useState(null)
  const [editingId, setEditingId] = useState(null)

  const load = () => api.get('/blocked-rules').then((res) => setItems(res.data)).catch(() => setItems([]))

  useEffect(() => { load() }, [])

  const filtered = useMemo(() => {
    const q = filter.toLowerCase().trim()
    return items.filter((x) => {
      const searchOk = !q || x.rule_type?.toLowerCase().includes(q) || x.rule_value?.toLowerCase().includes(q) || x.description?.toLowerCase().includes(q)
      const statusOk = statusFilter === 'all' || (statusFilter === 'active' ? x.is_active : !x.is_active)
      return searchOk && statusOk
    })
  }, [items, filter, statusFilter])

  const submit = async (e) => {
    e.preventDefault()
    await api.post('/blocked-rules', form)
    setForm(emptyForm)
    load()
  }

  const saveEdit = async (row) => {
    await api.put(`/blocked-rules/${row.id}`, {
      rule_type: row.rule_type,
      rule_value: row.rule_value,
      description: row.description,
      is_active: row.is_active,
    })
    setEditingId(null)
    load()
  }

  const removeItem = async () => {
    if (!selectedId) return
    await api.delete(`/blocked-rules/${selectedId}`)
    setSelectedId(null)
    load()
  }

  const patchRow = (id, patch) => setItems((prev) => prev.map((x) => (x.id === id ? { ...x, ...patch } : x)))

  return (
    <section>
      <h2>Blocked Rules List</h2>
      <form onSubmit={submit} style={{ display: 'grid', gap: 8, maxWidth: 520 }}>
        <input placeholder="rule_type" value={form.rule_type} onChange={(e) => setForm({ ...form, rule_type: e.target.value })} required />
        <input placeholder="rule_value" value={form.rule_value} onChange={(e) => setForm({ ...form, rule_value: e.target.value })} required />
        <input placeholder="description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
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
        <thead><tr><th>Type</th><th>Value</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {filtered.map((x) => (
            <tr key={x.id}>
              <td>{editingId === x.id ? <input value={x.rule_type} onChange={(e) => patchRow(x.id, { rule_type: e.target.value })} /> : x.rule_type}</td>
              <td>{editingId === x.id ? <input value={x.rule_value} onChange={(e) => patchRow(x.id, { rule_value: e.target.value })} /> : x.rule_value}</td>
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
