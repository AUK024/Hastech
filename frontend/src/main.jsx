import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { UIProvider } from './contexts/UIContext'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <UIProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </UIProvider>
  </React.StrictMode>
)
