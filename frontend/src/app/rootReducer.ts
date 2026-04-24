import { combineReducers } from '@reduxjs/toolkit'
import authReducer from '@/features/auth/authSlice'
import documentsReducer from '@/features/documents/documentsSlice'
import chatReducer from '@/features/chat/chatSlice'
import foldersReducer from '@/features/folders/foldersSlice'

const rootReducer = combineReducers({
  auth: authReducer,
  documents: documentsReducer,
  chat: chatReducer,
  folders: foldersReducer,
})

export default rootReducer
