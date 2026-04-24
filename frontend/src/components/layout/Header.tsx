import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { logout } from '@/features/auth/authSlice'
import { FileText, MessageSquare, LogOut } from 'lucide-react'

const Header = () => {
  const { t } = useTranslation('common')
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { user } = useAppSelector((state) => state.auth)

  const handleLogout = () => {
    dispatch(logout())
    navigate('/')
  }

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-8">
            <Link to="/documents" className="text-xl font-bold text-primary-900">
              {t('appName')}
            </Link>
            <nav className="flex gap-6">
              <Link
                to="/documents"
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <FileText className="w-5 h-5" />
                {t('documents')}
              </Link>
              <Link
                to="/chat"
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
              >
                <MessageSquare className="w-5 h-5" />
                {t('chat')}
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">{user?.name}</span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <LogOut className="w-5 h-5" />
              {t('logout')}
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
