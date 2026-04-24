import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { store } from '@/app/store'
import App from '@/App'
import ErrorBoundary from '@/components/common/ErrorBoundary'
import { ToastProvider } from '@/components/common/Toast'
import '@/index.css'
import '@/i18n'

// 启动 MSW Mock
async function startMockServer() {
  if (import.meta.env.VITE_USE_MSW === 'true') {
    const { startWorker } = await import('@/mocks/browser')
    await startWorker()
  }
}

startMockServer()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <ErrorBoundary>
          <ToastProvider>
            <App />
          </ToastProvider>
        </ErrorBoundary>
      </BrowserRouter>
    </Provider>
  </React.StrictMode>,
)
