import { motion, useReducedMotion } from 'framer-motion';

const blobs = [
  {
    className: 'left-[-10%] top-[8%] h-72 w-72 bg-teal-400/20',
    animate: { x: [0, 36, -18, 0], y: [0, -28, 18, 0], scale: [1, 1.08, 0.98, 1] },
  },
  {
    className: 'right-[-8%] top-[28%] h-80 w-80 bg-indigo-500/16',
    animate: { x: [0, -30, 24, 0], y: [0, 24, -18, 0], scale: [1, 0.96, 1.07, 1] },
  },
  {
    className: 'bottom-[-12%] left-[32%] h-96 w-96 bg-gradient-to-br from-teal-300/14 to-indigo-500/14',
    animate: { x: [0, 28, -34, 0], y: [0, -18, 24, 0], scale: [1, 1.06, 0.97, 1] },
  },
];

export default function AmbientBackground() {
  const shouldReduceMotion = useReducedMotion() ?? false;

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      {blobs.map((blob, index) => (
        <motion.div
          key={blob.className}
          className={`absolute rounded-full blur-3xl ${blob.className}`}
          animate={shouldReduceMotion ? undefined : blob.animate}
          transition={{
            duration: 18 + index * 4,
            repeat: Infinity,
            repeatType: 'mirror',
            ease: 'easeInOut',
          }}
          style={{ transform: 'translateZ(0)', willChange: 'transform' }}
        />
      ))}
    </div>
  );
}
