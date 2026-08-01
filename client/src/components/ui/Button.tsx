import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';
import { buttonTap } from './Animations';

export type ButtonVariant = 'primary' | 'outline' | 'ghost' | 'secondary';

export interface ButtonProps extends HTMLMotionProps<"button"> {
  variant?: ButtonVariant;
  children: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', children, className = '', ...props }, ref) => {
    const shouldReduceMotion = useReducedMotion();
    let variantStyles = '';
    
    if (variant === 'primary') {
      variantStyles = 'bg-[#0d9488] text-white px-6 py-3 rounded-full font-sans font-medium text-sm tracking-wide hover:bg-[#0f766e] transition-colors duration-200';
    } else if (variant === 'secondary') {
      variantStyles = 'bg-[#6366f1] text-white px-6 py-3 rounded-full font-sans font-medium text-sm tracking-wide hover:bg-[#4f46e5] transition-colors duration-200';
    } else if (variant === 'outline') {
      variantStyles = 'bg-transparent text-[#0a0a0a] px-6 py-3 rounded-full border border-[#0a0a0a]/20 hover:border-[#0a0a0a]/60 hover:bg-[#0a0a0a]/5 transition-colors duration-200 font-sans font-medium text-sm tracking-wide';
    } else if (variant === 'ghost') {
      variantStyles = 'bg-transparent text-[#0a0a0a] hover:text-[#0d9488] underline underline-offset-4 decoration-1 hover:decoration-2 transition-colors font-sans font-medium text-sm p-0 m-0 border-none inline-flex items-center justify-center';
    }

    return (
      <motion.button
        ref={ref}
        variants={buttonTap(shouldReduceMotion ?? false)}
        whileTap={variant !== 'ghost' ? "tap" : undefined}
        className={`${variantStyles} ${className}`}
        style={{ willChange: 'transform' }}
        {...props}
      >
        {children}
      </motion.button>
    );
  }
);
Button.displayName = 'Button';

export const PillTag = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => {
  return (
    <span className={`bg-[#f9fafb] text-[#0a0a0a] px-3 py-1 rounded-full text-xs font-sans font-medium tracking-widest uppercase inline-flex items-center gap-1.5 ${className}`}>
      {children}
    </span>
  );
};
