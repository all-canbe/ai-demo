import { useState, useEffect } from 'react'
import { useAppDispatch } from '@/app/hooks'
import { documentsApi } from '@/api/documents'
import { FileText, Sparkles, AlertCircle } from 'lucide-react'

interface SummaryCardProps {
  documentId: string
  className?: string
}

const SummaryCard = ({ documentId, className = '' }: SummaryCardProps) => {
  const dispatch = useAppDispatch()
  const [summary, setSummary] = useState<string | null>(null)
  const [keyPoints, setKeyPoints] = useState<string[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSummary = async () => {
      if (!documentId) return
      
      setLoading(true)
      setError(null)
      
      try {
        const data = await documentsApi.getSummary(documentId)
        setSummary(data.summary)
        setKeyPoints(data.keyPoints || [])
      } catch (err: any) {
        setError(err.message || '获取摘要失败')
      } finally {
        setLoading(false)
      }
    }

    fetchSummary()
  }, [documentId])

  if (loading) {
    return (
      <div className={`bg-white rounded-xl shadow-sm border p-6 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3" />
          <div className="h-4 bg-gray-200 rounded w-full" />
          <div className="h-4 bg-gray-200 rounded w-5/6" />
          <div className="h-4 bg-gray-200 rounded w-4/6" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-xl p-6 ${className}`}>
        <div className="flex items-center gap-2 text-red-700 mb-2">
          <AlertCircle className="w-5 h-5" />
          <span className="font-medium">获取摘要失败</span>
        </div>
        <p className="text-red-600 text-sm">{error}</p>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border p-6 ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-6 h-6 text-primary-600" />
        <h3 className="text-lg font-semibold text-gray-900">文档摘要</h3>
      </div>

      {summary && (
        <div className="mb-6">
          <p className="text-gray-700 leading-relaxed">{summary}</p>
        </div>
      )}

      {keyPoints.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            关键要点
          </h4>
          <ul className="space-y-2">
            {keyPoints.map((point, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-medium mt-0.5">
                  {index + 1}
                </span>
                <span className="text-gray-600">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {!summary && keyPoints.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>暂无摘要信息</p>
        </div>
      )}
    </div>
  )
}

export default SummaryCard
