import { apiPost, apiGet } from './client'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
}

export interface UserInfo {
  id: string
  email: string
  name: string
  createdAt: string
}

export interface LoginData {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
  user: UserInfo
}

export interface RefreshTokenData {
  accessToken: string
  tokenType: string
  expiresIn: number
}

export const authApi = {
  login: (data: LoginRequest) => apiPost<LoginData>('/auth/login', data),
  register: (data: RegisterRequest) => apiPost<UserInfo>('/auth/register', data),
  refreshToken: (refreshToken: string) =>
    apiPost<RefreshTokenData>('/auth/refresh', { refreshToken }),
  logout: () => apiPost('/auth/logout'),
  getMe: () => apiGet<UserInfo>('/auth/me'),
}
