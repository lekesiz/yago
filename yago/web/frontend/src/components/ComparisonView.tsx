/**
 * YAGO v8.0 - Comparison View Component
 * Compare multiple benchmark results side-by-side
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { benchmarkApi } from '../services/benchmarkApi';
import type { BenchmarkResult, CompareBenchmarksResponse } from '../types/benchmark';

interface ComparisonViewProps {
  projectId: string;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({ projectId }) => {
  const [availableResults, setAvailableResults] = useState<BenchmarkResult[]>([]);
  const [selectedResults, setSelectedResults] = useState<string[]>([]);
  const [comparison, setComparison] = useState<CompareBenchmarksResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Load available results
  useEffect(() => {
    const loadResults = async () => {
      try {
        const data = await benchmarkApi.getBenchmarkResults(projectId, undefined, 20);
        setAvailableResults(data.results.filter(r => r.status === 'completed'));
      } catch (error) {
        console.error('Failed to load results:', error);
        toast.error('Failed to load benchmark results');
      }
    };

    loadResults();
  }, [projectId]);

  // Handle select result
  const handleToggleResult = (resultId: string) => {
    if (selectedResults.includes(resultId)) {
      setSelectedResults(selectedResults.filter(id => id !== resultId));
    } else {
      if (selectedResults.length >= 5) {
        toast.error('Maximum 5 results can be compared');
        return;
      }
      setSelectedResults([...selectedResults, resultId]);
    }
  };

  // Handle compare
  const handleCompare = async () => {
    if (selectedResults.length < 2) {
      toast.error('Please select at least 2 results to compare');
      return;
    }

    try {
      setLoading(true);
      const data = await benchmarkApi.compareBenchmarks(
        selectedResults,
        `Comparison ${new Date().toISOString()}`
      );
      setComparison(data);
      toast.success('Comparison generated successfully');
    } catch (error) {
      toast.error('Failed to generate comparison');
    } finally {
      setLoading(false);
    }
  };

  // Format value
  const formatValue = (value: number, suffix: string = ''): string => {
    return `${value.toFixed(2)}${suffix}`;
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

  return (
    <div className="space-y-6">
      {/* Selection Panel */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Select Benchmarks to Compare
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {selectedResults.length}/5 selected
            </p>
          </div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleCompare}
            disabled={selectedResults.length < 2 || loading}
            className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Comparing...' : 'Compare Selected'}
          </motion.button>
        </div>

        {/* Available Results Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
          {availableResults.map((result) => {
            const isSelected = selectedResults.includes(result.result_id);

            return (
              <motion.button
                key={result.result_id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleToggleResult(result.result_id)}
                className={`text-left p-4 rounded-lg border-2 transition-all ${
                  isSelected
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    #{result.result_id.slice(0, 8)}
                  </div>
                  {isSelected && <span className="text-primary-500">✓</span>}
                </div>
                <div className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                  <div>Latency: {result.metrics.avg_latency_ms.toFixed(0)}ms</div>
                  <div>Accuracy: {(result.metrics.accuracy_score * 100).toFixed(1)}%</div>
                  <div>{formatTime(result.started_at)}</div>
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Comparison Results */}
      {comparison && (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Winner Badge */}
            {comparison.comparison.winner && (
              <div className="bg-gradient-to-r from-yellow-50 to-amber-100 dark:from-yellow-900/20 dark:to-amber-900/20 rounded-xl p-6 border border-yellow-200 dark:border-yellow-700">
                <div className="flex items-center space-x-3">
                  <span className="text-4xl">🏆</span>
                  <div>
                    <h3 className="text-xl font-bold text-yellow-900 dark:text-yellow-100">
                      Best Performer
                    </h3>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">
                      Benchmark #{comparison.comparison.winner.slice(0, 8)}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Improvements */}
            {Object.keys(comparison.comparison.improvements).length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  📊 Performance Improvements
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {Object.entries(comparison.comparison.improvements).map(([metric, improvement]) => (
                    <div
                      key={metric}
                      className={`rounded-lg p-3 ${
                        improvement > 0
                          ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700'
                          : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700'
                      }`}
                    >
                      <div className={`text-xs mb-1 ${
                        improvement > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                      }`}>
                        {metric.replace(/_/g, ' ')}
                      </div>
                      <div className={`text-xl font-bold ${
                        improvement > 0 ? 'text-green-900 dark:text-green-100' : 'text-red-900 dark:text-red-100'
                      }`}>
                        {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Insights */}
            {comparison.insights.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  💡 Insights
                </h3>
                <ul className="space-y-2">
                  {comparison.insights.map((insight, idx) => (
                    <li key={idx} className="flex items-start space-x-2 text-sm text-gray-700 dark:text-gray-300">
                      <span className="text-blue-500 mt-1">•</span>
                      <span>{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            {comparison.recommendations.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  🎯 Recommendations
                </h3>
                <ul className="space-y-2">
                  {comparison.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start space-x-2 text-sm text-gray-700 dark:text-gray-300">
                      <span className="text-primary-500 mt-1">→</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Side-by-Side Comparison Table */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700 overflow-x-auto">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                📋 Detailed Comparison
              </h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                      Metric
                    </th>
                    {comparison.comparison.results.map((result) => (
                      <th
                        key={result.result_id}
                        className="text-right py-3 px-4 font-medium text-gray-900 dark:text-white"
                      >
                        #{result.result_id.slice(0, 8)}
                        {result.result_id === comparison.comparison.winner && ' 🏆'}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">Avg Latency</td>
                    {comparison.comparison.results.map((result) => (
                      <td key={result.result_id} className="text-right py-3 px-4 text-gray-900 dark:text-white">
                        {result.metrics.avg_latency_ms.toFixed(0)}ms
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">Throughput</td>
                    {comparison.comparison.results.map((result) => (
                      <td key={result.result_id} className="text-right py-3 px-4 text-gray-900 dark:text-white">
                        {result.metrics.requests_per_second.toFixed(2)} req/s
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">Accuracy</td>
                    {comparison.comparison.results.map((result) => (
                      <td key={result.result_id} className="text-right py-3 px-4 text-gray-900 dark:text-white">
                        {(result.metrics.accuracy_score * 100).toFixed(1)}%
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">Total Cost</td>
                    {comparison.comparison.results.map((result) => (
                      <td key={result.result_id} className="text-right py-3 px-4 text-gray-900 dark:text-white">
                        ${result.metrics.total_cost.toFixed(4)}
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">Avg Memory</td>
                    {comparison.comparison.results.map((result) => (
                      <td key={result.result_id} className="text-right py-3 px-4 text-gray-900 dark:text-white">
                        {result.metrics.avg_memory_mb.toFixed(0)}MB
                      </td>
                    ))}
                  </tr>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-3 px-4 text-gray-700 dark:text-gray-300">Error Rate</td>
                    {comparison.comparison.results.map((result) => (
                      <td key={result.result_id} className="text-right py-3 px-4 text-gray-900 dark:text-white">
                        {(result.metrics.error_rate * 100).toFixed(2)}%
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </motion.div>
        </AnimatePresence>
      )}

      {/* Empty State */}
      {!comparison && selectedResults.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">⚖️</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Compare Benchmarks
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Select 2 or more benchmarks to compare their performance.
          </p>
        </div>
      )}
    </div>
  );
};
