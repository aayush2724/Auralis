import { motion, useReducedMotion } from 'framer-motion';

const blobs = [
  {
    className: 'left-[-12%] top-[8%] h-[22rem] w-[22rem] bg-teal-400/14',
    animate: { x: [0, 32, -20, 0], y: [0, -18, 14, 0], scale: [1, 1.05, 0.98, 1] },
  },
  {
    className: 'right-[-10%] top-[18%] h-[26rem] w-[26rem] bg-indigo-400/12',
    animate: { x: [0, -24, 18, 0], y: [0, 20, -16, 0], scale: [1, 0.96, 1.04, 1] },
  },
  {
    className: 'left-[28%] bottom-[-18%] h-[30rem] w-[30rem] bg-gradient-to-br from-teal-300/12 via-cyan-300/8 to-indigo-400/10',
    animate: { x: [0, 22, -26, 0], y: [0, -14, 20, 0], scale: [1, 1.04, 0.97, 1] },
  },
];

export default function AmbientBackground() {
  const shouldReduceMotion = useReducedMotion() ?? false;

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(20,184,166,0.04),_transparent_45%),radial-gradient(circle_at_bottom,_rgba(99,102,241,0.03),_transparent_50%)]" />
      {blobs.map((blob, index) => (
        <motion.div
          key={blob.className}
          className={`absolute rounded-full blur-3xl ${blob.className}`}
          animate={shouldReduceMotion ? undefined : blob.animate}
          transition={{
            duration: 24 + index * 5,
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
