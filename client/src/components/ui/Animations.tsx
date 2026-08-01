import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import type { Variants, HTMLMotionProps } from 'framer-motion';

export const springTransition = {
  type: 'spring',
  stiffness: 420,
  damping: 32,
  mass: 0.8,
} as const;

export const easeTransition = {
  duration: 0.35,
  ease: 'easeOut',
} as const;

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1, 
    transition: easeTransition,
  }
};

export const fadeUp = (reduced: boolean = false): Variants => ({
  hidden: { 
    opacity: 0, 
    y: reduced ? 0 : 15 
  },
  visible: { 
    opacity: 1, 
    y: 0, 
    transition: easeTransition,
  }
});

export const slideLeft = (reduced: boolean = false): Variants => ({
  hidden: { 
    opacity: 0, 
    x: reduced ? 0 : 20 
  },
  visible: { 
    opacity: 1, 
    x: 0, 
    transition: easeTransition,
  }
});

export const slideRight = (reduced: boolean = false): Variants => ({
  hidden: { 
    opacity: 0, 
    x: reduced ? 0 : -20 
  },
  visible: { 
    opacity: 1, 
    x: 0, 
    transition: easeTransition,
  }
});

export const staggerContainer = (staggerChildren = 0.1, delayChildren = 0): Variants => ({
  hidden: {},
  visible: {
    transition: {
      staggerChildren,
      delayChildren
    }
  }
});

export const pageTransition = (reduced: boolean = false): Variants => ({
  initial: { 
    opacity: 0, 
    x: reduced ? 0 : 10,
    y: reduced ? 0 : 6 
  },
  animate: { 
    opacity: 1, 
    x: 0,
    y: 0, 
    transition: reduced
      ? { duration: 0.2, ease: 'easeOut' }
      : { type: 'spring', stiffness: 320, damping: 34, mass: 0.9 },
  },
  exit: { 
    opacity: 0, 
    x: reduced ? 0 : -10,
    y: reduced ? 0 : -6, 
    transition: reduced
      ? { duration: 0.18, ease: 'easeIn' }
      : { duration: 0.26, ease: 'easeInOut' } 
  }
});

export const tabTransition = (reduced: boolean = false): Variants => ({
  inactive: {
    opacity: 0,
    x: reduced ? 0 : -18,
    y: reduced ? 0 : 4,
    scale: reduced ? 1 : 0.985,
    transition: reduced
      ? { duration: 0.18, ease: 'easeIn' }
      : { duration: 0.24, ease: 'easeInOut' },
  },
  active: {
    opacity: 1,
    y: 0,
    x: 0,
    transition: reduced
      ? { duration: 0.2, ease: 'easeOut' }
      : { type: 'spring', stiffness: 330, damping: 34, mass: 0.9 },
  },
});

export const scaleHover = (reduced: boolean = false) => ({
  hover: reduced ? {} : { scale: 1.02, transition: easeTransition }
});

export const buttonTap = (reduced: boolean = false) => ({
  tap: reduced ? {} : { scale: 0.97, transition: springTransition }
});

interface AnimationWrapperProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  delay?: number;
}

export const FadeIn: React.FC<AnimationWrapperProps> = ({ children, delay = 0, ...props }) => {
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-20px" }}
      variants={fadeIn}
      transition={{ delay }}
      style={{ willChange: 'opacity' }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export const FadeUp: React.FC<AnimationWrapperProps> = ({ children, delay = 0, ...props }) => {
  const reduced = useReducedMotion() ?? false;
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-20px" }}
      variants={fadeUp(reduced)}
      transition={{ delay }}
      style={{ transform: 'translateZ(0)', willChange: 'transform, opacity' }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export const SlideLeft: React.FC<AnimationWrapperProps> = ({ children, delay = 0, ...props }) => {
  const reduced = useReducedMotion() ?? false;
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-20px" }}
      variants={slideLeft(reduced)}
      transition={{ delay }}
      style={{ transform: 'translateZ(0)', willChange: 'transform, opacity' }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export const SlideRight: React.FC<AnimationWrapperProps> = ({ children, delay = 0, ...props }) => {
  const reduced = useReducedMotion() ?? false;
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-20px" }}
      variants={slideRight(reduced)}
      transition={{ delay }}
      style={{ transform: 'translateZ(0)', willChange: 'transform, opacity' }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export const PageTransition: React.FC<AnimationWrapperProps> = ({ children, ...props }) => {
  const reduced = useReducedMotion() ?? false;
  return (
    <motion.div
      variants={pageTransition(reduced)}
      initial="initial"
      animate="animate"
      exit="exit"
      style={{ transform: 'translateZ(0)', willChange: 'transform, opacity' }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export const Stagger: React.FC<AnimationWrapperProps & { staggerChildren?: number; delayChildren?: number }> = ({ 
  children, 
  staggerChildren = 0.1, 
  delayChildren = 0, 
  ...props 
}) => {
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-20px" }}
      variants={staggerContainer(staggerChildren, delayChildren)}
      {...props}
    >
      {children}
    </motion.div>
  );
};
