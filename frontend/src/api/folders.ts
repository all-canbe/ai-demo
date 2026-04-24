import { apiGet, apiPost, apiDelete, apiPut } from './client'
import type { Folder } from '@/types/folder'

export interface CreateFolderRequest {
  name: string
  parentId?: string
}

export interface UpdateFolderRequest {
  name: string
  parentId?: string
}

export const foldersApi = {
  list: () => apiGet<Folder[]>('/folders'),
  create: (data: CreateFolderRequest) => apiPost<Folder>('/folders', data),
  update: (id: string, data: UpdateFolderRequest) => apiPut<Folder>(`/folders/${id}`, data),
  delete: (id: string) => apiDelete(`/folders/${id}`),
}
