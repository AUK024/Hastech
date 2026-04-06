import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function IncomingMailLogsPage() {
  const [items, setItems] = useState([])

  useEffect(() => {
    api.get('/incoming-mails').then((res) => setItems(res.data)).catch(() => setItems([]))
  }, [])

  return (
    <section>
      <h2>Incoming Mail Logs</h2>
      <ul>
        {items.map((x) => <li key={x.id}>{x.sender_email} | {x.subject || '-'} | {x.processing_status}</li>)}
      </ul>
    </section>
  )
}
