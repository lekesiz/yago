/**
 * YAGO v7.1 - Header Component
 * Logo, project name, theme toggle
 */

import React from 'react';
import { motion } from 'framer-motion';

interface HeaderProps {
  projectIdea?: string;
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  projectIdea,
  darkMode,
  onToggleDarkMode,
}) => {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center gap-4">
            <motion.div
              initial={{ rotate: 0 }}
              animate={{ rotate: 360 }}
              transition={{ duration: 1, ease: 'easeInOut' }}
              className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-lg"
            >
              <span className="text-2xl font-bold text-white">Y</span>
            </motion.div>

            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                YAGO v7.1
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                AI Development Platform
              </p>
            </div>
          </div>

          {/* Project Idea (if available) */}
          {projectIdea && (
            <div className="hidden md:block flex-1 max-w-2xl mx-8">
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg px-4 py-2 border border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Project Idea:
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300 truncate">
                  {projectIdea}
                </p>
              </div>
            </div>
          )}

          {/* Theme Toggle */}
          <button
            onClick={onToggleDarkMode}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600
                     transition-all duration-200"
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <svg
                className="w-6 h-6 text-yellow-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
            ) : (
              <svg
                className="w-6 h-6 text-gray-700"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
