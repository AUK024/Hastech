import { NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { routes } from './pages/routes'
import { AppLayout } from './layouts/AppLayout'
import { useAuth } from './contexts/AuthContext'
import { useUI } from './contexts/UIContext'

export default function App() {
  const { theme } = useUI()
  const { user, isAuthenticated, logout } = useAuth()
  const location = useLocation()
  const isDark = theme === 'dark'
  const isAdmin = user?.role === 'admin'

  const canAccessRoute = (route) => !route.adminOnly || isAdmin
  const sidebarRoutes = routes.filter((r) => !r.public && r.sidebar !== false && canAccessRoute(r))
  const sectionOrder = ['Overview', 'Operations', 'Logs', 'Reports', 'System']

  const sections = sectionOrder
    .map((sectionName) => ({
      name: sectionName,
      items: sidebarRoutes.filter((r) => r.category === sectionName),
    }))
    .filter((section) => section.items.length > 0)

  const sidebar = (
    <nav style={{ display: 'grid', gap: 14 }}>
      {sections.map((section) => (
        <section key={section.name}>
          <h3 style={{ margin: '0 0 8px 0', fontSize: 12, letterSpacing: 0.6, opacity: 0.75 }}>
            {section.name}
          </h3>
          <div style={{ display: 'grid', gap: 8 }}>
            {section.items.map((r) => {
              const isSettingsChild = r.path.startsWith('/settings/') && r.path !== '/settings'
              return (
              <NavLink
                key={r.path}
                to={r.path}
                end={r.path === '/settings'}
                style={({ isActive }) => ({
                  textDecoration: 'none',
                  padding: isSettingsChild ? '8px 10px 8px 24px' : '8px 10px',
                  borderRadius: 8,
                  border: `1px solid ${isDark ? '#374151' : '#d1d5db'}`,
                  background: isActive ? (isDark ? '#0f766e' : '#ccfbf1') : (isDark ? '#111827' : '#f8fafc'),
                  color: isDark ? '#e5e7eb' : '#111827',
                  fontWeight: isActive ? 700 : 500,
                })}
              >
                {isSettingsChild ? `↳ ${r.label}` : r.label}
              </NavLink>
              )
            })}
          </div>
        </section>
      ))}
    </nav>
  )

  return (
    <AppLayout sidebar={isAuthenticated ? sidebar : null} user={user} onLogout={logout}>
      <Routes>
        {routes.map((r) => {
          const element = <r.component />
          if (r.public) {
            if (r.path === '/login') {
              return (
                <Route
                  key={r.path}
                  path={r.path}
                  element={isAuthenticated ? <Navigate to="/" replace /> : element}
                />
              )
            }
            return <Route key={r.path} path={r.path} element={element} />
          }
          return (
            <Route
              key={r.path}
              path={r.path}
              element={
                isAuthenticated ? (
                  canAccessRoute(r) ? (
                    element
                  ) : (
                    <Navigate to="/" replace />
                  )
                ) : (
                  <Navigate to="/login" replace state={{ from: location }} />
                )
              }
            />
          )
        })}
        <Route path="*" element={<Navigate to={isAuthenticated ? '/' : '/login'} replace />} />
      </Routes>
    </AppLayout>
  )
}
