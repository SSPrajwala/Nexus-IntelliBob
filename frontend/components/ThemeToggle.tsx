"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  
  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  // Only access theme context after component is mounted
  const themeContext = mounted ? useTheme() : null;
  const theme = themeContext?.theme || "dark";
  const toggleTheme = themeContext?.toggleTheme || (() => {});

  // Don't render until mounted to prevent hydration issues
  if (!mounted) {
    return (
      <div className="w-14 h-7 rounded-full bg-gray-700 border border-gray-600 animate-pulse" />
    );
  }

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative w-14 h-7 rounded-full bg-gray-700 dark:bg-gray-800 border border-gray-600 dark:border-gray-700 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900"
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
    >
      <motion.div
        className="absolute top-0.5 left-0.5 w-6 h-6 rounded-full bg-white dark:bg-gray-900 shadow-lg flex items-center justify-center"
        animate={{
          x: theme === "light" ? 28 : 0,
        }}
        transition={{
          type: "spring",
          stiffness: 500,
          damping: 30,
        }}
      >
        {theme === "light" ? (
          <Sun className="w-4 h-4 text-yellow-500" />
        ) : (
          <Moon className="w-4 h-4 text-blue-400" />
        )}
      </motion.div>
    </motion.button>
  );
}

// Made with Bob
