import { useNavigate, useParams } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { fetchSessions, setCurrentSession, deleteSession } from '@/features/chat/chatSlice'
import { useEffect } from 'react'
import { MessageSquare, Trash2, Plus } from 'lucide-react'

const SessionSidebar = () => {
  const navigate = useNavigate()
  const { chatId } = useParams()
  const dispatch = useAppDispatch()
  const { sessions, isLoading } = useAppSelector((state) => state.chat)

  useEffect(() => {
    dispatch(fetchSessions())
  }, [dispatch])

  const handleSessionClick = (sessionId: string) => {
    const session = sessions.find((s) => s.id === sessionId)
    if (session) {
      dispatch(setCurrentSession(session))
      navigate(`/chat/${sessionId}`)
    }
  }

  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation()
    if (window.confirm('确定要删除这个会话吗？')) {
      dispatch(deleteSession(sessionId))
    }
  }

  const handleCreateSession = () => {
    navigate('/chat')
  }

  return (
    <div className="w-72 bg-white border-r border-gray-200 flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={handleCreateSession}
          className="w-full flex items-center justify-center gap-2 btn btn-primary"
        >
          <Plus className="w-4 h-4" />
          <span>新建会话</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">加载中...</div>
        ) : sessions.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>暂无会话</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => handleSessionClick(session.id)}
                className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                  session.id === chatId ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      <h3 className="font-medium text-gray-900 truncate">
                        {session.title || '无标题会话'}
                      </h3>
                    </div>
                    <p className="text-sm text-gray-500 mt-1 truncate">
                      {new Date(session.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteSession(e, session.id)}
                    className="p-1 hover:bg-red-100 rounded text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default SessionSidebar
