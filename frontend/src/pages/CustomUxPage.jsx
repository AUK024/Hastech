import { useEffect, useRef, useState } from 'react'
import { useCustomUx } from '../contexts/CustomUxContext'
import { APP_NAME } from '../utils/constants'

const DEFAULT_TITLE = `${APP_NAME} Admin`
const MAX_LOGO_SIZE_BYTES = 1024 * 1024
const ALLOWED_LOGO_TYPES = new Set(['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml', 'image/webp'])

const fileToDataUrl = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(new Error('file_read_error'))
    reader.readAsDataURL(file)
  })

export function CustomUxPage() {
  const { headerTitle, headerLogoUrl, loading, saveCustomUx } = useCustomUx()
  const [form, setForm] = useState({
    headerTitle: DEFAULT_TITLE,
    headerLogoUrl: '',
    headerLogoUrlInput: '',
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [previewFailed, setPreviewFailed] = useState(false)
  const logoFileInputRef = useRef(null)

  useEffect(() => {
    setForm({
      headerTitle: headerTitle || DEFAULT_TITLE,
      headerLogoUrl: headerLogoUrl || '',
      headerLogoUrlInput: headerLogoUrl || '',
    })
  }, [headerTitle, headerLogoUrl])

  useEffect(() => {
    setPreviewFailed(false)
  }, [form.headerLogoUrl])

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setMessage('')
    try {
      await saveCustomUx({
        nextHeaderTitle: form.headerTitle,
        nextHeaderLogoUrl: form.headerLogoUrl,
      })
      setMessage('Custom UX ayarları kaydedildi.')
    } catch {
      setError('Ayarlar kaydedilemedi. API bağlantısını kontrol edin.')
    } finally {
      setSaving(false)
    }
  }

  const onLogoUrlChange = (value) => {
    setForm((prev) => ({
      ...prev,
      headerLogoUrlInput: value,
      headerLogoUrl: value.trim(),
    }))
  }

  const onLogoFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) {
      return
    }

    setError('')
    setMessage('')
    if (!ALLOWED_LOGO_TYPES.has((file.type || '').toLowerCase())) {
      setError('Sadece PNG, JPG, SVG veya WEBP dosyaları yüklenebilir.')
      return
    }
    if (file.size > MAX_LOGO_SIZE_BYTES) {
      setError('Logo dosyası en fazla 1MB olmalıdır.')
      return
    }

    try {
      const dataUrl = await fileToDataUrl(file)
      setForm((prev) => ({
        ...prev,
        headerLogoUrl: dataUrl,
        headerLogoUrlInput: '',
      }))
      setMessage('Logo yüklendi. Kaydet butonuna basarak kalıcı hale getirin.')
    } catch {
      setError('Logo dosyası okunamadı.')
    }
  }

  const clearLogo = () => {
    setForm((prev) => ({
      ...prev,
      headerLogoUrl: '',
      headerLogoUrlInput: '',
    }))
    if (logoFileInputRef.current) {
      logoFileInputRef.current.value = ''
    }
  }

  return (
    <section>
      <h2>Custom UX</h2>
      <p style={{ marginTop: 0, opacity: 0.8 }}>
        Header sol üst alanındaki logo ve header metnini buradan yönetebilirsiniz.
      </p>
      <form onSubmit={submit} style={{ display: 'grid', gap: 10, maxWidth: 640 }}>
        <label htmlFor="custom-ux-title">Header Text</label>
        <input
          id="custom-ux-title"
          placeholder={DEFAULT_TITLE}
          value={form.headerTitle}
          onChange={(e) => setForm((prev) => ({ ...prev, headerTitle: e.target.value }))}
          required
        />

        <label htmlFor="custom-ux-logo-url">Logo URL (optional)</label>
        <input
          id="custom-ux-logo-url"
          type="url"
          placeholder="https://example.com/logo.png"
          value={form.headerLogoUrlInput}
          onChange={(e) => onLogoUrlChange(e.target.value)}
        />
        <label htmlFor="custom-ux-logo-file">Logo Upload (PNG/JPG/SVG/WEBP, max 1MB)</label>
        <input
          id="custom-ux-logo-file"
          ref={logoFileInputRef}
          type="file"
          accept=".png,.jpg,.jpeg,.svg,.webp,image/png,image/jpeg,image/svg+xml,image/webp"
          onChange={onLogoFileChange}
        />

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 4 }}>
          <div
            style={{
              width: 60,
              height: 60,
              border: '1px solid #d1d5db',
              borderRadius: 10,
              display: 'grid',
              placeItems: 'center',
              overflow: 'hidden',
              background: '#fff',
            }}
          >
            {form.headerLogoUrl && !previewFailed ? (
              <img
                src={form.headerLogoUrl}
                alt="Logo preview"
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                onError={() => {
                  setPreviewFailed(true)
                }}
              />
            ) : (
              <span style={{ fontSize: 11, opacity: 0.7 }}>Logo</span>
            )}
          </div>
          <div>
            <strong>{form.headerTitle || DEFAULT_TITLE}</strong>
            <p style={{ margin: '6px 0 0 0', fontSize: 13, opacity: 0.75 }}>Header canlı önizleme</p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          <button type="submit" disabled={saving || loading}>
            {saving ? 'Kaydediliyor...' : 'Kaydet'}
          </button>
          <button
            type="button"
            onClick={() => setForm({ headerTitle: DEFAULT_TITLE, headerLogoUrl: '', headerLogoUrlInput: '' })}
            disabled={saving}
          >
            Varsayılanlara Dön
          </button>
          <button type="button" onClick={clearLogo} disabled={saving}>
            Logoyu Temizle
          </button>
        </div>
      </form>
      {message ? <p style={{ color: '#059669' }}>{message}</p> : null}
      {error ? <p style={{ color: '#dc2626' }}>{error}</p> : null}
    </section>
  )
}
