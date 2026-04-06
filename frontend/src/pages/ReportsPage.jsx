import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function ReportsPage() {
  const [domains, setDomains] = useState([])

  useEffect(() => {
    api.get('/reports/domains').then((res) => setDomains(res.data.top_domains || [])).catch(() => setDomains([]))
  }, [])

  return (
    <section>
      <h2>Reports</h2>
      <h3>Top Domains</h3>
      <ul>
        {domains.map((x) => <li key={x.domain}>{x.domain} ({x.count})</li>)}
      </ul>
    </section>
  )
}
