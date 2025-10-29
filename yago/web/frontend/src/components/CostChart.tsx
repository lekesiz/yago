/**
 * YAGO v8.0 - Cost Chart Component
 * Beautiful data visualizations for cost breakdown
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import type { CostSummary } from '../types/cost';

interface CostChartProps {
  summary: CostSummary;
  projectId: string;
}

export const CostChart: React.FC<CostChartProps> = ({ summary }) => {
  // Format currency
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    }).format(amount);
  };

  // Prepare model breakdown data
  const modelBreakdown = useMemo(() => {
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-purple-500',
      'bg-orange-500',
      'bg-pink-500',
      'bg-indigo-500',
    ];

    return Object.entries(summary.cost_by_model).map(([model, cost], index) => {
      const percentage = (cost / summary.total_cost) * 100;
      const calls = summary.calls_by_model[model] || 0;
      const tokens = summary.tokens_by_model[model] || 0;

      return {
        model,
        cost,
        percentage,
        calls,
        tokens,
        color: colors[index % colors.length],
      };
    }).sort((a, b) => b.cost - a.cost);
  }, [summary]);

  // Prepare agent breakdown data
  const agentBreakdown = useMemo(() => {
    const colors = [
      'bg-emerald-500',
      'bg-cyan-500',
      'bg-violet-500',
      'bg-rose-500',
      'bg-amber-500',
      'bg-lime-500',
    ];

    return Object.entries(summary.cost_by_agent).map(([agent, cost], index) => {
      const percentage = (cost / summary.total_cost) * 100;
      const calls = summary.calls_by_agent[agent] || 0;
      const tokens = summary.tokens_by_agent[agent] || 0;

      return {
        agent,
        cost,
        percentage,
        calls,
        tokens,
        color: colors[index % colors.length],
      };
    }).sort((a, b) => b.cost - a.cost);
  }, [summary]);

  // Prepare phase breakdown data
  const phaseBreakdown = useMemo(() => {
    const colors = [
      'bg-sky-500',
      'bg-teal-500',
      'bg-fuchsia-500',
      'bg-red-500',
      'bg-yellow-500',
    ];

    return Object.entries(summary.cost_by_phase).map(([phase, cost], index) => {
      const percentage = (cost / summary.total_cost) * 100;
      const tokens = summary.tokens_by_phase[phase] || 0;

      return {
        phase,
        cost,
        percentage,
        tokens,
        color: colors[index % colors.length],
      };
    }).sort((a, b) => b.cost - a.cost);
  }, [summary]);

  return (
    <div className="space-y-8">
      {/* Cost by Model */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          💎 Cost by AI Model
        </h3>
        <div className="space-y-3">
          {modelBreakdown.map((item, index) => (
            <motion.div
              key={item.model}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${item.color}`} />
                  <span className="font-medium text-gray-900 dark:text-white">
                    {item.model}
                  </span>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900 dark:text-white">
                    {formatCurrency(item.cost)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {item.percentage.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Progress bar */}
              <div className="relative w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.percentage}%` }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                  className={`absolute h-full ${item.color}`}
                />
              </div>

              <div className="flex justify-between mt-2 text-sm text-gray-600 dark:text-gray-400">
                <span>{item.calls} calls</span>
                <span>{item.tokens.toLocaleString()} tokens</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Cost by Agent */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          🤖 Cost by Agent
        </h3>
        <div className="space-y-3">
          {agentBreakdown.map((item, index) => (
            <motion.div
              key={item.agent}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${item.color}`} />
                  <span className="font-medium text-gray-900 dark:text-white">
                    {item.agent}
                  </span>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900 dark:text-white">
                    {formatCurrency(item.cost)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {item.percentage.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Progress bar */}
              <div className="relative w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.percentage}%` }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                  className={`absolute h-full ${item.color}`}
                />
              </div>

              <div className="flex justify-between mt-2 text-sm text-gray-600 dark:text-gray-400">
                <span>{item.calls} API calls</span>
                <span>{item.tokens.toLocaleString()} tokens</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Cost by Phase */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          ⚡ Cost by Project Phase
        </h3>
        <div className="space-y-3">
          {phaseBreakdown.map((item, index) => (
            <motion.div
              key={item.phase}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${item.color}`} />
                  <span className="font-medium text-gray-900 dark:text-white capitalize">
                    {item.phase}
                  </span>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900 dark:text-white">
                    {formatCurrency(item.cost)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {item.percentage.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Progress bar */}
              <div className="relative w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.percentage}%` }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                  className={`absolute h-full ${item.color}`}
                />
              </div>

              <div className="flex justify-between mt-2 text-sm text-gray-600 dark:text-gray-400">
                <span>{item.tokens.toLocaleString()} tokens</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Summary Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Most Used Model
          </div>
          <div className="font-bold text-gray-900 dark:text-white">
            {modelBreakdown[0]?.model.split('-').slice(0, 2).join(' ') || 'N/A'}
          </div>
        </div>

        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Most Active Agent
          </div>
          <div className="font-bold text-gray-900 dark:text-white">
            {agentBreakdown[0]?.agent || 'N/A'}
          </div>
        </div>

        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Current Phase
          </div>
          <div className="font-bold text-gray-900 dark:text-white capitalize">
            {phaseBreakdown[0]?.phase || 'N/A'}
          </div>
        </div>

        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Efficiency
          </div>
          <div className="font-bold text-green-600 dark:text-green-400">
            {((1 - summary.cost_per_1k_tokens / 10) * 100).toFixed(0)}%
          </div>
        </div>
      </div>
    </div>
  );
};
