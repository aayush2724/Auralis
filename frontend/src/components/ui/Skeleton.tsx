interface SkeletonProps {
  className?: string;
}

export default function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div 
      className={`bg-gradient-to-r from-auralis-frost via-white to-auralis-frost animate-shimmer rounded-2xl ${className}`}
      style={{ backgroundSize: '200% 100%' }}
    />
  );
}
