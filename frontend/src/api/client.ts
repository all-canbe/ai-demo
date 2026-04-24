import axios, { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import type { ApiResponse, ApiError } from './types'
import { toCamelCase, toSnakeCase } from './transform'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token!)
    }
  })
  failedQueue = []
}

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    if (config.data && !(config.data instanceof FormData)) {
      config.data = toSnakeCase(config.data)
    }

    if (config.params) {
      config.params = toSnakeCase(config.params)
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse<any>>) => {
    const rawData = response.data
    const converted = toCamelCase<ApiResponse<any>>(rawData)
    const { code, message, data } = converted

    if (code !== 0) {
      return Promise.reject({ code, message } as ApiError)
    }

    response.data = data
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refreshToken')

      if (!refreshToken) {
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(apiClient(originalRequest))
            },
            reject,
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const response = await axios.post<ApiResponse<{ accessToken: string }>>(
          `${apiClient.defaults.baseURL}/auth/refresh`,
          { refreshToken }
        )
        const converted = toCamelCase<ApiResponse<{ accessToken: string }>>(response.data)

        if (converted.code !== 0 || !converted.data?.accessToken) {
          throw new Error('Token refresh failed')
        }

        const newToken = converted.data.accessToken
        localStorage.setItem('accessToken', newToken)
        processQueue(null, newToken)

        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    if (error.response?.data) {
      const converted = toCamelCase<ApiError>(error.response.data)
      return Promise.reject({
        code: converted.code || 5001,
        message: converted.message || '网络错误',
      } as ApiError)
    }

    return Promise.reject({
      code: 5001,
      message: '网络错误',
    } as ApiError)
  }
)

export async function apiGet<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.get<T>(url, config)
  return response.data as T
}

export async function apiPost<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.post<T>(url, data, config)
  return response.data as T
}

export async function apiDelete<T = void>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.delete<T>(url, config)
  return response.data as T
}

export async function apiPut<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.put<T>(url, data, config)
  return response.data as T
}

export async function apiPatch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.patch<T>(url, data, config)
  return response.data as T
}

export default apiClient
