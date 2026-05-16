"use client";

import { motion } from "framer-motion";

interface NexusLogoProps {
  size?: number;
  animated?: boolean;
  className?: string;
}

export default function NexusLogo({ 
  size = 40, 
  animated = false,
  className = "" 
}: NexusLogoProps) {
  const LogoSVG = () => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer hexagon ring */}
      <path
        d="M50 5 L85 27.5 L85 72.5 L50 95 L15 72.5 L15 27.5 Z"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
        className="text-blue-500 dark:text-blue-400"
      />
      
      {/* Inner hexagon */}
      <path
        d="M50 20 L72 32.5 L72 67.5 L50 80 L28 67.5 L28 32.5 Z"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
        className="text-blue-400 dark:text-blue-300"
      />
      
      {/* Central node */}
      <circle
        cx="50"
        cy="50"
        r="8"
        fill="currentColor"
        className="text-blue-500 dark:text-blue-400"
      />
      
      {/* Connection nodes (6 points) */}
      <circle cx="50" cy="20" r="4" fill="currentColor" className="text-blue-400" />
      <circle cx="72" cy="32.5" r="4" fill="currentColor" className="text-blue-400" />
      <circle cx="72" cy="67.5" r="4" fill="currentColor" className="text-blue-400" />
      <circle cx="50" cy="80" r="4" fill="currentColor" className="text-blue-400" />
      <circle cx="28" cy="67.5" r="4" fill="currentColor" className="text-blue-400" />
      <circle cx="28" cy="32.5" r="4" fill="currentColor" className="text-blue-400" />
      
      {/* Connection lines from center to nodes */}
      <line x1="50" y1="50" x2="50" y2="20" stroke="currentColor" strokeWidth="1.5" className="text-blue-300 dark:text-blue-500" opacity="0.6" />
      <line x1="50" y1="50" x2="72" y2="32.5" stroke="currentColor" strokeWidth="1.5" className="text-blue-300 dark:text-blue-500" opacity="0.6" />
      <line x1="50" y1="50" x2="72" y2="67.5" stroke="currentColor" strokeWidth="1.5" className="text-blue-300 dark:text-blue-500" opacity="0.6" />
      <line x1="50" y1="50" x2="50" y2="80" stroke="currentColor" strokeWidth="1.5" className="text-blue-300 dark:text-blue-500" opacity="0.6" />
      <line x1="50" y1="50" x2="28" y2="67.5" stroke="currentColor" strokeWidth="1.5" className="text-blue-300 dark:text-blue-500" opacity="0.6" />
      <line x1="50" y1="50" x2="28" y2="32.5" stroke="currentColor" strokeWidth="1.5" className="text-blue-300 dark:text-blue-500" opacity="0.6" />
      
      {/* Subtle glow effect */}
      <circle
        cx="50"
        cy="50"
        r="12"
        fill="currentColor"
        className="text-blue-500 dark:text-blue-400"
        opacity="0.2"
      />
    </svg>
  );

  if (animated) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          animate={{
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <LogoSVG />
        </motion.div>
      </motion.div>
    );
  }

  return <LogoSVG />;
}

// Made with Bob
