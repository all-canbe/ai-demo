import { motion } from 'framer-motion'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
  count?: number
}

const Skeleton = ({
  className = '',
  variant = 'rectangular',
  width,
  height,
  count = 1,
}: SkeletonProps) => {
  const baseClasses = 'bg-gray-200'

  const variantClasses = {
    text: 'h-4 w-full',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  }

  const style = {
    width,
    height,
  }

  const SkeletonItem = () => (
    <motion.div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={style}
      animate={{
        backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: 'linear',
      }}
      style={{
        ...style,
        backgroundImage: 'linear-gradient(90deg, #e5e7eb 25%, #f3f4f6 50%, #e5e7eb 75%)',
        backgroundSize: '200% 100%',
      }}
    />
  )

  if (count > 1) {
    return (
      <div className="space-y-2">
        {Array.from({ length: count }).map((_, index) => (
          <SkeletonItem key={index} />
        ))}
      </div>
    )
  }

  return <SkeletonItem />
}

export const TextSkeleton = ({
  lines = 3,
  className = '',
}: {
  lines?: number
  className?: string
}) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, index) => (
      <Skeleton
        key={index}
        variant="text"
        width={index === lines - 1 ? '60%' : '100%'}
      />
    ))}
  </div>
)

export const CardSkeleton = ({
  className = '',
}: {
  className?: string
}) => (
  <div className={`bg-white rounded-xl p-6 border ${className}`}>
    <Skeleton variant="circular" width={48} height={48} className="mb-4" />
    <Skeleton variant="text" className="mb-2" />
    <TextSkeleton lines={2} />
  </div>
)

export default Skeleton
