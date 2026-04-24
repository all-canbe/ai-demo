import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { fetchDocuments, setFolderFilter, clearLastUploaded } from '@/features/documents/documentsSlice'
import { fetchFolders } from '@/features/folders/foldersSlice'
import UploadZone from '@/components/document/UploadZone'
import DocumentList from '@/components/document/DocumentList'
import { Folder, Home, MessageSquare, X } from 'lucide-react'

const DocumentsPage = () => {
  const navigate = useNavigate()
  const { t } = useTranslation('documents')
  const dispatch = useAppDispatch()
  const { documents, isLoading, error, filters, lastUploadedDocument } = useAppSelector((state) => state.documents)
  const { folders } = useAppSelector((state) => state.folders)

  useEffect(() => {
    dispatch(fetchDocuments({ folderId: filters.folderId }))
  }, [dispatch, filters.folderId])

  useEffect(() => {
    dispatch(fetchFolders())
  }, [dispatch])

  const handleFolderSelect = (folderId: string | undefined) => {
    dispatch(setFolderFilter(folderId))
  }

  const handleDismiss = () => {
    dispatch(clearLastUploaded())
  }

  const handleGoToChat = () => {
    dispatch(clearLastUploaded())
    navigate('/chat')
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">{t('title')}</h1>

        {/* 文件夹筛选 */}
        <div className="mb-6">
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => handleFolderSelect(undefined)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                !filters.folderId
                  ? 'bg-blue-50 border-blue-200 text-blue-700'
                  : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Home className="w-4 h-4" />
              <span>全部文档</span>
            </button>
            {folders.map((folder) => (
              <button
                key={folder.id}
                onClick={() => handleFolderSelect(folder.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                  filters.folderId === folder.id
                    ? 'bg-blue-50 border-blue-200 text-blue-700'
                    : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Folder className="w-4 h-4" />
                <span>{folder.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 上传成功提示 */}
        {lastUploadedDocument && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="mt-0.5">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
                <div>
                  <h3 className="text-green-800 font-medium">文件上传成功！</h3>
                  <p className="text-green-600 text-sm mt-1">
                    "{lastUploadedDocument.name}" 已成功上传，现在可以开始与文档对话了。
                  </p>
                  <button
                    onClick={handleGoToChat}
                    className="mt-3 inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <MessageSquare className="w-4 h-4" />
                    <span>开始聊天</span>
                  </button>
                </div>
              </div>
              <button
                onClick={handleDismiss}
                className="text-green-400 hover:text-green-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        <UploadZone />

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mt-6">
            {error}
          </div>
        )}

        <div className="mt-8">
          <DocumentList documents={documents} isLoading={isLoading} />
        </div>
      </div>
    </div>
  )
}

export default DocumentsPage
