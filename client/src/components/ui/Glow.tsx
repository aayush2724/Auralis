import React from 'react';

interface GlowProps {
  children: React.ReactNode;
  color?: 'teal' | 'indigo' | 'both';
  className?: string;
  glowClassName?: string;
  active?: boolean;
}

export const Glow: React.FC<GlowProps> = ({ 
  children, 
  color = 'teal', 
  className = '', 
  glowClassName = '', 
  active = false 
}) => {
  const colorMap = {
    teal: 'bg-teal-500/20 group-hover:bg-teal-500/30',
    indigo: 'bg-indigo-500/20 group-hover:bg-indigo-500/30',
    both: 'bg-gradient-to-r from-teal-500/20 to-indigo-500/20 group-hover:from-teal-500/30 group-hover:to-indigo-500/30'
  };

  const activeColorMap = {
    teal: 'bg-teal-500/25',
    indigo: 'bg-indigo-500/25',
    both: 'bg-gradient-to-r from-teal-500/25 to-indigo-500/25'
  };

  return (
    <div className={`relative group ${className}`}>
      <div 
        className={`absolute -inset-2 rounded-2xl blur-xl opacity-0 transition-opacity duration-300 pointer-events-none ${
          active ? 'opacity-100' : 'group-hover:opacity-100'
        } ${active ? activeColorMap[color] : colorMap[color]} ${glowClassName}`}
        style={{ willChange: 'opacity' }}
      />
      <div className="relative z-10 w-full h-full">
        {children}
      </div>
    </div>
  );
};

export default Glow;
