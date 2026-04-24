import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAppDispatch } from '@/app/hooks'
import { deleteDocument, setCurrentDocument } from '@/features/documents/documentsSlice'
import { createSession } from '@/features/chat/chatSlice'
import type { Document } from '@/types/document'
import { 
  FileText, 
  Trash2, 
  Eye, 
  MessageSquare, 
  File, 
  FileImage, 
  FileText as FileTextIcon, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  MoreVertical, 
  Download 
} from 'lucide-react'
import DocumentPreview from './DocumentPreview'

interface DocumentListProps {
  documents: Document[]
  isLoading: boolean
  viewMode?: 'list' | 'grid'
}

const DocumentList = ({ documents, isLoading, viewMode = 'list' }: DocumentListProps) => {
  const { t } = useTranslation('documents')
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null)
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([])

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return <FileTextIcon className="w-5 h-5" />
    if (type.includes('image') || type.match(/\.(png|jpg|jpeg|gif|svg)$/i)) {
      return <FileImage className="w-5 h-5" />
    }
    return <File className="w-5 h-5" />
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />
    }
  }

  const getStatusLabel = (status: string) => {
    const statusMap: Record<string, string> = {
      pending: '等待处理',
      parsing: '解析中',
      extracting: '提取中',
      embedding: '向量化中',
      completed: '已完成',
      error: '处理失败',
    }
    return statusMap[status] || status
  }

  const formatFileSize = (bytes: number) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${Math.round((bytes / Math.pow(k, i) * 100) / 100)} ${sizes[i]}`
  }

  const handleDelete = (id: string, event: React.MouseEvent) => {
    event.stopPropagation()
    if (window.confirm(t('list.deleteConfirm'))) {
      dispatch(deleteDocument(id))
    }
  }

  const handlePreview = (doc: Document, event: React.MouseEvent) => {
    event.stopPropagation()
    setPreviewDocument(doc)
  }

  const handleStartChat = async (doc: Document, event: React.MouseEvent) => {
    event.stopPropagation()
    dispatch(setCurrentDocument(doc))
    const result = await dispatch(createSession([doc.id]))
    if (createSession.fulfilled.match(result)) {
      navigate('/chat')
    }
  }

  const handleToggleSelect = (id: string, event: React.MouseEvent) => {
    event.stopPropagation()
    setSelectedDocuments(prev => 
      prev.includes(id) 
        ? prev.filter(d => d !== id)
        : [...prev, id]
    )
  }

  const handleStartMultiChat = async () => {
    if (selectedDocuments.length === 0) return
    const result = await dispatch(createSession(selectedDocuments))
    if (createSession.fulfilled.match(result)) {
      setSelectedDocuments([])
      navigate('/chat')
    }
  }

  if (isLoading) {
    if (viewMode === 'grid') {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-48 bg-gray-100 rounded-xl animate-pulse" />
        ))}
        </div>
      )
    }
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-gray-100 rounded-lg animate-pulse" />
        ))}
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-16">
        <FileText className="w-20 h-20 text-gray-200 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-600 mb-2">{t('list.empty')}</h3>
        <p className="text-gray-400">上传文档开始使用</p>
      </div>
    )
  }

  if (viewMode === 'grid') {
    return (
      <>
        {selectedDocuments.length > 0 && (
          <div className="mb-4 p-4 bg-primary-50 rounded-lg border border-primary-200">
            <div className="flex items-center justify-between">
              <span className="text-primary-700">
                已选择 {selectedDocuments.length} 个文档
              </span>
              <button
                onClick={handleStartMultiChat}
                className="btn btn-primary btn-sm"
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                开始聊天
              </button>
            </div>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              onClick={() => handleToggleSelect(doc.id, event as any)}
              className={`relative bg-white rounded-xl border-2 cursor-pointer transition-all hover:shadow-md ${
                selectedDocuments.includes(doc.id)
                  ? 'border-primary-500 ring-2 ring-primary-200'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="p-4 border-b bg-gray-50 rounded-t-xl">
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    {getFileIcon(doc.type)}
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(doc.processingStatus)}
                  </div>
                </div>
                <h3 className="font-medium text-gray-900 truncate" title={doc.name}>
                  {doc.name}
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  {formatFileSize(doc.size)}
                </p>
              </div>
              <div className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      doc.processingStatus === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : doc.processingStatus === 'error'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {getStatusLabel(doc.processingStatus)}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(doc.uploadTime).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                  onClick={(e) => handlePreview(doc, e)}
                  className="flex-1 btn btn-secondary btn-sm"
                >
                    <Eye className="w-4 h-4 mr-1" />
                  预览
                  </button>
                  {doc.processingStatus === 'completed' && (
                    <button
                    onClick={(e) => handleStartChat(doc, e)}
                    className="flex-1 btn btn-primary btn-sm"
                  >
                      <MessageSquare className="w-4 h-4 mr-1" />
                    聊天
                    </button>
                  )}
                <button
                  onClick={(e) => handleDelete(doc.id, e)}
                  className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                </div>
              </div>
            </div>
          ))}
        </div>
        {previewDocument && (
          <DocumentPreview
            documentId={previewDocument.id}
            url={previewDocument.fileUrl}
            fileName={previewDocument.name}
            fileType={previewDocument.type}
            isModal
            onClose={() => setPreviewDocument(null)}
          />
        )}
      </>
    )
  }

  return (
    <>
      {selectedDocuments.length > 0 && (
        <div className="mb-4 p-4 bg-primary-50 rounded-lg border border-primary-200">
          <div className="flex items-center justify-between">
            <span className="text-primary-700">
              已选择 {selectedDocuments.length} 个文档
            </span>
            <button
              onClick={handleStartMultiChat}
              className="btn btn-primary btn-sm"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              开始聊天
            </button>
          </div>
        </div>
      )}
      <div className="space-y-3">
        {documents.map((doc) => (
          <div
            key={doc.id}
            onClick={() => handleToggleSelect(doc.id, event as any)}
            className={`flex items-center justify-between p-4 bg-white rounded-lg border-2 cursor-pointer transition-all hover:shadow-md ${
              selectedDocuments.includes(doc.id)
                ? 'border-primary-500 ring-2 ring-primary-200'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-4 flex-1">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary-100 rounded-lg">
                  {getFileIcon(doc.type)}
                </div>
                <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-900 truncate">{doc.name}</h3>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs text-gray-500">
                    {formatFileSize(doc.size)}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(doc.uploadTime).toLocaleDateString()}
                  </span>
                </div>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
                <span
                className={`px-3 py-1 text-xs rounded-full flex items-center gap-1 ${
                  doc.processingStatus === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : doc.processingStatus === 'error'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {getStatusIcon(doc.processingStatus)}
                {getStatusLabel(doc.processingStatus)}
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={(e) => handlePreview(doc, e)}
                  className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg"
                  title="预览"
                >
                  <Eye className="w-5 h-5" />
                </button>
                {doc.processingStatus === 'completed' && (
                  <button
                  onClick={(e) => handleStartChat(doc, e)}
                  className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg"
                  title="开始聊天"
                >
                    <MessageSquare className="w-5 h-5" />
                  </button>
                )}
                <button
                  onClick={(e) => handleDelete(doc.id, e)}
                  className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg"
                  title="删除"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      {previewDocument && (
        <DocumentPreview
          documentId={previewDocument.id}
          url={previewDocument.fileUrl}
          fileName={previewDocument.name}
          fileType={previewDocument.type}
          isModal
          onClose={() => setPreviewDocument(null)}
        />
      )}
    </>
  )
}

export default DocumentList
