/**
 * YAGO v8.0 - Budget Alert Component
 * Real-time budget monitoring and warnings
 */

import React from 'react';
import { motion } from 'framer-motion';
import type { BudgetStatus } from '../types/cost';

interface BudgetAlertProps {
  budgetStatus: BudgetStatus | null;
}

export const BudgetAlert: React.FC<BudgetAlertProps> = ({ budgetStatus }) => {
  if (!budgetStatus || !budgetStatus.has_budget) {
    return null;
  }

  const {
    budget_limit,
    current_spent,
    percentage_used,
    projected_final,
    threshold_reached,
    threshold_pct,
    time_remaining_pct,
  } = budgetStatus;

  // Determine alert severity
  const getAlertSeverity = () => {
    if (current_spent >= budget_limit) {
      return {
        level: 'critical',
        color: 'from-red-500 to-red-600',
        bgColor: 'bg-red-50 dark:bg-red-900/20',
        textColor: 'text-red-800 dark:text-red-300',
        borderColor: 'border-red-500',
        icon: '🚨',
        title: 'Budget Exceeded!',
        message: 'Your project has exceeded the budget limit.',
      };
    } else if (percentage_used >= 90) {
      return {
        level: 'warning',
        color: 'from-orange-500 to-red-500',
        bgColor: 'bg-orange-50 dark:bg-orange-900/20',
        textColor: 'text-orange-800 dark:text-orange-300',
        borderColor: 'border-orange-500',
        icon: '⚠️',
        title: 'Budget Critical',
        message: 'You are very close to exceeding your budget.',
      };
    } else if (threshold_reached) {
      return {
        level: 'caution',
        color: 'from-yellow-500 to-orange-500',
        bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
        textColor: 'text-yellow-800 dark:text-yellow-300',
        borderColor: 'border-yellow-500',
        icon: '💡',
        title: 'Budget Threshold Reached',
        message: `You've reached ${threshold_pct}% of your budget.`,
      };
    } else {
      return {
        level: 'safe',
        color: 'from-green-500 to-emerald-500',
        bgColor: 'bg-green-50 dark:bg-green-900/20',
        textColor: 'text-green-800 dark:text-green-300',
        borderColor: 'border-green-500',
        icon: '✅',
        title: 'Budget Healthy',
        message: 'Your spending is within budget.',
      };
    }
  };

  const alert = getAlertSeverity();

  // Calculate if projected to exceed
  const willExceed = projected_final > budget_limit;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`${alert.bgColor} border-2 ${alert.borderColor} rounded-xl p-6 shadow-lg`}
    >
      <div className="flex items-start space-x-4">
        {/* Icon */}
        <div className="text-4xl">{alert.icon}</div>

        {/* Content */}
        <div className="flex-1">
          {/* Title */}
          <h3 className={`text-xl font-bold ${alert.textColor} mb-2`}>
            {alert.title}
          </h3>

          {/* Message */}
          <p className={`text-sm ${alert.textColor} mb-4`}>
            {alert.message}
          </p>

          {/* Budget Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className={`font-medium ${alert.textColor}`}>
                Budget Usage
              </span>
              <span className={`font-bold ${alert.textColor}`}>
                {percentage_used.toFixed(1)}%
              </span>
            </div>

            <div className="relative w-full h-4 bg-white dark:bg-gray-800 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(percentage_used, 100)}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
                className={`absolute h-full bg-gradient-to-r ${alert.color} rounded-full`}
              />
            </div>

            <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
              <span>${current_spent.toFixed(2)} spent</span>
              <span>${budget_limit.toFixed(2)} limit</span>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 mt-4">
            {/* Remaining Budget */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                Remaining
              </div>
              <div className={`text-lg font-bold ${alert.textColor}`}>
                ${(budget_limit - current_spent).toFixed(2)}
              </div>
            </div>

            {/* Time Remaining */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                Time Left
              </div>
              <div className={`text-lg font-bold ${alert.textColor}`}>
                {time_remaining_pct.toFixed(0)}%
              </div>
            </div>

            {/* Projected Final Cost */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                Projected Final
              </div>
              <div className={`text-lg font-bold ${willExceed ? 'text-red-600 dark:text-red-400' : alert.textColor}`}>
                ${projected_final.toFixed(2)}
              </div>
            </div>

            {/* Threshold */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3">
              <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                Alert Threshold
              </div>
              <div className={`text-lg font-bold ${alert.textColor}`}>
                {threshold_pct}%
              </div>
            </div>
          </div>

          {/* Projection Warning */}
          {willExceed && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg"
            >
              <div className="flex items-center space-x-2">
                <span className="text-lg">📊</span>
                <div className="flex-1">
                  <div className="text-sm font-semibold text-red-800 dark:text-red-300">
                    Projected to Exceed Budget
                  </div>
                  <div className="text-xs text-red-700 dark:text-red-400">
                    Based on current spending rate, you're projected to exceed budget by $
                    {(projected_final - budget_limit).toFixed(2)}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Recommendations */}
          {(threshold_reached || willExceed) && (
            <div className="mt-4 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                💡 Recommendations
              </div>
              <ul className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                <li className="flex items-start">
                  <span className="text-primary-500 mr-2">•</span>
                  <span>Review optimization suggestions to reduce costs</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-500 mr-2">•</span>
                  <span>Consider using cheaper models for non-critical tasks</span>
                </li>
                <li className="flex items-start">
                  <span className="text-primary-500 mr-2">•</span>
                  <span>Enable caching to reduce redundant API calls</span>
                </li>
                {willExceed && (
                  <li className="flex items-start">
                    <span className="text-primary-500 mr-2">•</span>
                    <span className="font-semibold text-red-600 dark:text-red-400">
                      Increase budget limit or pause project until review
                    </span>
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};
