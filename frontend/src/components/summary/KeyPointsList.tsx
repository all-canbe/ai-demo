import { CheckCircle } from 'lucide-react'

interface KeyPointsListProps {
  keyPoints: string[]
  className?: string
  onKeyPointClick?: (point: string, index: number) => void
}

const KeyPointsList = ({ keyPoints, className = '', onKeyPointClick }: KeyPointsListProps) => {
  if (keyPoints.length === 0) {
    return null
  }

  return (
    <div className={`bg-gradient-to-br from-primary-50 to-white rounded-xl p-5 border border-primary-100 ${className}`}>
      <h4 className="text-sm font-semibold text-primary-800 mb-3 flex items-center gap-2">
        <CheckCircle className="w-4 h-4" />
        关键要点
      </h4>
      <ul className="space-y-2">
        {keyPoints.map((point, index) => (
          <li
            key={index}
            onClick={() => onKeyPointClick?.(point, index)}
            className="flex items-start gap-3 p-2 rounded-lg hover:bg-primary-100 cursor-pointer transition-colors"
          >
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
              {index + 1}
            </span>
            <span className="text-gray-700 text-sm leading-relaxed">{point}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default KeyPointsList
