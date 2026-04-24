import { setupWorker } from 'msw/browser'
import { authHandlers } from './handlers/auth'
import { documentsHandlers } from './handlers/documents'
import { chatHandlers } from './handlers/chat'
import { foldersHandlers } from './handlers/folders'

const handlers = [
  ...authHandlers,
  ...documentsHandlers,
  ...chatHandlers,
  ...foldersHandlers,
]

export const worker = setupWorker(...handlers)

export async function startWorker(): Promise<void> {
  if (process.env.NODE_ENV === 'development' && import.meta.env.VITE_USE_MSW === 'true') {
    await worker.start({
      onUnhandledRequest: 'bypass',
    })
    console.log('[MSW] Mock API 服务器已启动')
  }
}
