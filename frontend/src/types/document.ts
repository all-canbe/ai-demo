export interface Document {
  id: string
  name: string
  type: string
  size: number
  uploadTime: string
  processingStatus: string
  folderId?: string
  fileUrl?: string
}

export interface DocumentStatus {
  id: string
  processingStatus: string
  progress: number
  errorMessage?: string
  updatedAt: string
}

export interface DocumentSummary {
  documentId: string
  summary: string
  keyPoints: string[]
}

export interface PaginatedDocuments {
  items: Document[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface DocumentsState {
  documents: Document[]
  currentDocument: Document | null
  uploadProgress: number
  isLoading: boolean
  error: string | null
  lastUploadedDocument: Document | null
  filters: any
  pagination: {
    page: number
    limit: number
    total: number
  }
}
