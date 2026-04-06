import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function WebhookLogsPage() {
  const [items, setItems] = useState([])

  useEffect(() => {
    api.get('/logs/webhook').then((res) => setItems(res.data)).catch(() => setItems([]))
  }, [])

  return (
    <section>
      <h2>Webhook Logs</h2>
      <ul>
        {items.map((x) => <li key={x.id}>{x.event_type} | {x.status}</li>)}
      </ul>
    </section>
  )
}
