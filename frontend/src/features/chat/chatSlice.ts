import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import type { ChatState, ChatSession, ChatMessage } from '@/types/chat'
import { chatApi, type ChatRequest } from '@/api/chat'

const initialState: ChatState = {
  sessions: [],
  currentSession: null,
  messages: [],
  isStreaming: false,
  isLoading: false,
  error: null,
}

export const fetchSessions = createAsyncThunk(
  'chat/fetchSessions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await chatApi.getSessions()
      return response
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

export const fetchMessages = createAsyncThunk(
  'chat/fetchMessages',
  async (sessionId: string, { rejectWithValue }) => {
    try {
      const response = await chatApi.getMessages(sessionId)
      return response.items
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

export const createSession = createAsyncThunk(
  'chat/createSession',
  async (documentIds: string[], { rejectWithValue }) => {
    try {
      const response = await chatApi.createSession(documentIds)
      return response
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

export const deleteSession = createAsyncThunk(
  'chat/deleteSession',
  async (chatId: string, { rejectWithValue }) => {
    try {
      await chatApi.deleteSession(chatId)
      return chatId
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (data: ChatRequest, { rejectWithValue }) => {
    try {
      const response = await chatApi.sendMessage(data)
      const assistantMessage: ChatMessage = {
        id: response.id,
        role: 'assistant',
        message: response.message,
        references: response.references,
        timestamp: response.timestamp,
      }
      return assistantMessage
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setCurrentSession: (state, action: PayloadAction<ChatSession | null>) => {
      state.currentSession = action.payload
    },
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload)
    },
    updateStreamingMessage: (state, action: PayloadAction<{ id: string; message: string }>) => {
      const index = state.messages.findIndex((m) => m.id === action.payload.id)
      if (index !== -1) {
        state.messages[index].message = action.payload.message
      }
    },
    setIsStreaming: (state, action: PayloadAction<boolean>) => {
      state.isStreaming = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSessions.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchSessions.fulfilled, (state, action) => {
        state.isLoading = false
        state.sessions = action.payload.items || []
      })
      .addCase(fetchSessions.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(fetchMessages.fulfilled, (state, action) => {
        state.messages = action.payload
      })
      .addCase(createSession.fulfilled, (state, action) => {
        state.sessions.unshift(action.payload)
        state.currentSession = action.payload
        state.messages = []
      })
      .addCase(deleteSession.fulfilled, (state, action) => {
        state.sessions = state.sessions.filter((s) => s.id !== action.payload)
      })
      .addCase(sendMessage.pending, (state) => {
        state.isStreaming = true
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.messages.push(action.payload)
        state.isStreaming = false
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isStreaming = false
        state.error = action.payload as string
      })
  },
})

export const { setCurrentSession, addMessage, updateStreamingMessage, setIsStreaming, clearError } =
  chatSlice.actions
export default chatSlice.reducer
