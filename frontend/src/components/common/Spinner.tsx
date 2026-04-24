import { Loader2, RefreshCw, Cpu, Database, Activity } from 'lucide-react'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'default' | 'primary' | 'white'
  className?: string
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
}

const colorClasses = {
  default: 'text-gray-600',
  primary: 'text-primary-600',
  white: 'text-white',
}

const Spinner = ({
  size = 'md',
  variant = 'default',
  className = '',
}: SpinnerProps) => (
  <Loader2
    className={`animate-spin ${sizeClasses[size]} ${colorClasses[variant]} ${className}`}
  />
)

export const ProcessingSpinner = ({
  text,
  icon = 'loader',
  className = '',
}: {
  text?: string
  icon?: 'loader' | 'cpu' | 'database' | 'activity'
  className?: string
}) => {
  const Icon = {
    loader: RefreshCw,
    cpu: Cpu,
    database: Database,
    activity: Activity,
  }[icon]

  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
      <Icon className="w-10 h-10 text-primary-600 animate-spin" />
      {text && (
        <p className="text-gray-600 text-sm">{text}</p>
      )}
    </div>
  )
}

export const PageSpinner = ({
  text = '加载中...',
}: {
  text?: string
}) => (
  <div className="min-h-screen flex items-center justify-center">
    <ProcessingSpinner text={text} />
  </div>
)

export default Spinner
