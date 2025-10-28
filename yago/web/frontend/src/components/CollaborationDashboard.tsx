/**
 * YAGO v7.1 - Collaboration Dashboard Component
 * Main dashboard for monitoring multi-agent collaboration
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { collaborationApi } from '../services/collaborationApi';
import type {
  GetAgentsStatusResponse,
  CollaborationHealth,
  WebSocketMessage
} from '../types/collaboration';
import { AgentStatusPanel } from './AgentStatusPanel';
import { MessageFlow } from './MessageFlow';
import { SharedContextView } from './SharedContextView';
import { ConflictResolver } from './ConflictResolver';

interface CollaborationDashboardProps {
  projectId: string;
}

type TabType = 'agents' | 'messages' | 'context' | 'conflicts';

export const CollaborationDashboard: React.FC<CollaborationDashboardProps> = ({
  projectId
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('agents');
  const [agentsStatus, setAgentsStatus] = useState<GetAgentsStatusResponse | null>(null);
  const [health, setHealth] = useState<CollaborationHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // Load data
  const loadData = async () => {
    try {
      setLoading(true);

      const [agentsData, healthData] = await Promise.all([
        collaborationApi.getAgentsStatus(projectId),
        collaborationApi.getHealth(),
      ]);

      setAgentsStatus(agentsData);
      setHealth(healthData);
    } catch (error: any) {
      console.error('Failed to load collaboration data:', error);
      toast.error('Failed to load collaboration data');
    } finally {
      setLoading(false);
    }
  };

  // Setup WebSocket connection
  useEffect(() => {
    loadData();

    // Auto-refresh every 10 seconds
    const interval = setInterval(loadData, 10000);
    setRefreshInterval(interval);

    // Setup WebSocket for real-time updates
    try {
      const websocket = collaborationApi.createWebSocket(projectId);

      websocket.onopen = () => {
        console.log('WebSocket connected');
        websocket.send(JSON.stringify({ type: 'ping' }));
      };

      websocket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          if (message.type === 'agent_status') {
            // Refresh agents status
            loadData();
          } else if (message.type === 'agent_message') {
            // Show notification for new message
            toast.success('New agent message received');
            loadData();
          } else if (message.type === 'conflict') {
            // Show warning for new conflict
            toast.error('⚠️ New conflict detected!');
            loadData();
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      websocket.onclose = () => {
        console.log('WebSocket disconnected');
      };

      setWs(websocket);
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }

    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
      if (ws) ws.close();
    };
  }, [projectId]);

  // Handle manual refresh
  const handleRefresh = () => {
    toast.promise(loadData(), {
      loading: 'Refreshing...',
      success: 'Data refreshed',
      error: 'Failed to refresh',
    });
  };

  if (loading && !agentsStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading collaboration data...</p>
        </div>
      </div>
    );
  }

  if (!agentsStatus) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">🤖</div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          No Collaboration Data
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Start a project to see agent collaboration.
        </p>
      </div>
    );
  }

  const tabs = [
    { id: 'agents' as TabType, label: 'Agents', icon: '🤖', count: agentsStatus?.total_agents || 0 },
    { id: 'messages' as TabType, label: 'Messages', icon: '💬', count: health?.total_messages || 0 },
    { id: 'context' as TabType, label: 'Context', icon: '📝', count: 0 },
    { id: 'conflicts' as TabType, label: 'Conflicts', icon: '⚔️', count: health?.active_conflicts || 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            Collaboration Dashboard
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitor multi-agent collaboration in real-time
          </p>
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleRefresh}
          disabled={loading}
          className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <span className={loading ? 'animate-spin' : ''}>🔄</span>
          <span>Refresh</span>
        </motion.button>
      </div>

      {/* Health Overview Cards */}
      {health && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Active Agents */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl p-6 border border-blue-200 dark:border-blue-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 dark:text-blue-400 mb-1">Active Agents</p>
                <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                  {agentsStatus.total_agents}
                </p>
              </div>
              <div className="text-4xl">🤖</div>
            </div>
          </motion.div>

          {/* Total Messages */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-xl p-6 border border-green-200 dark:border-green-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600 dark:text-green-400 mb-1">Total Messages</p>
                <p className="text-3xl font-bold text-green-900 dark:text-green-100">
                  {health.total_messages}
                </p>
              </div>
              <div className="text-4xl">💬</div>
            </div>
          </motion.div>

          {/* Active Conflicts */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-xl p-6 border border-orange-200 dark:border-orange-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-orange-600 dark:text-orange-400 mb-1">Conflicts</p>
                <p className="text-3xl font-bold text-orange-900 dark:text-orange-100">
                  {health.active_conflicts}
                </p>
              </div>
              <div className="text-4xl">⚔️</div>
            </div>
          </motion.div>

          {/* WebSocket Status */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl p-6 border border-purple-200 dark:border-purple-700"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600 dark:text-purple-400 mb-1">Connections</p>
                <p className="text-3xl font-bold text-purple-900 dark:text-purple-100">
                  {health.websocket_connections}
                </p>
              </div>
              <div className="text-4xl">{ws?.readyState === WebSocket.OPEN ? '🟢' : '🔴'}</div>
            </div>
          </motion.div>
        </div>
      )}

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
                    layoutId="activeTab"
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
              {activeTab === 'agents' && (
                <AgentStatusPanel agents={agentsStatus.agents} />
              )}
              {activeTab === 'messages' && (
                <MessageFlow projectId={projectId} />
              )}
              {activeTab === 'context' && (
                <SharedContextView projectId={projectId} />
              )}
              {activeTab === 'conflicts' && (
                <ConflictResolver projectId={projectId} />
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};
