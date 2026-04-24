import { useState, useCallback, useMemo, useEffect } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import { 
  ChevronLeft, 
  ChevronRight, 
  ZoomIn, 
  ZoomOut, 
  X, 
  FileText, 
  FileImage, 
  File, 
  Download, 
  AlertCircle 
} from 'lucide-react'
import type { Reference } from '@/types/chat'

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`

interface DocumentPreviewProps {
  documentId?: string
  url?: string
  fileName?: string
  fileType?: string
  highlightRefs?: Reference[]
  onPageClick?: (page: number) => void
  onClose?: () => void
  isModal?: boolean
}

const FileTypePreview = ({
  url,
  fileType,
  fileName,
  onClose,
}: {
  url: string
  fileType?: string
  fileName?: string
  onClose?: () => void
}) => {
  const [imageError, setImageError] = useState(false)
  const [iframeError, setIframeError] = useState(false)

  const isImage = useMemo(() => {
    if (!fileType) return false
    const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'bmp']
    return imageTypes.includes(fileType.toLowerCase())
  }, [fileType])

  const isPdf = useMemo(() => {
    return fileType?.toLowerCase() === 'pdf'
  }, [fileType])

  const isText = useMemo(() => {
    if (!fileType) return false
    const textTypes = ['txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'ts']
    return textTypes.includes(fileType.toLowerCase())
  }, [fileType])

  if (isImage && !imageError) {
    return (
      <div className="flex items-center justify-center p-4">
        <img
          src={url}
          alt={fileName || '文档预览'}
          className="max-w-full max-h-[60vh] object-contain shadow-lg rounded-lg"
          onError={() => setImageError(true)}
        />
      </div>
    )
  }

  if (isText && !iframeError) {
    return (
      <div className="p-4">
        <iframe
          src={url}
          className="w-full h-[60vh] border rounded-lg"
          title={fileName || '文档预览'}
          onError={() => setIframeError(true)}
        />
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <File className="w-24 h-24 text-gray-400 mb-4" />
      <h3 className="text-lg font-semibold text-gray-700 mb-2">
        此文件类型暂不支持预览
      </h3>
      <p className="text-gray-500 mb-6 max-w-md">
        文件: {fileName} (类型: {fileType?.toUpperCase() || '未知'})
      </p>
      <div className="flex gap-3">
        <a
          href={url}
          download={fileName}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Download className="w-4 h-4" />
          下载文件
        </a>
        {onClose && (
          <button
            onClick={onClose}
            className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            关闭
          </button>
        )}
      </div>
    </div>
  )
}

const DocumentPreview = ({
  documentId,
  url,
  fileName,
  fileType,
  highlightRefs = [],
  onPageClick,
  onClose,
  isModal = false,
}: DocumentPreviewProps) => {
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.0)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // 构建文件下载 URL
  const fileUrl = useMemo(() => {
    if (url) return url
    if (documentId) return `/api/v1/documents/${documentId}/download`
    return undefined
  }, [url, documentId])

  const isPdf = useMemo(() => {
    return fileType?.toLowerCase() === 'pdf'
  }, [fileType])

  // PDF 加载超时处理
  useEffect(() => {
    if (isPdf && loading) {
      const timer = setTimeout(() => {
        setError('PDF 加载超时，请尝试下载文件')
        setLoading(false)
      }, 15000) // 15秒超时
      return () => clearTimeout(timer)
    }
  }, [isPdf, loading])

  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setLoading(false)
    setError(null)
  }, [])

  const onDocumentLoadError = useCallback((error: any) => {
    console.error('Failed to load PDF:', error)
    setError('无法加载PDF文档')
    setLoading(false)
  }, [])

  const goToPrevPage = useCallback(() => {
    setPageNumber((prev) => Math.max(prev - 1, 1))
  }, [])

  const goToNextPage = useCallback(() => {
    setPageNumber((prev) => Math.min(prev + 1, numPages))
  }, [numPages])

  const zoomIn = useCallback(() => {
    setScale((prev) => Math.min(prev + 0.25, 3.0))
  }, [])

  const zoomOut = useCallback(() => {
    setScale((prev) => Math.max(prev - 0.25, 0.5))
  }, [])

  const containerClasses = isModal
    ? 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4'
    : 'w-full h-full'

  const contentClasses = isModal
    ? 'bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col'
    : 'w-full h-full flex flex-col'

  if (!fileUrl && !documentId) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        请选择文档进行预览
      </div>
    )
  }

  return (
    <div className={containerClasses}>
      <div className={contentClasses}>
        {isModal && onClose && (
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center gap-3">
              <h3 className="font-semibold text-gray-900">文档预览</h3>
              {fileName && (
                <span className="text-sm text-gray-500 truncate max-w-xs">
                  {fileName}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {fileUrl && (
                <a
                  href={fileUrl}
                  download={fileName}
                  className="p-2 hover:bg-gray-100 rounded-full text-gray-600 hover:text-primary-600 transition-colors"
                  title="下载文件"
                >
                  <Download className="w-5 h-5" />
                </a>
              )}
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-full text-gray-600 hover:text-gray-800 transition-colors"
                title="关闭"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {isPdf && (
          <div className="flex items-center justify-between p-4 border-b bg-gray-50">
            <div className="flex items-center gap-2">
              <button
                onClick={goToPrevPage}
                disabled={pageNumber <= 1}
                className="p-2 hover:bg-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-sm text-gray-700">
                第 {pageNumber} / {numPages || '-'} 页
              </span>
              <button
                onClick={goToNextPage}
                disabled={pageNumber >= numPages}
                className="p-2 hover:bg-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={zoomOut}
                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <ZoomOut className="w-5 h-5" />
              </button>
              <span className="text-sm text-gray-700">{Math.round(scale * 100)}%</span>
              <button
                onClick={zoomIn}
                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <ZoomIn className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-auto bg-gray-50">
          {loading && isPdf && (
            <div className="flex items-center justify-center h-96">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
            </div>
          )}
          
          {error && (
            <div className="flex flex-col items-center justify-center h-96 p-8 text-center">
              <AlertCircle className="w-16 h-16 text-red-400 mb-4" />
              <p className="text-red-600 font-medium mb-2">{error}</p>
              {fileUrl && (
                <a
                  href={fileUrl}
                  download={fileName}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  尝试下载文件
                </a>
              )}
            </div>
          )}
          
          {fileUrl && isPdf && !error && (
            <Document
              file={fileUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <div className="flex items-center justify-center h-96">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
                </div>
              }
              error={null}
            >
              <div className="flex justify-center py-8">
                <Page
                  pageNumber={pageNumber}
                  scale={scale}
                  onClick={() => onPageClick?.(pageNumber)}
                  className="shadow-lg bg-white"
                />
              </div>
            </Document>
          )}
          
          {fileUrl && !isPdf && (
            <FileTypePreview
              url={fileUrl}
              fileType={fileType}
              fileName={fileName}
              onClose={onClose}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default DocumentPreview
