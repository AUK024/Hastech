import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './contexts/AuthContext'
import { UIProvider } from './contexts/UIContext'
import { CustomUxProvider } from './contexts/CustomUxContext'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <UIProvider>
      <AuthProvider>
        <CustomUxProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </CustomUxProvider>
      </AuthProvider>
    </UIProvider>
  </React.StrictMode>
)
