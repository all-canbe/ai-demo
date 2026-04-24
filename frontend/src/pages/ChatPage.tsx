import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useAppDispatch } from '@/app/hooks'
import { fetchSessions, fetchMessages } from '@/features/chat/chatSlice'
import ChatWindow from '@/components/chat/ChatWindow'
import SessionSidebar from '@/components/chat/SessionSidebar'

const ChatPage = () => {
  const { chatId } = useParams()
  const dispatch = useAppDispatch()

  useEffect(() => {
    dispatch(fetchSessions())
  }, [dispatch])

  useEffect(() => {
    if (chatId) {
      dispatch(fetchMessages(chatId))
    }
  }, [dispatch, chatId])

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <SessionSidebar />
      <div className="flex-1">
        <ChatWindow />
      </div>
    </div>
  )
}

export default ChatPage
