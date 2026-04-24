import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import type { DocumentsState, Document } from '@/types/document'
import { documentsApi, type FetchDocumentsParams } from '@/api/documents'

const initialState: DocumentsState = {
  documents: [],
  currentDocument: null,
  uploadProgress: 0,
  isLoading: false,
  error: null,
  lastUploadedDocument: null,
  filters: {
    folderId: undefined,
  },
  pagination: {
    page: 1,
    limit: 20,
    total: 0,
  },
}

export const fetchDocuments = createAsyncThunk(
  'documents/fetchDocuments',
  async (params: FetchDocumentsParams | undefined, { rejectWithValue }) => {
    try {
      const response = await documentsApi.list(params)
      return response
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

export const uploadDocument = createAsyncThunk(
  'documents/uploadDocument',
  async (
    { file, folderId, onProgress }: { file: File; folderId?: string; onProgress?: (progress: number) => void },
    { rejectWithValue }
  ) => {
    try {
      const response = await documentsApi.upload(
        { file, folderId },
        (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress?.(progress)
          }
        }
      )
      return response
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

export const deleteDocument = createAsyncThunk(
  'documents/deleteDocument',
  async (id: string, { rejectWithValue }) => {
    try {
      await documentsApi.delete(id)
      return id
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

const documentsSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    setCurrentDocument: (state, action: PayloadAction<Document | null>) => {
      state.currentDocument = action.payload
    },
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
    clearLastUploaded: (state) => {
      state.lastUploadedDocument = null
    },
    setFolderFilter: (state, action: PayloadAction<string | undefined>) => {
      state.filters.folderId = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDocuments.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.isLoading = false
        state.documents = action.payload.items
        state.pagination.total = action.payload.total
        state.pagination.page = action.payload.page
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(uploadDocument.pending, (state) => {
        state.isLoading = true
        state.error = null
        state.uploadProgress = 0
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.isLoading = false
        state.documents.unshift(action.payload)
        state.lastUploadedDocument = action.payload
        state.uploadProgress = 100
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(deleteDocument.fulfilled, (state, action) => {
        state.documents = state.documents.filter((doc) => doc.id !== action.payload)
      })
  },
})

export const { setCurrentDocument, setUploadProgress, clearError, clearLastUploaded, setFolderFilter } = documentsSlice.actions
export default documentsSlice.reducer
