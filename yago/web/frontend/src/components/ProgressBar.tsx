/**
 * YAGO v8.0 - Progress Bar Component
 * Visual progress indicator with category breakdown
 */

import React from 'react';
import { motion } from 'framer-motion';
import type { ClarificationProgress } from '../types/clarification';

interface ProgressBarProps {
  progress: ClarificationProgress;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress }) => {
  const getCategoryIcon = (category: string) => {
    const icons = {
      basic: '📋',
      technical: '⚙️',
      infrastructure: '🏗️',
      security: '🔒',
      quality: '✨',
    };
    return icons[category as keyof typeof icons] || '📌';
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      basic: 'bg-blue-500',
      technical: 'bg-purple-500',
      infrastructure: 'bg-green-500',
      security: 'bg-red-500',
      quality: 'bg-yellow-500',
    };
    return colors[category as keyof typeof colors] || 'bg-gray-500';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
      {/* Overall Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Overall Progress
          </h3>
          <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {Math.round(progress.percentage)}%
          </span>
        </div>

        <div className="relative h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress.percentage}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full"
          />
        </div>

        <div className="flex items-center justify-between mt-2 text-sm text-gray-600 dark:text-gray-400">
          <span>
            {progress.answered} of {progress.total} questions answered
          </span>
          <span>
            {progress.estimated_time_remaining > 0
              ? `~${Math.ceil(progress.estimated_time_remaining)} min remaining`
              : 'Almost done!'}
          </span>
        </div>
      </div>

      {/* Category Progress */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Progress by Category
        </h4>

        {Object.entries(progress.category_progress).map(([category, value]) => {
          const [answered, total] = value.split('/').map(Number);
          const percentage = total > 0 ? (answered / total) * 100 : 0;

          return (
            <div key={category} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span>{getCategoryIcon(category)}</span>
                  <span className="font-medium text-gray-700 dark:text-gray-300 capitalize">
                    {category}
                  </span>
                </div>
                <span className="text-gray-600 dark:text-gray-400">{value}</span>
              </div>

              <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ duration: 0.4, delay: 0.1 }}
                  className={`absolute top-0 left-0 h-full ${getCategoryColor(category)} rounded-full`}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Completion Status */}
      {progress.percentage >= 80 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800"
        >
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0">
              <svg
                className="w-6 h-6 text-green-600 dark:text-green-400"
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
            </div>
            <div>
              <p className="text-sm font-semibold text-green-800 dark:text-green-200">
                Almost There!
              </p>
              <p className="text-xs text-green-600 dark:text-green-400">
                You can finish early if you want
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ProgressBar;
