import { ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
}

export function GlassCard({ children, className = '' }: GlassCardProps) {
  return (
    <div 
      className={`bg-white/[0.03] backdrop-blur-[10px] border border-white/10 rounded-xl ${className}`}
      style={{ backdropFilter: 'blur(10px)' }}
    >
      {children}
    </div>
  );
}
