import { Routes, Route, Link } from 'react-router-dom'
import { routes } from './pages/routes'
import { AppLayout } from './layouts/AppLayout'
import { useUI } from './contexts/UIContext'

export default function App() {
  const { theme } = useUI()
  const isDark = theme === 'dark'

  return (
    <AppLayout>
      <nav style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 16 }}>
        {routes.map((r) => (
          <Link
            key={r.path}
            to={r.path}
            style={{
              textDecoration: 'none',
              padding: '6px 10px',
              borderRadius: 8,
              background: isDark ? '#1f2937' : '#ffffff',
              color: isDark ? '#e5e7eb' : '#111827',
              border: `1px solid ${isDark ? '#374151' : '#d1d5db'}`,
            }}
          >
            {r.label}
          </Link>
        ))}
      </nav>
      <Routes>
        {routes.map((r) => (
          <Route key={r.path} path={r.path} element={<r.component />} />
        ))}
      </Routes>
    </AppLayout>
  )
}
