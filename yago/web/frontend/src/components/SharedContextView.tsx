/**
 * YAGO v8.0 - Shared Context View Component
 * Display and manage shared context across agents
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { collaborationApi } from '../services/collaborationApi';
import type { SharedContext, Issue, Decision } from '../types/collaboration';

interface SharedContextViewProps {
  projectId: string;
}

export const SharedContextView: React.FC<SharedContextViewProps> = ({ projectId }) => {
  const [context, setContext] = useState<SharedContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'tech' | 'architecture' | 'issues' | 'decisions'>('tech');

  // Load shared context
  useEffect(() => {
    const loadContext = async () => {
      try {
        setLoading(true);
        const data = await collaborationApi.getSharedContext(projectId);
        setContext(data);
      } catch (error: any) {
        console.error('Failed to load shared context:', error);
        toast.error('Failed to load shared context');
      } finally {
        setLoading(false);
      }
    };

    loadContext();
    const interval = setInterval(loadContext, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, [projectId]);

  // Get issue severity color
  const getIssueSeverityColor = (severity: 'low' | 'medium' | 'high' | 'critical'): string => {
    const colors = {
      low: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
      high: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
      critical: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    };
    return colors[severity];
  };

  // Get issue status color
  const getIssueStatusColor = (status: 'open' | 'in_progress' | 'resolved' | 'closed'): string => {
    const colors = {
      open: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
      in_progress: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
      resolved: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
      closed: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    };
    return colors[status];
  };

  // Get decision impact color
  const getDecisionImpactColor = (impact: 'low' | 'medium' | 'high'): string => {
    const colors = {
      low: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
      medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
      high: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    };
    return colors[impact];
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

  if (loading && !context) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading shared context...</p>
        </div>
      </div>
    );
  }

  if (!context) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">📝</div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          No Shared Context
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Shared context will appear here when agents start collaborating.
        </p>
      </div>
    );
  }

  const tabs = [
    { id: 'tech' as const, label: 'Tech Stack', icon: '⚙️', count: Object.keys(context.tech_stack || {}).length },
    { id: 'architecture' as const, label: 'Architecture', icon: '🏗️', count: Object.keys(context.architecture || {}).length },
    { id: 'issues' as const, label: 'Issues', icon: '⚠️', count: context.active_issues?.length || 0 },
    { id: 'decisions' as const, label: 'Decisions', icon: '💡', count: context.decisions?.length || 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-xl p-6 border border-primary-200 dark:border-primary-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-primary-900 dark:text-primary-100 mb-1">
              Shared Context
            </h3>
            <p className="text-sm text-primary-600 dark:text-primary-400">
              Last updated: {formatTime(context.timestamp)}
            </p>
          </div>
          <div className="text-4xl">📚</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2 border-b border-gray-200 dark:border-gray-700">
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setActiveTab(tab.id)}
            className={`
              px-4 py-3 font-medium transition-colors relative
              ${activeTab === tab.id
                ? 'text-primary-600 dark:text-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }
            `}
          >
            <div className="flex items-center space-x-2">
              <span className="text-xl">{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.count > 0 && (
                <span className={`
                  px-2 py-0.5 text-xs rounded-full
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
                layoutId="activeContextTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"
              />
            )}
          </motion.button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {/* Tech Stack */}
          {activeTab === 'tech' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(context.tech_stack || {}).map(([key, value]) => (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-md border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-2xl">⚙️</span>
                    <h4 className="font-semibold text-gray-900 dark:text-white capitalize">
                      {key.replace(/_/g, ' ')}
                    </h4>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-3">
                    <pre className="text-xs text-gray-900 dark:text-white overflow-auto">
                      {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                    </pre>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {/* Architecture */}
          {activeTab === 'architecture' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(context.architecture || {}).map(([key, value]) => (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-md border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-2xl">🏗️</span>
                    <h4 className="font-semibold text-gray-900 dark:text-white capitalize">
                      {key.replace(/_/g, ' ')}
                    </h4>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900/50 rounded p-3">
                    <pre className="text-xs text-gray-900 dark:text-white overflow-auto">
                      {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                    </pre>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {/* Issues */}
          {activeTab === 'issues' && (
            <div className="space-y-3">
              {context.active_issues && context.active_issues.length > 0 ? (
                context.active_issues.map((issue: Issue) => (
                  <motion.div
                    key={issue.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-md border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getIssueSeverityColor(issue.severity)}`}>
                            {issue.severity.toUpperCase()}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getIssueStatusColor(issue.status)}`}>
                            {issue.status.replace(/_/g, ' ').toUpperCase()}
                          </span>
                        </div>
                        <p className="text-gray-900 dark:text-white font-medium mb-2">
                          {issue.description}
                        </p>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Created by <span className="font-medium">{issue.created_by}</span> • {formatTime(issue.created_at)}
                        </div>
                        {issue.assigned_to && (
                          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            Assigned to <span className="font-medium">{issue.assigned_to}</span>
                          </div>
                        )}
                        {issue.resolution && (
                          <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-700">
                            <div className="text-xs font-medium text-green-700 dark:text-green-300 mb-1">
                              Resolution:
                            </div>
                            <p className="text-sm text-green-900 dark:text-green-100">
                              {issue.resolution}
                            </p>
                            {issue.resolved_at && (
                              <div className="text-xs text-green-600 dark:text-green-400 mt-1">
                                Resolved at {formatTime(issue.resolved_at)}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12">
                  <div className="text-4xl mb-2">✅</div>
                  <p className="text-gray-600 dark:text-gray-400">No active issues</p>
                </div>
              )}
            </div>
          )}

          {/* Decisions */}
          {activeTab === 'decisions' && (
            <div className="space-y-3">
              {context.decisions && context.decisions.length > 0 ? (
                context.decisions.map((decision: Decision) => (
                  <motion.div
                    key={decision.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-md border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-2xl">💡</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDecisionImpactColor(decision.impact)}`}>
                            {decision.impact.toUpperCase()} IMPACT
                          </span>
                        </div>
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                          {decision.description}
                        </h4>
                        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 mb-3">
                          <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                            Rationale:
                          </div>
                          <p className="text-sm text-gray-900 dark:text-white">
                            {decision.rationale}
                          </p>
                        </div>
                        {decision.alternatives && decision.alternatives.length > 0 && (
                          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-700">
                            <div className="text-xs font-medium text-blue-700 dark:text-blue-300 mb-2">
                              Alternatives Considered:
                            </div>
                            <ul className="space-y-1">
                              {decision.alternatives.map((alt, idx) => (
                                <li key={idx} className="text-sm text-blue-900 dark:text-blue-100 flex items-start">
                                  <span className="text-blue-500 mr-2">•</span>
                                  {alt}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-3">
                          Made by <span className="font-medium">{decision.made_by}</span> • {formatTime(decision.timestamp)}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12">
                  <div className="text-4xl mb-2">🤔</div>
                  <p className="text-gray-600 dark:text-gray-400">No decisions recorded yet</p>
                </div>
              )}
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};
