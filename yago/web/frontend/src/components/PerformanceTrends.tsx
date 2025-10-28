/**
 * YAGO v7.1 - Performance Trends Component
 * Visualize performance trends over time with charts
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import type { PerformanceTrend, MetricType } from '../types/benchmark';

interface PerformanceTrendsProps {
  projectId: string;
  trends: PerformanceTrend[];
}

export const PerformanceTrends: React.FC<PerformanceTrendsProps> = ({
  projectId,
  trends,
}) => {
  const [selectedMetric, setSelectedMetric] = useState<MetricType | 'all'>('all');

  // Get trend direction icon and color
  const getTrendIcon = (direction: 'improving' | 'declining' | 'stable'): string => {
    const icons = {
      improving: '📈',
      declining: '📉',
      stable: '➡️',
    };
    return icons[direction];
  };

  const getTrendColor = (direction: 'improving' | 'declining' | 'stable'): string => {
    const colors = {
      improving: 'from-green-400 to-emerald-600',
      declining: 'from-red-400 to-red-600',
      stable: 'from-gray-400 to-gray-600',
    };
    return colors[direction];
  };

  const getTrendBadgeColor = (direction: 'improving' | 'declining' | 'stable'): string => {
    const colors = {
      improving: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
      declining: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
      stable: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    };
    return colors[direction];
  };

  // Get metric label
  const getMetricLabel = (metric: MetricType): string => {
    const labels: Record<MetricType, string> = {
      latency: 'Latency (ms)',
      throughput: 'Throughput (req/s)',
      accuracy: 'Accuracy (%)',
      cost: 'Cost ($)',
      memory: 'Memory (MB)',
      cpu: 'CPU (%)',
    };
    return labels[metric];
  };

  // Get metric icon
  const getMetricIcon = (metric: MetricType): string => {
    const icons: Record<MetricType, string> = {
      latency: '⚡',
      throughput: '🚀',
      accuracy: '🎯',
      cost: '💰',
      memory: '🧠',
      cpu: '⚙️',
    };
    return icons[metric];
  };

  // Filter trends by selected metric
  const filteredTrends = selectedMetric === 'all'
    ? trends
    : trends.filter(t => t.metric === selectedMetric);

  // Format value based on metric type
  const formatValue = (metric: MetricType, value: number): string => {
    switch (metric) {
      case 'latency':
        return `${value.toFixed(0)}ms`;
      case 'throughput':
        return `${value.toFixed(2)} req/s`;
      case 'accuracy':
        return `${(value * 100).toFixed(1)}%`;
      case 'cost':
        return `$${value.toFixed(4)}`;
      case 'memory':
        return `${value.toFixed(0)}MB`;
      case 'cpu':
        return `${value.toFixed(1)}%`;
      default:
        return value.toFixed(2);
    }
  };

  // Format timestamp
  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (trends.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📈</div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          No Trend Data
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Run more benchmarks to see performance trends.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Metric Filter */}
      <div className="flex items-center space-x-3 overflow-x-auto pb-2">
        <button
          onClick={() => setSelectedMetric('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
            selectedMetric === 'all'
              ? 'bg-primary-500 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          All Metrics
        </button>
        {(['latency', 'throughput', 'accuracy', 'cost', 'memory', 'cpu'] as MetricType[]).map((metric) => (
          <button
            key={metric}
            onClick={() => setSelectedMetric(metric)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              selectedMetric === metric
                ? 'bg-primary-500 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            {getMetricIcon(metric)} {metric.charAt(0).toUpperCase() + metric.slice(1)}
          </button>
        ))}
      </div>

      {/* Trends Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredTrends.map((trend, index) => {
          const latestValue = trend.data_points[trend.data_points.length - 1]?.value || 0;
          const earliestValue = trend.data_points[0]?.value || 0;
          const minValue = Math.min(...trend.data_points.map(d => d.value));
          const maxValue = Math.max(...trend.data_points.map(d => d.value));

          return (
            <motion.div
              key={`${trend.metric}-${index}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">{getMetricIcon(trend.metric)}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {getMetricLabel(trend.metric)}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {trend.data_points.length} data points
                    </p>
                  </div>
                </div>

                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTrendBadgeColor(trend.trend_direction)}`}>
                  {getTrendIcon(trend.trend_direction)} {trend.trend_direction.toUpperCase()}
                </span>
              </div>

              {/* Current Value & Improvement */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Current Value</div>
                  <div className="text-xl font-bold text-gray-900 dark:text-white">
                    {formatValue(trend.metric, latestValue)}
                  </div>
                </div>

                <div className={`rounded-lg p-3 bg-gradient-to-r ${getTrendColor(trend.trend_direction)}`}>
                  <div className="text-xs text-white/90 mb-1">Improvement Rate</div>
                  <div className="text-xl font-bold text-white">
                    {trend.improvement_rate_pct > 0 ? '+' : ''}
                    {trend.improvement_rate_pct.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Min/Max Stats */}
              <div className="grid grid-cols-3 gap-2 mb-4">
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 border border-blue-200 dark:border-blue-700">
                  <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">First</div>
                  <div className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                    {formatValue(trend.metric, earliestValue)}
                  </div>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-2 border border-green-200 dark:border-green-700">
                  <div className="text-xs text-green-600 dark:text-green-400 mb-1">Best</div>
                  <div className="text-sm font-semibold text-green-900 dark:text-green-100">
                    {formatValue(trend.metric, minValue)}
                  </div>
                </div>
                <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-2 border border-red-200 dark:border-red-700">
                  <div className="text-xs text-red-600 dark:text-red-400 mb-1">Worst</div>
                  <div className="text-sm font-semibold text-red-900 dark:text-red-100">
                    {formatValue(trend.metric, maxValue)}
                  </div>
                </div>
              </div>

              {/* Simple Sparkline Chart */}
              <div className="relative h-24 bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3">
                <svg width="100%" height="100%" className="overflow-visible">
                  {/* Grid lines */}
                  <line x1="0" y1="0" x2="100%" y2="0" stroke="currentColor" strokeWidth="1" className="text-gray-300 dark:text-gray-600" />
                  <line x1="0" y1="50%" x2="100%" y2="50%" stroke="currentColor" strokeWidth="1" className="text-gray-300 dark:text-gray-600" strokeDasharray="2,2" />
                  <line x1="0" y1="100%" x2="100%" y2="100%" stroke="currentColor" strokeWidth="1" className="text-gray-300 dark:text-gray-600" />

                  {/* Trend Line */}
                  <polyline
                    points={trend.data_points.map((point, i) => {
                      const x = (i / (trend.data_points.length - 1)) * 100;
                      const normalizedValue = ((point.value - minValue) / (maxValue - minValue || 1)) * 100;
                      const y = 100 - normalizedValue; // Invert Y axis
                      return `${x}%,${y}%`;
                    }).join(' ')}
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    className={`${
                      trend.trend_direction === 'improving' ? 'text-green-500' :
                      trend.trend_direction === 'declining' ? 'text-red-500' :
                      'text-gray-500'
                    }`}
                  />

                  {/* Data Points */}
                  {trend.data_points.map((point, i) => {
                    const x = (i / (trend.data_points.length - 1)) * 100;
                    const normalizedValue = ((point.value - minValue) / (maxValue - minValue || 1)) * 100;
                    const y = 100 - normalizedValue;
                    return (
                      <circle
                        key={i}
                        cx={`${x}%`}
                        cy={`${y}%`}
                        r="3"
                        fill="currentColor"
                        className={`${
                          trend.trend_direction === 'improving' ? 'text-green-500' :
                          trend.trend_direction === 'declining' ? 'text-red-500' :
                          'text-gray-500'
                        }`}
                      />
                    );
                  })}
                </svg>
              </div>

              {/* Recent Data Points */}
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Recent Data Points
                </div>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {trend.data_points.slice(-5).reverse().map((point, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span className="text-gray-600 dark:text-gray-400">
                        {point.label || formatTime(point.timestamp)}
                      </span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {formatValue(trend.metric, point.value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
