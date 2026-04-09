import axios from 'axios'
import { AUTH_STORAGE_KEY } from '../utils/constants'

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

const configuredTenantCode = (import.meta.env.VITE_TENANT_CODE || '').trim().toLowerCase() || 'default'

export const api = axios.create({
  baseURL: defaultApiBaseUrl(),
})

api.interceptors.request.use((config) => {
  if (typeof window === 'undefined') {
    return config
  }

  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) {
      return config
    }
    const parsed = JSON.parse(raw)
    const email = typeof parsed?.email === 'string' ? parsed.email.toLowerCase() : ''
    if (email) {
      config.headers = config.headers || {}
      config.headers['X-Admin-Email'] = email
    }
  } catch {
    // Ignore session parsing issues and continue request without admin header.
  }

  config.headers = config.headers || {}
  config.headers['X-Tenant-Code'] = configuredTenantCode

  return config
})
