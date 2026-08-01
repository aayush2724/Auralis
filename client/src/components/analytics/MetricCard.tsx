import { motion, useReducedMotion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { useCountUp } from '../../hooks/useCountUp';

interface MetricCardProps {
  label: string;
  value: string | number;
  suffix?: string;
  icon: LucideIcon;
  color: string;
  delay?: number;
}

const ACCENT_STYLES: Record<string, { base: string; glow: string; icon: string; shadow: string }> = {
  '[#0d9488]': {
    base: 'bg-[#0d9488]/10 text-[#0d9488]',
    glow: 'rgba(13, 148, 136, 0.32)',
    icon: 'rgba(13, 148, 136, 0.18)',
    shadow: 'rgba(13, 148, 136, 0.12)',
  },
  green: {
    base: 'bg-green-100 text-green-700',
    glow: 'rgba(34, 197, 94, 0.26)',
    icon: 'rgba(34, 197, 94, 0.16)',
    shadow: 'rgba(34, 197, 94, 0.10)',
  },
  indigo: {
    base: 'bg-indigo-100 text-indigo-700',
    glow: 'rgba(99, 102, 241, 0.28)',
    icon: 'rgba(99, 102, 241, 0.16)',
    shadow: 'rgba(99, 102, 241, 0.10)',
  },
};

export default function MetricCard({ label, value, suffix, icon: Icon, color, delay = 0 }: MetricCardProps) {
  const shouldReduceMotion = useReducedMotion() ?? false;
  const accent = ACCENT_STYLES[color] ?? ACCENT_STYLES.indigo;

  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  const count = useCountUp(numValue, 1200, true);
  
  const decimals = typeof value === 'string' && value.includes('.') 
    ? value.split('.')[1].length 
    : (Number.isInteger(numValue) ? 0 : 2);
    
  const displayValue = count.toFixed(decimals);

  return (
    <motion.div 
      initial={shouldReduceMotion ? { opacity: 1, y: 0, scale: 1 } : { opacity: 0, y: 14, scale: 0.985 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={shouldReduceMotion
        ? { duration: 0.2 }
        : { type: 'spring', stiffness: 280, damping: 26, mass: 0.85, delay }}
      whileHover={shouldReduceMotion
        ? undefined
        : {
            y: -4,
            scale: 1.012,
            boxShadow: `0 18px 44px ${accent.shadow}, 0 0 0 1px rgba(13, 148, 136, 0.08)`,
            transition: { type: 'spring', stiffness: 500, damping: 30, mass: 0.5 },
          }}
      className="group relative overflow-hidden rounded-2xl border border-[#f9fafb] bg-white p-5 shadow-sm"
      style={{
        transform: 'translateZ(0)',
        willChange: 'transform, opacity, box-shadow',
      }}
    >
      <div
        className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full blur-3xl opacity-70"
        style={{ background: `radial-gradient(circle, ${accent.glow} 0%, transparent 70%)` }}
      />
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-px opacity-70"
        style={{ background: `linear-gradient(90deg, transparent, ${accent.glow}, transparent)` }}
      />
      <div className="flex justify-between items-start">
        <div>
          <div className="text-3xl font-display font-normal text-[#0a0a0a] flex items-baseline space-x-1 tracking-tight">
            <span>{displayValue}</span>
            {suffix && <span className="text-sm font-sans font-light text-[#6b7280]">{suffix}</span>}
          </div>
          <p className="text-xs font-sans font-medium uppercase tracking-widest text-[#6b7280] mt-1">{label}</p>
        </div>
        <motion.div
          className={`w-10 h-10 rounded-full flex items-center justify-center ${accent.base}`}
          whileHover={shouldReduceMotion ? undefined : { scale: 1.08, rotate: 8 }}
          transition={{ type: 'spring', stiffness: 500, damping: 28, mass: 0.45 }}
        >
          <motion.div
            whileHover={shouldReduceMotion ? undefined : { scale: 1.12, rotate: -6 }}
            transition={{ type: 'spring', stiffness: 600, damping: 30, mass: 0.4 }}
          >
            <Icon className="w-5 h-5" />
          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  );
}
