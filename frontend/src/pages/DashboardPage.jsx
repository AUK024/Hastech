import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function DashboardPage() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get('/dashboard').then((res) => setData(res.data)).catch(() => setData(null))
  }, [])

  return (
    <section>
      <h2>Dashboard</h2>
      {!data && <p>Loading...</p>}
      {data && (
        <ul>
          <li>Daily incoming: {data.daily_incoming}</li>
          <li>Daily external: {data.daily_external}</li>
          <li>Auto reply sent: {data.daily_auto_reply_sent}</li>
          <li>Error count: {data.daily_errors}</li>
        </ul>
      )}
    </section>
  )
}
