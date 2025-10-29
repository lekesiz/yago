/**
 * YAGO v8.0 - Cost Optimization Suggestions Component
 * AI-powered cost saving recommendations
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { costApi } from '../services/costApi';
import type { OptimizationSuggestion } from '../types/cost';

interface CostOptimizationSuggestionsProps {
  projectId: string;
}

export const CostOptimizationSuggestions: React.FC<CostOptimizationSuggestionsProps> = ({
  projectId,
}) => {
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    loadSuggestions();
  }, [projectId]);

  const loadSuggestions = async () => {
    try {
      setLoading(true);
      const data = await costApi.getOptimizations(projectId);
      setSuggestions(data);
    } catch (error) {
      console.error('Failed to load optimizations:', error);
      toast.error('Failed to load optimization suggestions');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
      high: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300',
      low: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
    };
    return colors[priority as keyof typeof colors] || colors.medium;
  };

  const getPriorityIcon = (priority: string) => {
    const icons = {
      critical: '🚨',
      high: '⚠️',
      medium: '💡',
      low: '💫',
    };
    return icons[priority as keyof typeof icons] || '💡';
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      easy: 'text-green-600 dark:text-green-400',
      medium: 'text-yellow-600 dark:text-yellow-400',
      hard: 'text-red-600 dark:text-red-400',
    };
    return colors[difficulty as keyof typeof colors] || colors.medium;
  };

  const getCategoryIcon = (category: string) => {
    const icons = {
      model_selection: '💎',
      caching: '⚡',
      parallelization: '🚀',
      context_reduction: '📉',
      budget_alert: '💰',
    };
    return icons[category as keyof typeof icons] || '💡';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Analyzing cost optimization opportunities...</p>
        </div>
      </div>
    );
  }

  if (suggestions.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">✨</div>
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          You're Doing Great!
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          No optimization suggestions at the moment. Your project is already well-optimized!
        </p>
      </div>
    );
  }

  const totalSavings = suggestions.reduce((sum, s) => sum + s.potential_savings_amount, 0);

  return (
    <div className="space-y-6">
      {/* Header with total savings */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              💰 Potential Savings
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {suggestions.length} optimization opportunities found
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">
              ${totalSavings.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Total potential savings
            </div>
          </div>
        </div>
      </div>

      {/* Suggestions */}
      <div className="space-y-4">
        {suggestions.map((suggestion, index) => (
          <motion.div
            key={suggestion.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden"
          >
            <div
              className="p-6 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              onClick={() => setExpandedId(expandedId === suggestion.id ? null : suggestion.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="text-3xl">
                    {getCategoryIcon(suggestion.category)}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(suggestion.priority)}`}>
                        {getPriorityIcon(suggestion.priority)} {suggestion.priority.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                        {suggestion.category.replace('_', ' ')}
                      </span>
                    </div>

                    <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                      {suggestion.title}
                    </h4>
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                      {suggestion.description}
                    </p>
                  </div>
                </div>

                <div className="text-right ml-4">
                  <div className="text-xl font-bold text-green-600 dark:text-green-400">
                    {suggestion.potential_savings_pct > 0
                      ? `${suggestion.potential_savings_pct.toFixed(0)}%`
                      : 'N/A'}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    ${suggestion.potential_savings_amount.toFixed(2)} savings
                  </div>
                  <div className={`text-xs mt-1 ${getDifficultyColor(suggestion.implementation_difficulty)}`}>
                    {suggestion.implementation_difficulty} to implement
                  </div>
                </div>
              </div>

              {/* Expand indicator */}
              <div className="mt-4 flex items-center justify-center">
                <motion.div
                  animate={{ rotate: expandedId === suggestion.id ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <svg
                    className="w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </motion.div>
              </div>
            </div>

            {/* Expanded details */}
            <AnimatePresence>
              {expandedId === suggestion.id && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 p-6"
                >
                  <h5 className="font-semibold text-gray-900 dark:text-white mb-3">
                    Implementation Details
                  </h5>

                  <div className="space-y-3">
                    {Object.entries(suggestion.details).map(([key, value]) => (
                      <div key={key} className="flex items-start space-x-2">
                        <span className="text-primary-500">•</span>
                        <div className="flex-1">
                          <span className="font-medium text-gray-700 dark:text-gray-300 capitalize">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span className="text-gray-600 dark:text-gray-400 ml-2">
                            {Array.isArray(value)
                              ? value.join(', ')
                              : typeof value === 'object'
                              ? JSON.stringify(value)
                              : String(value)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toast.success('Optimization suggestion noted! Implementation guide coming soon.');
                    }}
                    className="mt-4 w-full px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                  >
                    Apply This Optimization
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
