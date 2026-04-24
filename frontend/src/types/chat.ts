export interface Reference {
  documentId: string
  page: number
  content: string
}

export interface ChatMessage {
  id: string
  role: string
  message: string
  references?: Reference[]
  timestamp: string
}

export interface ChatResponse {
  id: string
  chatId: string
  message: string
  references: Reference[]
  timestamp: string
}

export interface ChatSession {
  id: string
  title: string
  createdAt: string
}

export interface ChatHistoryData {
  id: string
  items: ChatMessage[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface ChatState {
  sessions: ChatSession[]
  currentSession: ChatSession | null
  messages: ChatMessage[]
  isStreaming: boolean
  isLoading: boolean
  error: string | null
}
