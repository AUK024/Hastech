import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function AuditLogsPage() {
  const [items, setItems] = useState([])

  useEffect(() => {
    api.get('/logs/audit').then((res) => setItems(res.data)).catch(() => setItems([]))
  }, [])

  return (
    <section>
      <h2>Audit Logs</h2>
      <ul>
        {items.map((x) => <li key={x.id}>{x.module_name}.{x.action_name} {'->'} {x.result}</li>)}
      </ul>
    </section>
  )
}
