import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { sendMessage } from '@/features/chat/chatSlice'
import { Send } from 'lucide-react'
import MessageBubble from './MessageBubble'

const ChatWindow = () => {
  const { t } = useTranslation('chat')
  const dispatch = useAppDispatch()
  const { messages, isStreaming } = useAppSelector((state) => state.chat)
  const [inputValue, setInputValue] = useState('')

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim()) return
    dispatch(sendMessage({ message: inputValue, documentIds: [] }))
    setInputValue('')
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <p>{t('noSession')}</p>
          </div>
        ) : (
          <div className="space-y-4 max-w-4xl mx-auto">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isStreaming && (
              <div className="flex items-center gap-2 text-gray-500">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
                <span>{t('typing')}</span>
              </div>
            )}
          </div>
        )}
      </div>
      <div className="border-t bg-white p-4">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto">
          <div className="flex gap-4">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={t('inputPlaceholder')}
              className="flex-1 input"
            />
            <button type="submit" className="btn btn-primary" disabled={!inputValue.trim()}>
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ChatWindow
