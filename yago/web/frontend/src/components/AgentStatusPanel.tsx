/**
 * YAGO v8.0 - Agent Status Panel Component
 * Real-time monitoring of agent activities and status
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import type { Agent } from '../types/collaboration';
import { AgentType, AgentStatus } from '../types/collaboration';

interface AgentStatusPanelProps {
  agents: Agent[];
}

export const AgentStatusPanel: React.FC<AgentStatusPanelProps> = ({
  agents
}) => {
  // Agent type icons and colors
  const getAgentIcon = (agentType: AgentType): string => {
    const icons: Record<AgentType, string> = {
      [AgentType.PLANNER]: '🎯',
      [AgentType.CODER]: '💻',
      [AgentType.TESTER]: '🧪',
      [AgentType.REVIEWER]: '👀',
      [AgentType.DOCUMENTER]: '📝',
      [AgentType.SECURITY]: '🔒',
      [AgentType.DEVOPS]: '⚙️',
      [AgentType.DATABASE]: '🗄️',
      [AgentType.FRONTEND]: '🎨',
      [AgentType.BACKEND]: '🔧',
    };
    return icons[agentType] || '🤖';
  };

  const getStatusColor = (status: AgentStatus): string => {
    const colors: Record<AgentStatus, string> = {
      [AgentStatus.IDLE]: 'from-gray-400 to-gray-500',
      [AgentStatus.BUSY]: 'from-blue-400 to-blue-600',
      [AgentStatus.WAITING]: 'from-yellow-400 to-yellow-600',
      [AgentStatus.ERROR]: 'from-red-400 to-red-600',
    };
    return colors[status];
  };

  const getStatusBadgeColor = (status: AgentStatus): string => {
    const colors: Record<AgentStatus, string> = {
      [AgentStatus.IDLE]: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      [AgentStatus.BUSY]: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
      [AgentStatus.WAITING]: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
      [AgentStatus.ERROR]: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    };
    return colors[status];
  };

  const getStatusLabel = (status: AgentStatus): string => {
    const labels: Record<AgentStatus, string> = {
      [AgentStatus.IDLE]: 'Idle',
      [AgentStatus.BUSY]: 'Active',
      [AgentStatus.WAITING]: 'Waiting',
      [AgentStatus.ERROR]: 'Error',
    };
    return labels[status];
  };

  // Calculate agent statistics
  const stats = useMemo(() => {
    const totalMessages = agents.reduce(
      (sum, agent) => sum + agent.messages_sent + agent.messages_received,
      0
    );
    const totalTasks = agents.reduce(
      (sum, agent) => sum + agent.tasks_completed + agent.tasks_failed,
      0
    );
    const successRate = totalTasks > 0
      ? (agents.reduce((sum, agent) => sum + agent.tasks_completed, 0) / totalTasks) * 100
      : 0;

    const activeAgents = agents.filter(a => a.status === AgentStatus.BUSY).length;
    const idleAgents = agents.filter(a => a.status === AgentStatus.IDLE).length;
    const errorAgents = agents.filter(a => a.status === AgentStatus.ERROR).length;

    return {
      totalMessages,
      totalTasks,
      successRate,
      activeAgents,
      idleAgents,
      errorAgents,
    };
  }, [agents]);

  // Sort agents by status priority (active first, then waiting, idle, error)
  const sortedAgents = useMemo(() => {
    const priority: Record<AgentStatus, number> = {
      [AgentStatus.BUSY]: 1,
      [AgentStatus.WAITING]: 2,
      [AgentStatus.IDLE]: 3,
      [AgentStatus.ERROR]: 4,
    };
    return [...agents].sort((a, b) => priority[a.status] - priority[b.status]);
  }, [agents]);

  // Format timestamp to relative time
  const formatRelativeTime = (timestamp: string): string => {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);

    if (diffSec < 60) return `${diffSec}s ago`;
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHour < 24) return `${diffHour}h ago`;
    return `${Math.floor(diffHour / 24)}d ago`;
  };

  if (agents.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🤖</div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          No Agents Active
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Agents will appear here when the collaboration starts.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
          <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">Active</div>
          <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
            {stats.activeAgents}
          </div>
        </div>

        <div className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/20 dark:to-gray-800/20 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Idle</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {stats.idleAgents}
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-4 border border-green-200 dark:border-green-700">
          <div className="text-xs text-green-600 dark:text-green-400 mb-1">Success Rate</div>
          <div className="text-2xl font-bold text-green-900 dark:text-green-100">
            {stats.successRate.toFixed(0)}%
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
          <div className="text-xs text-purple-600 dark:text-purple-400 mb-1">Total Tasks</div>
          <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
            {stats.totalTasks}
          </div>
        </div>
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {sortedAgents.map((agent, index) => {
          const efficiency = agent.tasks_completed + agent.tasks_failed > 0
            ? (agent.tasks_completed / (agent.tasks_completed + agent.tasks_failed)) * 100
            : 0;

          return (
            <motion.div
              key={agent.agent_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="text-4xl">{getAgentIcon(agent.agent_type)}</div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {agent.agent_type}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      ID: {agent.agent_id.slice(0, 8)}...
                    </p>
                  </div>
                </div>

                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeColor(agent.status)}`}>
                  {getStatusLabel(agent.status)}
                </span>
              </div>

              {/* Current Task */}
              {agent.current_task && (
                <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Current Task</div>
                  <div className="text-sm text-gray-900 dark:text-white font-medium">
                    {agent.current_task}
                  </div>
                </div>
              )}

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    📨 Messages Sent
                  </div>
                  <div className="text-xl font-bold text-gray-900 dark:text-white">
                    {agent.messages_sent}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/50 dark:to-gray-800/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    📬 Received
                  </div>
                  <div className="text-xl font-bold text-gray-900 dark:text-white">
                    {agent.messages_received}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-3">
                  <div className="text-xs text-green-600 dark:text-green-400 mb-1">
                    ✅ Completed
                  </div>
                  <div className="text-xl font-bold text-green-900 dark:text-green-100">
                    {agent.tasks_completed}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-lg p-3">
                  <div className="text-xs text-red-600 dark:text-red-400 mb-1">
                    ❌ Failed
                  </div>
                  <div className="text-xl font-bold text-red-900 dark:text-red-100">
                    {agent.tasks_failed}
                  </div>
                </div>
              </div>

              {/* Efficiency Bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Efficiency</span>
                  <span className={`font-bold ${
                    efficiency >= 90 ? 'text-green-600 dark:text-green-400' :
                    efficiency >= 70 ? 'text-yellow-600 dark:text-yellow-400' :
                    'text-red-600 dark:text-red-400'
                  }`}>
                    {efficiency.toFixed(0)}%
                  </span>
                </div>

                <div className="relative w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${efficiency}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    className={`absolute h-full bg-gradient-to-r ${
                      efficiency >= 90 ? 'from-green-400 to-green-600' :
                      efficiency >= 70 ? 'from-yellow-400 to-yellow-600' :
                      'from-red-400 to-red-600'
                    }`}
                  />
                </div>
              </div>

              {/* Last Activity */}
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Last activity: <span className="font-medium">{formatRelativeTime(agent.last_activity)}</span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
