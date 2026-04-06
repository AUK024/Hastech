import { useUI } from '../contexts/UIContext'

export function ConfirmModal({ open, onConfirm, onCancel, message }) {
  const { theme, t } = useUI()
  if (!open) return null

  const isDark = theme === 'dark'
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.45)',
      display: 'grid',
      placeItems: 'center',
      zIndex: 2000,
    }}>
      <div style={{
        width: 420,
        maxWidth: '92vw',
        borderRadius: 12,
        padding: 16,
        background: isDark ? '#1f2937' : '#ffffff',
        color: isDark ? '#e5e7eb' : '#111827',
      }}>
        <h3 style={{ marginTop: 0 }}>{t('confirm_delete_title')}</h3>
        <p>{message || t('confirm_delete_message')}</p>
        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button onClick={onCancel}>{t('cancel')}</button>
          <button onClick={onConfirm}>{t('delete')}</button>
        </div>
      </div>
    </div>
  )
}
