/**
 * YAGO v8.0 - Conflict Resolver Component
 * Interface for detecting and resolving agent conflicts
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { collaborationApi } from '../services/collaborationApi';
import type { Conflict } from '../types/collaboration';
import { AgentType } from '../types/collaboration';

interface ConflictResolverProps {
  projectId: string;
}

export const ConflictResolver: React.FC<ConflictResolverProps> = ({ projectId }) => {
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [loading, setLoading] = useState(true);
  const [showResolved, setShowResolved] = useState(false);
  const [expandedConflictId, setExpandedConflictId] = useState<string | null>(null);
  const [resolvingConflictId, setResolvingConflictId] = useState<string | null>(null);
  const [resolutionText, setResolutionText] = useState('');
  const [resolutionReason, setResolutionReason] = useState('');

  // Load conflicts
  useEffect(() => {
    const loadConflicts = async () => {
      try {
        setLoading(true);
        const data = await collaborationApi.getConflicts(projectId, !showResolved);
        setConflicts(data.conflicts);
      } catch (error: any) {
        console.error('Failed to load conflicts:', error);
        toast.error('Failed to load conflicts');
      } finally {
        setLoading(false);
      }
    };

    loadConflicts();
    const interval = setInterval(loadConflicts, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, [projectId, showResolved]);

  // Get agent icon
  const getAgentIcon = (agent: AgentType): string => {
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
    return icons[agent] || '🤖';
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

  // Handle resolve conflict
  const handleResolveConflict = async (conflictId: string) => {
    if (!resolutionText.trim() || !resolutionReason.trim()) {
      toast.error('Please provide both resolution and reason');
      return;
    }

    try {
      await collaborationApi.resolveConflict(
        conflictId,
        { resolution: resolutionText },
        'User', // resolvedBy
        resolutionReason
      );

      setConflicts((prev) =>
        prev.map((conflict) =>
          conflict.id === conflictId
            ? {
                ...conflict,
                resolved: true,
                resolution: { resolution: resolutionText },
                resolved_by: 'User',
                resolution_reason: resolutionReason,
                resolved_at: new Date().toISOString(),
              }
            : conflict
        )
      );

      setResolvingConflictId(null);
      setResolutionText('');
      setResolutionReason('');
      toast.success('Conflict resolved successfully');
    } catch (error) {
      toast.error('Failed to resolve conflict');
    }
  };

  if (loading && conflicts.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading conflicts...</p>
        </div>
      </div>
    );
  }

  const unresolvedConflicts = conflicts.filter(c => !c.resolved);
  const resolvedConflicts = conflicts.filter(c => c.resolved);

  return (
    <div className="space-y-6">
      {/* Header with Toggle */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            Conflict Resolution
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {unresolvedConflicts.length} unresolved • {resolvedConflicts.length} resolved
          </p>
        </div>

        <button
          onClick={() => setShowResolved(!showResolved)}
          className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          {showResolved ? 'Hide Resolved' : 'Show Resolved'}
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 rounded-lg p-4 border border-red-200 dark:border-red-700">
          <div className="text-xs text-red-600 dark:text-red-400 mb-1">Unresolved</div>
          <div className="text-2xl font-bold text-red-900 dark:text-red-100">
            {unresolvedConflicts.length}
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-4 border border-green-200 dark:border-green-700">
          <div className="text-xs text-green-600 dark:text-green-400 mb-1">Resolved</div>
          <div className="text-2xl font-bold text-green-900 dark:text-green-100">
            {resolvedConflicts.length}
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
          <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">Resolution Rate</div>
          <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
            {conflicts.length > 0
              ? Math.round((resolvedConflicts.length / conflicts.length) * 100)
              : 0}%
          </div>
        </div>
      </div>

      {/* Conflicts List */}
      {conflicts.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">✅</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No Conflicts
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            All agents are working in harmony!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <AnimatePresence>
            {conflicts.map((conflict) => (
              <motion.div
                key={conflict.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border-2 ${
                  conflict.resolved
                    ? 'border-green-200 dark:border-green-700'
                    : 'border-red-200 dark:border-red-700'
                }`}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl">⚔️</span>
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Conflict Between Agents
                      </h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Detected at {formatTime(conflict.created_at)}
                      </p>
                    </div>
                  </div>

                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      conflict.resolved
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                        : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                    }`}
                  >
                    {conflict.resolved ? '✓ Resolved' : '⚠ Unresolved'}
                  </span>
                </div>

                {/* Agents Involved */}
                <div className="flex items-center space-x-4 mb-4">
                  <div className="flex items-center space-x-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg px-3 py-2">
                    <span className="text-2xl">{getAgentIcon(conflict.agent_a)}</span>
                    <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                      {conflict.agent_a}
                    </span>
                  </div>

                  <span className="text-2xl">🆚</span>

                  <div className="flex items-center space-x-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg px-3 py-2">
                    <span className="text-2xl">{getAgentIcon(conflict.agent_b)}</span>
                    <span className="text-sm font-medium text-purple-900 dark:text-purple-100">
                      {conflict.agent_b}
                    </span>
                  </div>
                </div>

                {/* Description */}
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 mb-4">
                  <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                    Description:
                  </div>
                  <p className="text-sm text-gray-900 dark:text-white">
                    {conflict.description}
                  </p>
                </div>

                {/* Proposals */}
                <button
                  onClick={() =>
                    setExpandedConflictId(
                      expandedConflictId === conflict.id ? null : conflict.id
                    )
                  }
                  className="text-sm text-primary-600 dark:text-primary-400 hover:underline mb-3"
                >
                  {expandedConflictId === conflict.id ? 'Hide' : 'Show'} Proposals
                </button>

                <AnimatePresence>
                  {expandedConflictId === conflict.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4"
                    >
                      {/* Agent A Proposal */}
                      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-xl">{getAgentIcon(conflict.agent_a)}</span>
                          <div className="text-sm font-medium text-blue-900 dark:text-blue-100">
                            {conflict.agent_a}'s Proposal
                          </div>
                        </div>
                        <pre className="text-xs text-blue-900 dark:text-blue-100 overflow-auto bg-white dark:bg-gray-800 rounded p-2">
                          {JSON.stringify(conflict.agent_a_proposal, null, 2)}
                        </pre>
                      </div>

                      {/* Agent B Proposal */}
                      <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-xl">{getAgentIcon(conflict.agent_b)}</span>
                          <div className="text-sm font-medium text-purple-900 dark:text-purple-100">
                            {conflict.agent_b}'s Proposal
                          </div>
                        </div>
                        <pre className="text-xs text-purple-900 dark:text-purple-100 overflow-auto bg-white dark:bg-gray-800 rounded p-2">
                          {JSON.stringify(conflict.agent_b_proposal, null, 2)}
                        </pre>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Resolution */}
                {conflict.resolved ? (
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-700">
                    <div className="text-sm font-medium text-green-700 dark:text-green-300 mb-2">
                      ✓ Resolved by {conflict.resolved_by} • {conflict.resolved_at && formatTime(conflict.resolved_at)}
                    </div>
                    <div className="space-y-2">
                      <div>
                        <div className="text-xs text-green-600 dark:text-green-400 mb-1">
                          Resolution:
                        </div>
                        <pre className="text-sm text-green-900 dark:text-green-100 bg-white dark:bg-gray-800 rounded p-2 overflow-auto">
                          {JSON.stringify(conflict.resolution, null, 2)}
                        </pre>
                      </div>
                      {conflict.resolution_reason && (
                        <div>
                          <div className="text-xs text-green-600 dark:text-green-400 mb-1">
                            Reason:
                          </div>
                          <p className="text-sm text-green-900 dark:text-green-100">
                            {conflict.resolution_reason}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <>
                    {resolvingConflictId === conflict.id ? (
                      <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-700 space-y-3">
                        <div className="text-sm font-medium text-yellow-700 dark:text-yellow-300">
                          Resolving Conflict
                        </div>

                        <div>
                          <label className="block text-xs text-yellow-600 dark:text-yellow-400 mb-1">
                            Resolution (JSON):
                          </label>
                          <textarea
                            value={resolutionText}
                            onChange={(e) => setResolutionText(e.target.value)}
                            placeholder='{"decision": "use proposal A", "modifications": {...}}'
                            className="w-full px-3 py-2 rounded-lg border border-yellow-300 dark:border-yellow-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm font-mono"
                            rows={4}
                          />
                        </div>

                        <div>
                          <label className="block text-xs text-yellow-600 dark:text-yellow-400 mb-1">
                            Reason:
                          </label>
                          <textarea
                            value={resolutionReason}
                            onChange={(e) => setResolutionReason(e.target.value)}
                            placeholder="Explain why this resolution was chosen..."
                            className="w-full px-3 py-2 rounded-lg border border-yellow-300 dark:border-yellow-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                            rows={3}
                          />
                        </div>

                        <div className="flex items-center space-x-2">
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => handleResolveConflict(conflict.id)}
                            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm"
                          >
                            Confirm Resolution
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                              setResolvingConflictId(null);
                              setResolutionText('');
                              setResolutionReason('');
                            }}
                            className="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-900 dark:text-white rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500 text-sm"
                          >
                            Cancel
                          </motion.button>
                        </div>
                      </div>
                    ) : (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setResolvingConflictId(conflict.id)}
                        className="w-full px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 text-sm font-medium"
                      >
                        Resolve Conflict
                      </motion.button>
                    )}
                  </>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};
