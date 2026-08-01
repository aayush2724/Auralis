import { motion, useReducedMotion } from 'framer-motion';

export default function TypingIndicator() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div className="flex w-full mt-4 space-x-3 max-w-2xl">
      <div className="flex-shrink-0 mt-1">
        <motion.div
          initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.28, ease: 'easeOut' }}
          className="w-8 h-8 rounded-full bg-gradient-to-br from-[#0d9488] to-[#0a0a0a] flex items-center justify-center"
        >
          <span className="text-white text-xs font-bold">A</span>
        </motion.div>
      </div>
      <motion.div
        initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.28, ease: 'easeOut' }}
        className="bg-[#f9fafb] text-[#0a0a0a] rounded-2xl rounded-tl-sm px-4 py-4 max-w-[70%] flex items-center space-x-1 shadow-sm h-10"
        style={{ willChange: 'opacity, transform' }}
      >
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-1.5 h-1.5 bg-[#6b7280] rounded-full"
            animate={
              shouldReduceMotion 
                ? { opacity: [0.45, 1, 0.45] } 
                : { y: [0, -3, 0], scale: [0.95, 1.08, 0.95], opacity: [0.45, 1, 0.45] }
            }
            transition={{
              repeat: Infinity,
              duration: 1.6,
              delay: i * 0.2,
              ease: 'easeInOut',
            }}
            style={{ willChange: 'opacity, transform' }}
          />
        ))}
      </motion.div>
    </div>
  );
}
