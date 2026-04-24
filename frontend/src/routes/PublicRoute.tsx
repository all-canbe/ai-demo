import { Navigate, Outlet } from 'react-router-dom'
import { useAppSelector } from '@/app/hooks'

const PublicRoute = () => {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated)

  if (isAuthenticated) {
    return <Navigate to="/documents" replace />
  }

  return <Outlet />
}

export default PublicRoute
