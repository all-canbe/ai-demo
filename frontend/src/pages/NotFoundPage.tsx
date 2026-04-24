import { Link } from 'react-router-dom'

const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-primary-600">404</h1>
        <p className="text-2xl text-gray-600 mt-4 mb-8">页面未找到</p>
        <Link to="/" className="btn btn-primary">
          返回首页
        </Link>
      </div>
    </div>
  )
}

export default NotFoundPage
