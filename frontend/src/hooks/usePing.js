import { useEffect, useState } from 'react'
import { api } from '../services/api'

export function usePing() {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    api.get('/dashboard/')
      .then(() => setStatus('ok'))
      .catch(() => setStatus('error'))
  }, [])

  return status
}
