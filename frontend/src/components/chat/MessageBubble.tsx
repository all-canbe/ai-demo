import { useTranslation } from 'react-i18next'
import type { ChatMessage } from '@/types/chat'

interface MessageBubbleProps {
  message: ChatMessage
}

const MessageBubble = ({ message }: MessageBubbleProps) => {
  const { t } = useTranslation('chat')
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-2xl px-6 py-4 rounded-2xl ${
          isUser ? 'bg-primary-600 text-white' : 'bg-white border border-gray-200'
        }`}
      >
        <p className={isUser ? 'text-white' : 'text-gray-900'}>{message.message}</p>
        {message.references && message.references.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-2">{t('references')}:</p>
            <ul className="text-sm">
              {message.references.map((ref, index) => (
                <li key={index} className="text-gray-600">
                  {ref.documentId} - Page {ref.page}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default MessageBubble
