/**
 * YAGO v7.1 - Benchmark Results Component
 * Display individual benchmark results with detailed metrics
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { benchmarkApi } from '../services/benchmarkApi';
import type { BenchmarkResult, BenchmarkSummary, BenchmarkStatus } from '../types/benchmark';

interface BenchmarkResultsProps {
  projectId: string;
  results: BenchmarkResult[];
  summary: BenchmarkSummary;
}

export const BenchmarkResults: React.FC<BenchmarkResultsProps> = ({
  projectId,
  results,
  summary,
}) => {
  const [expandedResultId, setExpandedResultId] = useState<string | null>(null);
  const [selectedResults, setSelectedResults] = useState<Set<string>>(new Set());

  // Get status color and badge
  const getStatusColor = (status: BenchmarkStatus): string => {
    const colors = {
      pending: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      running: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
      completed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
      failed: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    };
    return colors[status];
  };

  const getStatusIcon = (status: BenchmarkStatus): string => {
    const icons = {
      pending: '⏳',
      running: '🔄',
      completed: '✅',
      failed: '❌',
    };
    return icons[status];
  };

  // Format duration
  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
    return `${(ms / 60000).toFixed(2)}min`;
  };

  // Format timestamp
  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Handle select result for comparison
  const handleSelectResult = (resultId: string) => {
    const newSelected = new Set(selectedResults);
    if (newSelected.has(resultId)) {
      newSelected.delete(resultId);
    } else {
      if (newSelected.size >= 5) {
        toast.error('Maximum 5 results can be selected for comparison');
        return;
      }
      newSelected.add(resultId);
    }
    setSelectedResults(newSelected);
  };

  // Handle delete result
  const handleDeleteResult = async (resultId: string) => {
    if (!confirm('Are you sure you want to delete this benchmark result?')) {
      return;
    }

    try {
      await benchmarkApi.deleteBenchmark(resultId);
      toast.success('Benchmark deleted successfully');
      window.location.reload(); // Simple reload for now
    } catch (error) {
      toast.error('Failed to delete benchmark');
    }
  };

  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📊</div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          No Benchmark Results
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Run a benchmark to see results here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      {summary.best_performance && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Best Performance */}
          <div className="bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/20 dark:to-emerald-800/20 rounded-lg p-4 border border-green-200 dark:border-green-700">
            <div className="text-xs text-green-600 dark:text-green-400 mb-1">🏆 Best Performance</div>
            <div className="text-xl font-bold text-green-900 dark:text-green-100">
              {summary.best_performance.metrics.avg_latency_ms.toFixed(0)}ms
            </div>
            <div className="text-xs text-green-700 dark:text-green-300 mt-1">
              {formatTime(summary.best_performance.started_at)}
            </div>
          </div>

          {/* Worst Performance */}
          {summary.worst_performance && (
            <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-lg p-4 border border-red-200 dark:border-red-700">
              <div className="text-xs text-red-600 dark:text-red-400 mb-1">⚠️ Worst Performance</div>
              <div className="text-xl font-bold text-red-900 dark:text-red-100">
                {summary.worst_performance.metrics.avg_latency_ms.toFixed(0)}ms
              </div>
              <div className="text-xs text-red-700 dark:text-red-300 mt-1">
                {formatTime(summary.worst_performance.started_at)}
              </div>
            </div>
          )}

          {/* Latest Result */}
          {summary.latest_result && (
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
              <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">🕒 Latest Result</div>
              <div className="text-xl font-bold text-blue-900 dark:text-blue-100">
                {summary.latest_result.metrics.avg_latency_ms.toFixed(0)}ms
              </div>
              <div className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                {formatTime(summary.latest_result.started_at)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Selected Results Actions */}
      {selectedResults.size > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 border border-primary-200 dark:border-primary-700"
        >
          <div className="flex items-center justify-between">
            <div className="text-sm text-primary-900 dark:text-primary-100">
              {selectedResults.size} result(s) selected for comparison
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setSelectedResults(new Set())}
                className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
              >
                Clear
              </button>
              <button
                onClick={() => {
                  // Navigate to comparison tab with selected results
                  toast.success('Comparison view not yet implemented');
                }}
                className="px-3 py-1 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600"
              >
                Compare Selected
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Results List */}
      <div className="space-y-4">
        {results.map((result, index) => {
          const isSelected = selectedResults.has(result.result_id);

          return (
            <motion.div
              key={result.result_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border-2 transition-colors ${
                isSelected
                  ? 'border-primary-500'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => handleSelectResult(result.result_id)}
                    className="w-5 h-5 rounded border-gray-300 text-primary-500 focus:ring-primary-500"
                  />
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Benchmark #{result.result_id.slice(0, 8)}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(result.status)}`}>
                        {getStatusIcon(result.status)} {result.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Started: {formatTime(result.started_at)}
                      {result.completed_at && ` • Completed: ${formatTime(result.completed_at)}`}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => handleDeleteResult(result.result_id)}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  🗑️
                </button>
              </div>

              {/* Key Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Duration</div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">
                    {formatDuration(result.duration_ms)}
                  </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Avg Latency</div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">
                    {result.metrics.avg_latency_ms.toFixed(0)}ms
                  </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Iterations</div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">
                    {result.iterations_completed}/{result.iterations_completed + result.iterations_failed}
                  </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Accuracy</div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">
                    {(result.metrics.accuracy_score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Expand/Collapse Button */}
              <button
                onClick={() => setExpandedResultId(expandedResultId === result.result_id ? null : result.result_id)}
                className="text-sm text-primary-600 dark:text-primary-400 hover:underline mb-3"
              >
                {expandedResultId === result.result_id ? 'Hide' : 'Show'} Detailed Metrics
              </button>

              {/* Detailed Metrics */}
              <AnimatePresence>
                {expandedResultId === result.result_id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-gray-200 dark:border-gray-700 pt-4"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Performance Metrics */}
                      <div className="space-y-2">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">⚡ Performance</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Min Latency:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{result.metrics.min_latency_ms.toFixed(0)}ms</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Max Latency:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{result.metrics.max_latency_ms.toFixed(0)}ms</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">P95 Latency:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{result.metrics.p95_latency_ms.toFixed(0)}ms</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">P99 Latency:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{result.metrics.p99_latency_ms.toFixed(0)}ms</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Requests/sec:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{result.metrics.requests_per_second.toFixed(2)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Quality & Resource Metrics */}
                      <div className="space-y-2">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">📊 Quality & Resources</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Precision:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{(result.metrics.precision_score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Recall:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{(result.metrics.recall_score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">F1 Score:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{(result.metrics.f1_score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Avg Memory:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{result.metrics.avg_memory_mb.toFixed(0)}MB</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Avg CPU:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{result.metrics.avg_cpu_percent.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>

                      {/* Cost & Error Metrics */}
                      <div className="space-y-2">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">💰 Cost</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Total Cost:</span>
                            <span className="font-medium text-gray-900 dark:text-white">${result.metrics.total_cost.toFixed(4)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Cost/Request:</span>
                            <span className="font-medium text-gray-900 dark:text-white">${result.metrics.cost_per_request.toFixed(6)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Total Tokens:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{result.metrics.total_tokens.toLocaleString()}</span>
                          </div>
                        </div>
                      </div>

                      {/* Error Metrics */}
                      <div className="space-y-2">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">⚠️ Errors</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Error Rate:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{(result.metrics.error_rate * 100).toFixed(2)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Timeout Rate:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{(result.metrics.timeout_rate * 100).toFixed(2)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Retry Rate:</span>
                            <span className="font-medium text-gray-900 dark:text-white">{(result.metrics.retry_rate * 100).toFixed(2)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Error Message */}
                    {result.error && (
                      <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-700">
                        <div className="text-sm font-medium text-red-700 dark:text-red-300 mb-1">Error:</div>
                        <p className="text-sm text-red-900 dark:text-red-100">{result.error}</p>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
