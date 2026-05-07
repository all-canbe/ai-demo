interface LoadingDotsProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizes = {
  sm: 'w-1.5 h-1.5',
  md: 'w-2 h-2',
  lg: 'w-3 h-3',
};

export function LoadingDots({ size = 'md', className = '' }: LoadingDotsProps) {
  return (
    <div className={`flex items-center gap-1 ${className}`}>
      <span className={`${sizes[size]} rounded-full bg-current animate-bounce`} style={{ animationDelay: '0ms' }} />
      <span className={`${sizes[size]} rounded-full bg-current animate-bounce`} style={{ animationDelay: '150ms' }} />
      <span className={`${sizes[size]} rounded-full bg-current animate-bounce`} style={{ animationDelay: '300ms' }} />
    </div>
  );
}
