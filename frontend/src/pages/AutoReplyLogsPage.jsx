import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function AutoReplyLogsPage() {
  const [items, setItems] = useState([])

  useEffect(() => {
    api.get('/auto-reply-logs').then((res) => setItems(res.data)).catch(() => setItems([]))
  }, [])

  return (
    <section>
      <h2>Auto Reply Logs</h2>
      <ul>
        {items.map((x) => <li key={x.id}>incoming#{x.incoming_email_id} | sent: {String(x.reply_sent)} | lang: {x.target_language || '-'}</li>)}
      </ul>
    </section>
  )
}
