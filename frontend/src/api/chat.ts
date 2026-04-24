import { apiGet, apiPost, apiDelete } from './client'
import type { ChatSession, ChatResponse, ChatHistoryData } from '@/types/chat'

export interface ChatRequest {
  message: string
  documentIds: string[]
  chatId?: string
}

export const chatApi = {
  getSessions: (page?: number, pageSize?: number) =>
    apiGet<ChatHistoryData>('/chat/sessions', {
      params: { page, pageSize },
    }),
  createSession: (documentIds: string[]) =>
    apiPost<ChatSession>('/chat/sessions', { documentIds }),
  getMessages: (chatId: string, page?: number, pageSize?: number) =>
    apiGet<ChatHistoryData>(`/chat/${chatId}`, {
      params: { page, pageSize },
    }),
  sendMessage: (data: ChatRequest) => apiPost<ChatResponse>('/chat', data),
  deleteSession: (chatId: string) => apiDelete(`/chat/${chatId}`),
}
