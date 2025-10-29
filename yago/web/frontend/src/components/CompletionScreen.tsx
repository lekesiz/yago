/**
 * YAGO v8.0 - Completion Screen Component
 * Shows results and generated brief after clarification
 */

import React from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

interface CompletionScreenProps {
  brief: any;
  onStartNew: () => void;
  onContinue?: () => void;
}

export const CompletionScreen: React.FC<CompletionScreenProps> = ({
  brief,
  onStartNew,
  onContinue,
}) => {
  const downloadBrief = () => {
    const dataStr = JSON.stringify(brief, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `yago-brief-${brief.session_id}.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success('Brief downloaded successfully!');
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(brief, null, 2));
      toast.success('Brief copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy to clipboard');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-4xl"
      >
        {/* Success Animation */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 15 }}
            className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-green-500 to-green-600 rounded-full shadow-2xl mb-6"
          >
            <svg
              className="w-12 h-12 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={3}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </motion.div>

          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Clarification Complete!
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Great job! We've gathered all the information needed to build your project.
            Here's your comprehensive project brief.
          </p>
        </div>

        {/* Brief Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-200 dark:border-gray-700 mb-6"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            Project Brief Summary
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Questions Answered */}
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-200 dark:border-blue-800">
              <div className="text-3xl mb-2">📋</div>
              <div className="text-2xl font-bold text-blue-900 dark:text-blue-100 mb-1">
                {brief.question_count || 0}
              </div>
              <div className="text-sm text-blue-700 dark:text-blue-300">
                Questions Answered
              </div>
            </div>

            {/* Completion Rate */}
            <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 border border-green-200 dark:border-green-800">
              <div className="text-3xl mb-2">✅</div>
              <div className="text-2xl font-bold text-green-900 dark:text-green-100 mb-1">
                {brief.answer_count || 0}/{brief.question_count || 0}
              </div>
              <div className="text-sm text-green-700 dark:text-green-300">
                Completion Rate
              </div>
            </div>

            {/* Time Taken */}
            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border border-purple-200 dark:border-purple-800">
              <div className="text-3xl mb-2">⏱️</div>
              <div className="text-2xl font-bold text-purple-900 dark:text-purple-100 mb-1">
                {brief.time_taken || '~10'} min
              </div>
              <div className="text-sm text-purple-700 dark:text-purple-300">
                Time Invested
              </div>
            </div>
          </div>

          {/* Project Idea */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Project Idea
            </h3>
            <p className="text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              {brief.project_idea}
            </p>
          </div>

          {/* Key Answers */}
          {brief.answers && Object.keys(brief.answers).length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                Key Answers (Preview)
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {Object.entries(brief.answers)
                  .slice(0, 5)
                  .map(([key, value]: [string, any]) => (
                    <div
                      key={key}
                      className="flex items-start gap-3 bg-gray-50 dark:bg-gray-900 rounded-lg p-3 border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex-shrink-0 w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {key}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 truncate">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </div>
                      </div>
                    </div>
                  ))}
                {Object.keys(brief.answers).length > 5 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                    +{Object.keys(brief.answers).length - 5} more answers
                  </p>
                )}
              </div>
            </div>
          )}
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            What's Next?
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            {/* Download Brief */}
            <button
              onClick={downloadBrief}
              className="flex items-center justify-center gap-3 px-6 py-4 rounded-xl
                       border-2 border-primary-500 text-primary-700 dark:text-primary-300
                       hover:bg-primary-50 dark:hover:bg-primary-900/20
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
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Download Brief
            </button>

            {/* Copy to Clipboard */}
            <button
              onClick={copyToClipboard}
              className="flex items-center justify-center gap-3 px-6 py-4 rounded-xl
                       border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300
                       hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-700
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
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              Copy to Clipboard
            </button>
          </div>

          <div className="space-y-3">
            {/* Continue Button */}
            {onContinue && (
              <motion.button
                onClick={onContinue}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full py-4 px-6 rounded-xl bg-gradient-to-r from-primary-600 to-primary-700
                         hover:from-primary-700 hover:to-primary-800 text-white font-semibold text-lg
                         shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center gap-3"
              >
                Continue to Agent Selection
                <svg
                  className="w-6 h-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              </motion.button>
            )}

            {/* Start New */}
            <button
              onClick={onStartNew}
              className="w-full py-3 px-6 rounded-xl border-2 border-gray-300 dark:border-gray-600
                       text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-gray-500
                       hover:bg-gray-50 dark:hover:bg-gray-700 font-medium
                       transition-all duration-200"
            >
              Start a New Project
            </button>
          </div>
        </motion.div>

        {/* Info Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="mt-6 text-center"
        >
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Your brief has been saved. You can download it or continue to the next phase.
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default CompletionScreen;
