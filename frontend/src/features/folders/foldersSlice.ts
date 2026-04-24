import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import type { FoldersState, Folder } from '@/types/folder'
import { foldersApi, type CreateFolderRequest, type UpdateFolderRequest } from '@/api/folders'

const initialState: FoldersState = {
  folders: [],
  currentFolder: null,
  isLoading: false,
  error: null,
}

export const fetchFolders = createAsyncThunk(
  'folders/fetchFolders',
  async (_, { rejectWithValue }) => {
    try {
      const response = await foldersApi.list()
      return response
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

export const createFolder = createAsyncThunk(
  'folders/createFolder',
  async (data: CreateFolderRequest, { rejectWithValue }) => {
    try {
      const response = await foldersApi.create(data)
      return response
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

export const updateFolder = createAsyncThunk(
  'folders/updateFolder',
  async ({ id, data }: { id: string; data: UpdateFolderRequest }, { rejectWithValue }) => {
    try {
      const response = await foldersApi.update(id, data)
      return response
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

export const deleteFolder = createAsyncThunk(
  'folders/deleteFolder',
  async (id: string, { rejectWithValue }) => {
    try {
      await foldersApi.delete(id)
      return id
    } catch (error: any) {
      return rejectWithValue(error.message)
    }
  }
)

const foldersSlice = createSlice({
  name: 'folders',
  initialState,
  reducers: {
    setCurrentFolder: (state, action: PayloadAction<Folder | null>) => {
      state.currentFolder = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFolders.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchFolders.fulfilled, (state, action) => {
        state.isLoading = false
        state.folders = action.payload
      })
      .addCase(fetchFolders.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(createFolder.fulfilled, (state, action) => {
        state.folders.push(action.payload)
      })
      .addCase(updateFolder.fulfilled, (state, action) => {
        const index = state.folders.findIndex((f) => f.id === action.payload.id)
        if (index !== -1) {
          state.folders[index] = action.payload
        }
      })
      .addCase(deleteFolder.fulfilled, (state, action) => {
        state.folders = state.folders.filter((folder) => folder.id !== action.payload)
      })
  },
})

export const { setCurrentFolder, clearError } = foldersSlice.actions
export default foldersSlice.reducer
