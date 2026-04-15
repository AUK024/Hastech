import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'

export function SettingsPage() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState({ setting_key: '', setting_value: '', description: '' })

  useEffect(() => {
    api.get('/settings').then((res) => setItems(res.data)).catch(() => setItems([]))
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    const res = await api.post('/settings/upsert', form)
    setItems((prev) => {
      const next = prev.filter((x) => x.setting_key !== res.data.setting_key)
      return [...next, res.data]
    })
    setForm({ setting_key: '', setting_value: '', description: '' })
  }

  return (
    <section>
      <h2>Settings</h2>
      <p style={{ marginTop: 0 }}>
        Header görsel/metin ayarları için <Link to="/settings/custom-ux">Custom UX</Link> sayfasını kullanın.
      </p>
      <form onSubmit={submit} style={{ display: 'grid', gap: 8, maxWidth: 520 }}>
        <input placeholder="setting_key" value={form.setting_key} onChange={(e) => setForm({ ...form, setting_key: e.target.value })} required />
        <input placeholder="setting_value" value={form.setting_value} onChange={(e) => setForm({ ...form, setting_value: e.target.value })} required />
        <input placeholder="description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <button type="submit">Upsert</button>
      </form>
      <ul>
        {items.map((x) => <li key={x.id}><strong>{x.setting_key}</strong>: {x.setting_value}</li>)}
      </ul>
    </section>
  )
}
