import { useRef } from 'react';
import { motion, useInView, useReducedMotion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { useCountUp } from '../../hooks/useCountUp';
import { scaleHover } from '../ui/Animations';

interface MetricCardProps {
  label: string;
  value: string | number;
  suffix?: string;
  icon: LucideIcon;
  color: string;
}

export default function MetricCard({ label, value, suffix, icon: Icon, color }: MetricCardProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.1 });
  const shouldReduceMotion = useReducedMotion() ?? false;
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  const count = useCountUp(numValue, 1200, isInView);
  
  const decimals = typeof value === 'string' && value.includes('.') 
    ? value.split('.')[1].length 
    : (Number.isInteger(numValue) ? 0 : 2);
    
  const displayValue = count.toFixed(decimals);

  return (
    <motion.div 
      ref={ref}
      variants={{ hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }}
      whileHover={scaleHover(shouldReduceMotion).hover}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className="bg-white border border-[#f9fafb] rounded-2xl p-5 shadow-sm"
      style={{ transform: 'translateZ(0)', willChange: 'transform, opacity' }}
    >
      <div className="flex justify-between items-start">
        <div>
          <div className="text-3xl font-display font-normal text-[#0a0a0a] flex items-baseline space-x-1 tracking-tight">
            <span>{displayValue}</span>
            {suffix && <span className="text-sm font-sans font-light text-[#6b7280]">{suffix}</span>}
          </div>
          <p className="text-xs font-sans font-medium uppercase tracking-widest text-[#6b7280] mt-1">{label}</p>
        </div>
        <div className={`w-10 h-10 rounded-full flex items-center justify-center
          ${color === '[#0d9488]' ? 'bg-[#0d9488]/10 text-[#0d9488]' : 
            color === 'green' ? 'bg-green-100 text-green-700' : 
            'bg-indigo-100 text-indigo-700'}
        `}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </motion.div>
  );
}
