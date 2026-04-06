import { createContext, useContext, useMemo, useState } from 'react'

const UIContext = createContext(null)

const dictionary = {
  tr: {
    theme_dark: 'Koyu Tema',
    theme_light: 'Açık Tema',
    language: 'Dil',
    filter: 'Filtre',
    reset: 'Temizle',
    delete: 'Sil',
    create: 'Oluştur',
    logout: 'Çıkış',
    cancel: 'İptal',
    confirm_delete_title: 'Silme Onayı',
    confirm_delete_message: 'Bu kaydı silmek istediğinize emin misiniz?',
    active: 'Aktif',
    inactive: 'Pasif',
  },
  en: {
    theme_dark: 'Dark Theme',
    theme_light: 'Light Theme',
    language: 'Language',
    filter: 'Filter',
    reset: 'Reset',
    delete: 'Delete',
    create: 'Create',
    logout: 'Logout',
    cancel: 'Cancel',
    confirm_delete_title: 'Delete Confirmation',
    confirm_delete_message: 'Are you sure you want to delete this record?',
    active: 'Active',
    inactive: 'Inactive',
  },
}

export function UIProvider({ children }) {
  const [theme, setTheme] = useState('light')
  const [lang, setLang] = useState('tr')

  const value = useMemo(() => ({
    theme,
    setTheme,
    lang,
    setLang,
    t: (key) => dictionary[lang]?.[key] || key,
  }), [theme, lang])

  return <UIContext.Provider value={value}>{children}</UIContext.Provider>
}

export function useUI() {
  const ctx = useContext(UIContext)
  if (!ctx) {
    throw new Error('useUI must be used within UIProvider')
  }
  return ctx
}
