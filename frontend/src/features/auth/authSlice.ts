import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import type { AuthState } from '@/types/auth'
import { authApi, type LoginRequest, type RegisterRequest, type LoginData, type UserInfo } from '@/api/auth'

const initialState: AuthState = {
  user: null,
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  isAuthenticated: !!localStorage.getItem('accessToken'),
  isLoading: false,
  error: null,
}

export const login = createAsyncThunk(
  'auth/login',
  async (data: LoginRequest, { rejectWithValue }) => {
    try {
      const response = await authApi.login(data)
      return response
    } catch (error: any) {
      return rejectWithValue(error.message || error || '登录失败')
    }
  }
)

export const register = createAsyncThunk(
  'auth/register',
  async (data: RegisterRequest, { rejectWithValue }) => {
    try {
      await authApi.register(data)
      const loginData: LoginRequest = { email: data.email, password: data.password }
      const loginResponse = await authApi.login(loginData)
      return loginResponse
    } catch (error: any) {
      return rejectWithValue(error.message || error || '注册失败')
    }
  }
)

export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authApi.getMe()
      return response
    } catch (error: any) {
      return rejectWithValue(error.message || '获取用户信息失败')
    }
  }
)

export const logout = createAsyncThunk('auth/logout', async () => {
  await authApi.logout()
})

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
      builder
        .addCase(login.pending, (state) => {
          state.isLoading = true
          state.error = null
        })
        .addCase(login.fulfilled, (state, action: PayloadAction<LoginData>) => {
          state.isLoading = false
          state.user = action.payload.user
          state.accessToken = action.payload.accessToken
          state.refreshToken = action.payload.refreshToken
          state.isAuthenticated = true
          localStorage.setItem('accessToken', action.payload.accessToken)
          localStorage.setItem('refreshToken', action.payload.refreshToken)
        })
        .addCase(login.rejected, (state, action) => {
          state.isLoading = false
          state.error = action.payload as string
        })
        .addCase(register.pending, (state) => {
          state.isLoading = true
          state.error = null
        })
        .addCase(register.fulfilled, (state, action: PayloadAction<LoginData>) => {
          state.isLoading = false
          state.user = action.payload.user
          state.accessToken = action.payload.accessToken
          state.refreshToken = action.payload.refreshToken
          state.isAuthenticated = true
          localStorage.setItem('accessToken', action.payload.accessToken)
          localStorage.setItem('refreshToken', action.payload.refreshToken)
        })
        .addCase(register.rejected, (state, action) => {
          state.isLoading = false
          state.error = action.payload as string
        })
        .addCase(fetchCurrentUser.fulfilled, (state, action: PayloadAction<UserInfo>) => {
          state.user = {
            id: action.payload.id,
            email: action.payload.email,
            name: action.payload.name,
            createdAt: action.payload.createdAt,
          }
        })
        .addCase(logout.fulfilled, (state) => {
          state.user = null
          state.accessToken = null
          state.refreshToken = null
          state.isAuthenticated = false
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
        })
    },
})

export const { clearError } = authSlice.actions
export default authSlice.reducer
