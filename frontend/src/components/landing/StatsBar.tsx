import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { useCountUp } from '../../hooks/useCountUp';

const stats = [
  { value: 6,  suffix: '×',  label: 'faster objection response',  prefix: '' },
  { value: 94, suffix: '%',  label: 'buyer persona accuracy',       prefix: '' },
  { value: 38, suffix: '%',  label: 'average conversion lift',      prefix: '' },
  { value: 2,  suffix: 's',  label: 'real-time response latency',   prefix: '<' },
];

const StatTile = ({ stat, i, isVisible }: { stat: any, i: number, isVisible: boolean }) => {
  const countUp = useCountUp(stat.value, 1400, isVisible);
  
  return (
    <motion.div
      className="text-center"
      initial={{ opacity: 0, y: 20 }}
      animate={isVisible ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: i * 0.1 }}
    >
      <div className="font-display text-5xl text-white leading-none mb-2">
        {stat.prefix}{Math.floor(countUp)}{stat.suffix}
      </div>
      <div className="font-sans text-sm text-white/55 leading-snug max-w-[130px] mx-auto">
        {stat.label}
      </div>
    </motion.div>
  );
};

export default function StatsBar() {
  const ref = useRef<HTMLElement>(null);
  const isVisible = useInView(ref, { once: true, margin: "-100px 0px" });

  return (
    <section id="stats" className="relative z-20 bg-auralis-green py-16 px-6" ref={ref}>
      <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
        {stats.map((stat, i) => (
          <StatTile key={stat.label} stat={stat} i={i} isVisible={isVisible} />
        ))}
      </div>
    </section>
  );
}
