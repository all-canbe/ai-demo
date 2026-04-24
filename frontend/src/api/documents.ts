import { apiGet, apiPost, apiDelete } from './client'
import type { Document, PaginatedDocuments, DocumentStatus, DocumentSummary } from '@/types/document'

export interface UploadDocumentRequest {
  file: File
  folderId?: string
}

export interface FetchDocumentsParams {
  folderId?: string
  page?: number
  pageSize?: number
}

export const documentsApi = {
  list: (params?: FetchDocumentsParams) =>
    apiGet<PaginatedDocuments>('/documents', { params }),
  upload: (data: UploadDocumentRequest, onUploadProgress?: (progressEvent: any) => void) => {
    const formData = new FormData()
    formData.append('file', data.file)
    if (data.folderId) {
      formData.append('folderId', data.folderId)
    }
    return apiPost<Document>('/documents', formData, {
      onUploadProgress,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  delete: (id: string) => apiDelete(`/documents/${id}`),
  getSummary: (id: string) => apiGet<DocumentSummary>(`/documents/${id}/summary`),
  getStatus: (id: string) => apiGet<DocumentStatus>(`/documents/${id}/status`),
  getDownloadUrl: (id: string) => `/documents/${id}/download`,
  download: async (id: string, filename?: string) => {
    const url = `/documents/${id}/download`
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
    })
    if (!response.ok) throw new Error('下载失败')
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = filename || `document-${id}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(downloadUrl)
  },
}
