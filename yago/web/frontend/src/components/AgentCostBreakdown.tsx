/**
 * YAGO v7.1 - Agent Cost Breakdown Component
 * Detailed cost analysis per agent
 */

import React from 'react';
import { motion } from 'framer-motion';
import type { CostSummary } from '../types/cost';

interface AgentCostBreakdownProps {
  summary: CostSummary;
  projectId: string;
}

export const AgentCostBreakdown: React.FC<AgentCostBreakdownProps> = ({ summary }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    }).format(amount);
  };

  const agents = Object.entries(summary.cost_by_agent).map(([agent, cost]) => {
    const calls = summary.calls_by_agent[agent] || 0;
    const tokens = summary.tokens_by_agent[agent] || 0;
    const avgCostPerCall = calls > 0 ? cost / calls : 0;
    const avgTokensPerCall = calls > 0 ? tokens / calls : 0;
    const efficiency = Math.min(100, Math.max(0, 100 - (avgCostPerCall * 100)));

    return {
      agent,
      cost,
      calls,
      tokens,
      avgCostPerCall,
      avgTokensPerCall,
      efficiency,
      percentage: (cost / summary.total_cost) * 100,
    };
  }).sort((a, b) => b.cost - a.cost);

  const getAgentIcon = (agent: string) => {
    const icons: Record<string, string> = {
      'Planner': '🎯',
      'Coder': '💻',
      'Tester': '🧪',
      'Reviewer': '👀',
      'Documenter': '📝',
      'SecurityAgent': '🔒',
      'DevOpsAgent': '🚀',
      'DatabaseAgent': '🗄️',
      'FrontendAgent': '🎨',
      'BackendAgent': '⚙️',
    };
    return icons[agent] || '🤖';
  };

  const getEfficiencyColor = (efficiency: number) => {
    if (efficiency >= 90) return 'text-green-600 dark:text-green-400';
    if (efficiency >= 70) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Agent Performance & Cost Analysis
        </h3>
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {agents.length} agents active
        </span>
      </div>

      <div className="grid gap-4">
        {agents.map((agent, index) => (
          <motion.div
            key={agent.agent}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="text-3xl">{getAgentIcon(agent.agent)}</div>
                <div>
                  <h4 className="text-lg font-bold text-gray-900 dark:text-white">
                    {agent.agent}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {agent.calls} API calls · {agent.tokens.toLocaleString()} tokens
                  </p>
                </div>
              </div>

              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(agent.cost)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {agent.percentage.toFixed(1)}% of total
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                  Avg Cost/Call
                </div>
                <div className="text-sm font-semibold text-gray-900 dark:text-white">
                  {formatCurrency(agent.avgCostPerCall)}
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                  Avg Tokens/Call
                </div>
                <div className="text-sm font-semibold text-gray-900 dark:text-white">
                  {Math.round(agent.avgTokensPerCall).toLocaleString()}
                </div>
              </div>

              <div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                  Efficiency
                </div>
                <div className={`text-sm font-bold ${getEfficiencyColor(agent.efficiency)}`}>
                  {agent.efficiency.toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Efficiency bar */}
            <div className="mt-4">
              <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
                <span>Cost Efficiency</span>
                <span>{agent.efficiency.toFixed(0)}%</span>
              </div>
              <div className="relative w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${agent.efficiency}%` }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                  className={`absolute h-full ${
                    agent.efficiency >= 90
                      ? 'bg-green-500'
                      : agent.efficiency >= 70
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4 p-6 bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-xl">
        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Most Expensive
          </div>
          <div className="font-bold text-gray-900 dark:text-white">
            {agents[0]?.agent || 'N/A'}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {formatCurrency(agents[0]?.cost || 0)}
          </div>
        </div>

        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Most Efficient
          </div>
          <div className="font-bold text-gray-900 dark:text-white">
            {[...agents].sort((a, b) => b.efficiency - a.efficiency)[0]?.agent || 'N/A'}
          </div>
          <div className="text-xs text-green-600 dark:text-green-400">
            {[...agents].sort((a, b) => b.efficiency - a.efficiency)[0]?.efficiency.toFixed(0)}% eff.
          </div>
        </div>

        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Most Active
          </div>
          <div className="font-bold text-gray-900 dark:text-white">
            {[...agents].sort((a, b) => b.calls - a.calls)[0]?.agent || 'N/A'}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {[...agents].sort((a, b) => b.calls - a.calls)[0]?.calls || 0} calls
          </div>
        </div>

        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
            Avg Efficiency
          </div>
          <div className="font-bold text-gray-900 dark:text-white">
            {(agents.reduce((sum, a) => sum + a.efficiency, 0) / agents.length).toFixed(0)}%
          </div>
        </div>
      </div>
    </div>
  );
};
