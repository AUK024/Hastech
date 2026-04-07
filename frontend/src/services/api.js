import axios from 'axios'

const defaultApiBaseUrl = () => {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()
  if (configuredBaseUrl) {
    return configuredBaseUrl
  }

  if (typeof window === 'undefined') {
    return 'http://localhost:8000/api/v1'
  }

  const { protocol, hostname, port, origin } = window.location
  if (port === '5173') {
    return `${protocol}//${hostname}:8000/api/v1`
  }

  return `${origin}/api/v1`
}

export const api = axios.create({
  baseURL: defaultApiBaseUrl(),
})
