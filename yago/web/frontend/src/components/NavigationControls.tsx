/**
 * YAGO v8.0 - Navigation Controls Component
 * Next, Previous, Skip, and Finish buttons
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface NavigationControlsProps {
  onNext: () => void;
  onPrevious: () => void;
  onSkip: () => void;
  onFinish: () => void;
  canNext: boolean;
  canPrevious: boolean;
  canSkip: boolean;
  canFinish: boolean;
  loading?: boolean;
}

export const NavigationControls: React.FC<NavigationControlsProps> = ({
  onNext,
  onPrevious,
  onSkip,
  onFinish,
  canNext,
  canPrevious,
  canSkip,
  canFinish,
  loading = false,
}) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Previous Button */}
        <button
          onClick={onPrevious}
          disabled={!canPrevious || loading}
          className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg
                   bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300
                   hover:bg-gray-200 dark:hover:bg-gray-600
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-all duration-200 font-medium"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Previous
        </button>

        {/* Skip Button */}
        {canSkip && (
          <button
            onClick={onSkip}
            disabled={loading}
            className="flex-1 px-6 py-3 rounded-lg
                     border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300
                     hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-700
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-all duration-200 font-medium"
          >
            Skip Question
          </button>
        )}

        {/* Finish Early Button */}
        <AnimatePresence mode="wait">
          {canFinish && (
            <motion.button
              key="finish-button"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={onFinish}
              disabled={loading}
              className="flex-1 px-6 py-3 rounded-lg
                       bg-green-600 hover:bg-green-700 text-white
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-all duration-200 font-medium shadow-lg"
            >
              <span className="flex items-center justify-center gap-2">
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Finish Early
              </span>
            </motion.button>
          )}
        </AnimatePresence>

        {/* Next Button */}
        <button
          onClick={onNext}
          disabled={!canNext || loading}
          className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg
                   bg-primary-600 hover:bg-primary-700 text-white
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-all duration-200 font-medium shadow-lg"
        >
          {loading ? (
            <>
              <svg
                className="animate-spin h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Loading...
            </>
          ) : (
            <>
              Next
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </>
          )}
        </button>
      </div>

      {/* Keyboard Shortcuts Hint */}
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
          <span className="font-semibold">Keyboard shortcuts:</span>{' '}
          <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">←</kbd> Previous •{' '}
          <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">→</kbd> Next •{' '}
          <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">Shift+Enter</kbd> Skip
        </p>
      </div>
    </div>
  );
};

export default NavigationControls;
