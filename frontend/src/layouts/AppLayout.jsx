import { useEffect, useState } from 'react'
import { useUI } from '../contexts/UIContext'
import { useCustomUx } from '../contexts/CustomUxContext'
import { APP_NAME } from '../utils/constants'

export function AppLayout({ children, sidebar, user, onLogout }) {
  const { theme, setTheme, lang, setLang, t } = useUI()
  const { headerTitle, headerLogoUrl } = useCustomUx()
  const isDark = theme === 'dark'
  const [logoLoadFailed, setLogoLoadFailed] = useState(false)
  const resolvedHeaderTitle = (headerTitle || '').trim() || `${APP_NAME} Admin`
  const showLogoImage = Boolean(headerLogoUrl) && !logoLoadFailed

  useEffect(() => {
    setLogoLoadFailed(false)
  }, [headerLogoUrl])

  return (
    <div style={{
      fontFamily: 'Inter, Arial, sans-serif',
      padding: 20,
      minHeight: '100vh',
      background: isDark ? '#111827' : '#f5f7fb',
      color: isDark ? '#e5e7eb' : '#111827',
      transition: 'all .2s ease',
    }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, gap: 12, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 10,
              border: `1px solid ${isDark ? '#374151' : '#d1d5db'}`,
              background: isDark ? '#111827' : '#ffffff',
              display: 'grid',
              placeItems: 'center',
              overflow: 'hidden',
              flexShrink: 0,
            }}
          >
            {showLogoImage ? (
              <img
                src={headerLogoUrl}
                alt="Header Logo"
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                onError={(e) => {
                  setLogoLoadFailed(true)
                }}
              />
            ) : (
              <span style={{ fontSize: 10, opacity: 0.75 }}>Logo</span>
            )}
          </div>
          <h1 style={{ margin: 0, fontSize: 28, lineHeight: 1.1, wordBreak: 'break-word' }}>
            {resolvedHeaderTitle}
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <label>{t('language')}:</label>
          <select value={lang} onChange={(e) => setLang(e.target.value)}>
            <option value="tr">TR</option>
            <option value="en">EN</option>
          </select>
          <button onClick={() => setTheme(isDark ? 'light' : 'dark')}>
            {isDark ? t('theme_light') : t('theme_dark')}
          </button>
          {user ? (
            <>
              <span style={{ padding: '4px 8px', borderRadius: 8, border: `1px solid ${isDark ? '#374151' : '#d1d5db'}` }}>
                {user.email} ({user.role || 'employee'})
              </span>
              <button onClick={onLogout}>{t('logout')}</button>
            </>
          ) : null}
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: sidebar ? '260px minmax(0, 1fr)' : '1fr', gap: 16 }}>
        {sidebar ? (
          <aside
            style={{
              alignSelf: 'start',
              position: 'sticky',
              top: 20,
              padding: 12,
              borderRadius: 12,
              border: `1px solid ${isDark ? '#374151' : '#d1d5db'}`,
              background: isDark ? '#1f2937' : '#ffffff',
            }}
          >
            {sidebar}
          </aside>
        ) : null}

        <main
          style={{
            minWidth: 0,
            padding: 16,
            borderRadius: 12,
            border: `1px solid ${isDark ? '#374151' : '#d1d5db'}`,
            background: isDark ? '#1f2937' : '#ffffff',
          }}
        >
          {children}
        </main>
      </div>
    </div>
  )
}
