/**
 * YAGO v7.1 - Cost Dashboard Component
 * Main cost tracking dashboard with real-time updates
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { costApi } from '../services/costApi';
import type { CostSummary, BudgetStatus } from '../types/cost';
import { CostChart } from './CostChart';
import { AgentCostBreakdown } from './AgentCostBreakdown';
import { CostOptimizationSuggestions } from './CostOptimizationSuggestions';
import { BudgetAlert } from './BudgetAlert';

interface CostDashboardProps {
  projectId: string;
}

export const CostDashboard: React.FC<CostDashboardProps> = ({ projectId }) => {
  const [summary, setSummary] = useState<CostSummary | null>(null);
  const [budgetStatus, setBudgetStatus] = useState<BudgetStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'agents' | 'optimizations' | 'history'>('overview');
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // Load data
  const loadData = async () => {
    try {
      setLoading(true);

      // Load cost summary
      const summaryData = await costApi.getCostSummary(projectId);
      setSummary(summaryData);

      // Try to load budget status (may not exist)
      try {
        const budgetData = await costApi.getBudgetStatus(projectId);
        setBudgetStatus(budgetData);
      } catch (err) {
        // Budget not set - that's okay
        setBudgetStatus(null);
      }
    } catch (error: any) {
      console.error('Failed to load cost data:', error);
      if (error.response?.status !== 404) {
        toast.error('Failed to load cost data');
      }
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    loadData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    setRefreshInterval(interval);

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [projectId]);

  // Format currency
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    }).format(amount);
  };

  // Format number with commas
  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading cost data...</p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-6xl mb-4">💰</div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">
            No Cost Data Yet
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Cost tracking will appear here once API calls are made.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                💰 Cost Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Real-time cost tracking and optimization
              </p>
            </div>
            <button
              onClick={loadData}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
              disabled={loading}
            >
              {loading ? '🔄 Refreshing...' : '🔄 Refresh'}
            </button>
          </div>
        </motion.div>

        {/* Budget Alert (if applicable) */}
        {budgetStatus && (
          <BudgetAlert budgetStatus={budgetStatus} />
        )}

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Cost */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Cost
              </h3>
              <span className="text-2xl">💵</span>
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {formatCurrency(summary.total_cost)}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              {formatNumber(summary.total_api_calls)} API calls
            </p>
          </motion.div>

          {/* Total Tokens */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Tokens
              </h3>
              <span className="text-2xl">🔤</span>
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {formatNumber(summary.total_tokens)}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              {formatCurrency(summary.cost_per_1k_tokens)} per 1K tokens
            </p>
          </motion.div>

          {/* Average Cost per Call */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Avg Cost/Call
              </h3>
              <span className="text-2xl">📊</span>
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {formatCurrency(summary.avg_cost_per_call)}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              {formatNumber(summary.avg_tokens_per_call)} tokens avg
            </p>
          </motion.div>

          {/* API Calls per Hour */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Calls/Hour
              </h3>
              <span className="text-2xl">⚡</span>
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">
              {summary.calls_per_hour.toFixed(1)}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              {summary.avg_duration_ms.toFixed(0)}ms avg duration
            </p>
          </motion.div>
        </div>

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <div className="flex">
              {[
                { id: 'overview', label: '📈 Overview', icon: '📈' },
                { id: 'agents', label: '🤖 Agents', icon: '🤖' },
                { id: 'optimizations', label: '💡 Optimizations', icon: '💡' },
                { id: 'history', label: '📜 History', icon: '📜' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`
                    px-6 py-4 font-medium transition-colors relative
                    ${activeTab === tab.id
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                    }
                  `}
                >
                  {tab.label}
                  {activeTab === tab.id && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"
                    />
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'overview' && (
              <CostChart
                summary={summary}
                projectId={projectId}
              />
            )}

            {activeTab === 'agents' && (
              <AgentCostBreakdown
                summary={summary}
                projectId={projectId}
              />
            )}

            {activeTab === 'optimizations' && (
              <CostOptimizationSuggestions
                projectId={projectId}
              />
            )}

            {activeTab === 'history' && (
              <div className="text-center text-gray-600 dark:text-gray-400 py-8">
                Cost history chart coming soon...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
