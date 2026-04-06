import { useUI } from '../contexts/UIContext'

export function AppLayout({ children }) {
  const { theme, setTheme, lang, setLang, t } = useUI()
  const isDark = theme === 'dark'

  return (
    <div style={{
      fontFamily: 'Inter, Arial, sans-serif',
      padding: 20,
      minHeight: '100vh',
      background: isDark ? '#111827' : '#f5f7fb',
      color: isDark ? '#e5e7eb' : '#111827',
      transition: 'all .2s ease',
    }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1 style={{ margin: 0 }}>Hascelik Mail Automation Admin</h1>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <label>{t('language')}:</label>
          <select value={lang} onChange={(e) => setLang(e.target.value)}>
            <option value="tr">TR</option>
            <option value="en">EN</option>
          </select>
          <button onClick={() => setTheme(isDark ? 'light' : 'dark')}>
            {isDark ? t('theme_light') : t('theme_dark')}
          </button>
        </div>
      </header>
      {children}
    </div>
  )
}
