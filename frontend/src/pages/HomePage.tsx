import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FileText, MessageSquare, Zap, Shield } from 'lucide-react'

const HomePage = () => {
  const { t } = useTranslation('common')
  const navigate = useNavigate()

  const features = [
    {
      icon: FileText,
      title: '智能文档解析',
      description: '支持多种格式文档，自动提取内容和结构化信息',
    },
    {
      icon: MessageSquare,
      title: 'AI对话交互',
      description: '基于文档内容进行智能问答，快速获取所需信息',
    },
    {
      icon: Zap,
      title: '高效检索',
      description: '结合知识图谱和向量检索，精准定位相关内容',
    },
    {
      icon: Shield,
      title: '安全可靠',
      description: '数据加密存储，权限严格控制，保障信息安全',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="text-xl font-bold text-primary-900">{t('appName')}</div>
            <div className="flex gap-4">
              <button
                onClick={() => navigate('/login')}
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                {t('login')}
              </button>
              <button
                onClick={() => navigate('/register')}
                className="btn btn-primary"
              >
                {t('register')}
              </button>
            </div>
          </div>
        </div>
      </nav>

      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            让文档交互更智能
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            上传您的文档，与AI进行自然对话，快速获取信息、生成摘要、发现洞察
          </p>
          <div className="flex justify-center gap-4">
            <button
              onClick={() => navigate('/register')}
              className="btn btn-primary text-lg px-8 py-3"
            >
              开始使用
            </button>
            <button className="btn btn-secondary text-lg px-8 py-3">
              了解更多
            </button>
          </div>
        </div>
      </section>

      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            核心功能
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="p-6 bg-gray-50 rounded-xl hover:shadow-lg transition-shadow"
              >
                <feature.icon className="w-12 h-12 text-primary-600 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
