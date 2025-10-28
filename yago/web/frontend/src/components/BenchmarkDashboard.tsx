/**
 * YAGO v7.1 - Benchmark Dashboard Component
 * Main dashboard for performance benchmarking and testing
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { benchmarkApi } from '../services/benchmarkApi';
import type {
  GetBenchmarkResultsResponse,
  GetBenchmarkSummaryResponse,
  BenchmarkType,
} from '../types/benchmark';
import { BenchmarkResults } from './BenchmarkResults';
import { PerformanceTrends } from './PerformanceTrends';
import { ComparisonView } from './ComparisonView';

interface BenchmarkDashboardProps {
  projectId: string;
}

type TabType = 'results' | 'trends' | 'comparison';

export const BenchmarkDashboard: React.FC<BenchmarkDashboardProps> = ({
  projectId
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('results');
  const [results, setResults] = useState<GetBenchmarkResultsResponse | null>(null);
  const [summary, setSummary] = useState<GetBenchmarkSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [benchmarkType, setBenchmarkType] = useState<BenchmarkType | 'all'>('all');
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // Load data
  const loadData = async () => {
    try {
      setLoading(true);

      const [resultsData, summaryData] = await Promise.all([
        benchmarkApi.getBenchmarkResults(
          projectId,
          benchmarkType === 'all' ? undefined : benchmarkType,
          50
        ),
        benchmarkApi.getBenchmarkSummary(projectId),
      ]);

      setResults(resultsData);
      setSummary(summaryData);
    } catch (error: any) {
      console.error('Failed to load benchmark data:', error);
      toast.error('Failed to load benchmark data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    // Auto-refresh every 15 seconds
    const interval = setInterval(loadData, 15000);
    setRefreshInterval(interval);

    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
    };
  }, [projectId, benchmarkType]);

  // Handle manual refresh
  const handleRefresh = () => {
    toast.promise(loadData(), {
      loading: 'Refreshing...',
      success: 'Data refreshed',
      error: 'Failed to refresh',
    });
  };

  // Handle run new benchmark
  const handleRunBenchmark = async () => {
    try {
      const response = await benchmarkApi.runBenchmark(projectId, {
        name: 'Manual Benchmark',
        description: 'User-initiated benchmark',
        type: 'all',
        iterations: 10,
        warmup_iterations: 2,
        timeout_seconds: 300,
        parallel_execution: false,
        metrics_to_track: ['latency', 'throughput', 'accuracy', 'cost'],
      });

      toast.success('Benchmark started successfully');
      setTimeout(loadData, 2000); // Refresh after 2 seconds
    } catch (error) {
      toast.error('Failed to start benchmark');
    }
  };

  if (loading && !results) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading benchmark data...</p>
        </div>
      </div>
    );
  }

  if (!results || !summary) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">📊</div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          No Benchmark Data
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Run your first benchmark to see results.
        </p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleRunBenchmark}
          className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
        >
          Run Benchmark
        </motion.button>
      </div>
    );
  }

  const tabs = [
    { id: 'results' as TabType, label: 'Results', icon: '📊', count: results.total },
    { id: 'trends' as TabType, label: 'Trends', icon: '📈', count: summary.trends.length },
    { id: 'comparison' as TabType, label: 'Comparison', icon: '⚖️', count: 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            Benchmark Dashboard
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Performance testing and analysis
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRefresh}
            disabled={loading}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <span className={loading ? 'animate-spin' : ''}>🔄</span>
            <span>Refresh</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRunBenchmark}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 flex items-center space-x-2"
          >
            <span>▶️</span>
            <span>Run Benchmark</span>
          </motion.button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Benchmarks */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl p-6 border border-blue-200 dark:border-blue-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-600 dark:text-blue-400 mb-1">Total Benchmarks</p>
              <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                {summary.summary.total_benchmarks}
              </p>
            </div>
            <div className="text-4xl">📊</div>
          </div>
        </motion.div>

        {/* Avg Duration */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl p-6 border border-green-200 dark:border-green-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 dark:text-green-400 mb-1">Avg Duration</p>
              <p className="text-3xl font-bold text-green-900 dark:text-green-100">
                {(summary.summary.avg_duration_ms / 1000).toFixed(2)}s
              </p>
            </div>
            <div className="text-4xl">⏱️</div>
          </div>
        </motion.div>

        {/* Success Rate */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl p-6 border border-purple-200 dark:border-purple-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-600 dark:text-purple-400 mb-1">Success Rate</p>
              <p className="text-3xl font-bold text-purple-900 dark:text-purple-100">
                {summary.summary.total_benchmarks > 0
                  ? Math.round((summary.summary.completed_benchmarks / summary.summary.total_benchmarks) * 100)
                  : 0}%
              </p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </motion.div>

        {/* Running */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl p-6 border border-orange-200 dark:border-orange-700"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-orange-600 dark:text-orange-400 mb-1">Running</p>
              <p className="text-3xl font-bold text-orange-900 dark:text-orange-100">
                {summary.summary.running_benchmarks}
              </p>
            </div>
            <div className="text-4xl">{summary.summary.running_benchmarks > 0 ? '🔄' : '💤'}</div>
          </div>
        </motion.div>
      </div>

      {/* Type Filter */}
      <div className="flex items-center space-x-3">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Benchmark Type:
        </label>
        <div className="flex space-x-2">
          {['all', 'performance', 'quality', 'cost'].map((type) => (
            <motion.button
              key={type}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setBenchmarkType(type as BenchmarkType | 'all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                benchmarkType === type
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex -mb-px">
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex-1 px-6 py-4 text-center font-medium transition-colors relative
                  ${activeTab === tab.id
                    ? 'text-primary-600 dark:text-primary-400'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }
                `}
              >
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-2xl">{tab.icon}</span>
                  <span>{tab.label}</span>
                  {tab.count > 0 && (
                    <span className={`
                      px-2 py-1 text-xs rounded-full
                      ${activeTab === tab.id
                        ? 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400'
                        : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                      }
                    `}>
                      {tab.count}
                    </span>
                  )}
                </div>
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeBenchmarkTab"
                    className="absolute bottom-0 left-0 right-0 h-1 bg-primary-500"
                  />
                )}
              </motion.button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'results' && (
                <BenchmarkResults
                  projectId={projectId}
                  results={results.results}
                  summary={summary.summary}
                />
              )}
              {activeTab === 'trends' && (
                <PerformanceTrends
                  projectId={projectId}
                  trends={summary.trends}
                />
              )}
              {activeTab === 'comparison' && (
                <ComparisonView projectId={projectId} />
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};
