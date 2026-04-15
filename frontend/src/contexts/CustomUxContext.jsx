import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import { APP_NAME } from '../utils/constants'

const CustomUxContext = createContext(null)

const DEFAULT_HEADER_TITLE = `${APP_NAME} Admin`

const findSettingValue = (items, key, fallback = '') => {
  const row = items.find((item) => item.setting_key === key)
  return row?.setting_value || fallback
}

export function CustomUxProvider({ children }) {
  const [headerTitle, setHeaderTitle] = useState(DEFAULT_HEADER_TITLE)
  const [headerLogoUrl, setHeaderLogoUrl] = useState('')
  const [loading, setLoading] = useState(false)

  const reloadCustomUx = async () => {
    setLoading(true)
    try {
      const response = await api.get('/settings')
      const items = Array.isArray(response.data) ? response.data : []
      setHeaderTitle(findSettingValue(items, 'custom_ux_header_title', DEFAULT_HEADER_TITLE))
      setHeaderLogoUrl(findSettingValue(items, 'custom_ux_header_logo_url', ''))
    } catch {
      setHeaderTitle(DEFAULT_HEADER_TITLE)
      setHeaderLogoUrl('')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    reloadCustomUx()
  }, [])

  const saveCustomUx = async ({ nextHeaderTitle, nextHeaderLogoUrl }) => {
    const title = String(nextHeaderTitle || '').trim() || DEFAULT_HEADER_TITLE
    const logoUrl = String(nextHeaderLogoUrl || '').trim()

    await Promise.all([
      api.post('/settings/upsert', {
        setting_key: 'custom_ux_header_title',
        setting_value: title,
        description: 'Header title text',
      }),
      api.post('/settings/upsert', {
        setting_key: 'custom_ux_header_logo_url',
        setting_value: logoUrl,
        description: 'Header logo image URL',
      }),
    ])

    setHeaderTitle(title)
    setHeaderLogoUrl(logoUrl)
  }

  const value = useMemo(
    () => ({
      headerTitle,
      headerLogoUrl,
      loading,
      reloadCustomUx,
      saveCustomUx,
    }),
    [headerTitle, headerLogoUrl, loading],
  )

  return <CustomUxContext.Provider value={value}>{children}</CustomUxContext.Provider>
}

export function useCustomUx() {
  const ctx = useContext(CustomUxContext)
  if (!ctx) {
    throw new Error('useCustomUx must be used within CustomUxProvider')
  }
  return ctx
}
