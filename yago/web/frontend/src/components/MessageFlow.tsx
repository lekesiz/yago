/**
 * YAGO v8.0 - Message Flow Component
 * Visualization of inter-agent message communication
 */

import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { collaborationApi } from '../services/collaborationApi';
import type { AgentMessage } from '../types/collaboration';
import { MessageType, MessagePriority, AgentType } from '../types/collaboration';

interface MessageFlowProps {
  projectId: string;
}

export const MessageFlow: React.FC<MessageFlowProps> = ({ projectId }) => {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<AgentType | 'all'>('all');
  const [selectedType, setSelectedType] = useState<MessageType | 'all'>('all');
  const [expandedMessageId, setExpandedMessageId] = useState<string | null>(null);

  // Load messages
  useEffect(() => {
    const loadMessages = async () => {
      try {
        setLoading(true);
        const data = await collaborationApi.getMessages(projectId);
        setMessages(data.messages);
      } catch (error: any) {
        console.error('Failed to load messages:', error);
        toast.error('Failed to load messages');
      } finally {
        setLoading(false);
      }
    };

    loadMessages();
    const interval = setInterval(loadMessages, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, [projectId]);

  // Get message type icon
  const getMessageTypeIcon = (type: MessageType): string => {
    const icons: Record<MessageType, string> = {
      [MessageType.CODE_READY]: '💻',
      [MessageType.TEST_RESULTS]: '🧪',
      [MessageType.REVIEW_NEEDED]: '👀',
      [MessageType.ISSUE_FOUND]: '⚠️',
      [MessageType.FIX_REQUESTED]: '🔧',
      [MessageType.DOCUMENTATION_READY]: '📝',
      [MessageType.CLARIFICATION_NEEDED]: '❓',
      [MessageType.TASK_COMPLETED]: '✅',
      [MessageType.TASK_FAILED]: '❌',
      [MessageType.CONFLICT_DETECTED]: '⚔️',
    };
    return icons[type] || '📬';
  };

  // Get priority color
  const getPriorityColor = (priority: MessagePriority): string => {
    const colors: Record<MessagePriority, string> = {
      [MessagePriority.LOW]: 'from-gray-400 to-gray-500',
      [MessagePriority.MEDIUM]: 'from-blue-400 to-blue-600',
      [MessagePriority.HIGH]: 'from-orange-400 to-orange-600',
      [MessagePriority.CRITICAL]: 'from-red-400 to-red-600',
    };
    return colors[priority];
  };

  const getPriorityBadgeColor = (priority: MessagePriority): string => {
    const colors: Record<MessagePriority, string> = {
      [MessagePriority.LOW]: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
      [MessagePriority.MEDIUM]: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
      [MessagePriority.HIGH]: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
      [MessagePriority.CRITICAL]: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
    };
    return colors[priority];
  };

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
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  // Filter messages
  const filteredMessages = useMemo(() => {
    return messages.filter((msg) => {
      const agentMatch = selectedAgent === 'all' ||
        msg.from_agent === selectedAgent ||
        msg.to_agent === selectedAgent;
      const typeMatch = selectedType === 'all' || msg.message_type === selectedType;
      return agentMatch && typeMatch;
    });
  }, [messages, selectedAgent, selectedType]);

  // Get unique agents
  const uniqueAgents = useMemo(() => {
    const agents = new Set<AgentType>();
    messages.forEach((msg) => {
      agents.add(msg.from_agent);
      if (msg.to_agent) agents.add(msg.to_agent);
    });
    return Array.from(agents);
  }, [messages]);

  // Handle message acknowledgement
  const handleAcknowledge = async (messageId: string) => {
    try {
      await collaborationApi.acknowledgeMessage(messageId);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, acknowledged: true, ack_timestamp: new Date().toISOString() } : msg
        )
      );
      toast.success('Message acknowledged');
    } catch (error) {
      toast.error('Failed to acknowledge message');
    }
  };

  if (loading && messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading messages...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        {/* Agent Filter */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Filter by Agent
          </label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value as AgentType | 'all')}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Agents</option>
            {uniqueAgents.map((agent) => (
              <option key={agent} value={agent}>
                {getAgentIcon(agent)} {agent}
              </option>
            ))}
          </select>
        </div>

        {/* Type Filter */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Filter by Type
          </label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value as MessageType | 'all')}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Types</option>
            {Object.values(MessageType).map((type) => (
              <option key={type} value={type}>
                {getMessageTypeIcon(type)} {type.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
          <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">Total Messages</div>
          <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
            {filteredMessages.length}
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-4 border border-green-200 dark:border-green-700">
          <div className="text-xs text-green-600 dark:text-green-400 mb-1">Acknowledged</div>
          <div className="text-2xl font-bold text-green-900 dark:text-green-100">
            {filteredMessages.filter(m => m.acknowledged).length}
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
          <div className="text-xs text-purple-600 dark:text-purple-400 mb-1">Broadcasts</div>
          <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
            {filteredMessages.filter(m => m.to_agent === null).length}
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg p-4 border border-orange-200 dark:border-orange-700">
          <div className="text-xs text-orange-600 dark:text-orange-400 mb-1">High Priority</div>
          <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">
            {filteredMessages.filter(m => m.priority === MessagePriority.HIGH || m.priority === MessagePriority.CRITICAL).length}
          </div>
        </div>
      </div>

      {/* Messages List */}
      {filteredMessages.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No Messages
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Messages will appear here when agents start communicating.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {filteredMessages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.02 }}
                className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-md border border-gray-200 dark:border-gray-700"
              >
                {/* Message Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    {/* From Agent */}
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{getAgentIcon(message.from_agent)}</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {message.from_agent}
                      </span>
                    </div>

                    {/* Arrow */}
                    <span className="text-gray-400">→</span>

                    {/* To Agent */}
                    <div className="flex items-center space-x-2">
                      {message.to_agent ? (
                        <>
                          <span className="text-2xl">{getAgentIcon(message.to_agent)}</span>
                          <span className="text-sm font-medium text-gray-900 dark:text-white">
                            {message.to_agent}
                          </span>
                        </>
                      ) : (
                        <span className="text-sm font-medium text-purple-600 dark:text-purple-400">
                          📢 Broadcast
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Badges */}
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityBadgeColor(message.priority)}`}>
                      {message.priority}
                    </span>
                    {message.acknowledged && (
                      <span className="text-green-500 text-lg">✓</span>
                    )}
                  </div>
                </div>

                {/* Message Type and Time */}
                <div className="flex items-center space-x-3 mb-3">
                  <span className="text-2xl">{getMessageTypeIcon(message.message_type)}</span>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {message.message_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {formatTime(message.timestamp)}
                  </span>
                </div>

                {/* Message Content */}
                <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 mb-3">
                  <p className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => setExpandedMessageId(
                      expandedMessageId === message.id ? null : message.id
                    )}
                    className="text-xs text-primary-600 dark:text-primary-400 hover:underline"
                  >
                    {expandedMessageId === message.id ? 'Hide' : 'Show'} Details
                  </button>

                  {message.requires_ack && !message.acknowledged && (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleAcknowledge(message.id)}
                      className="px-3 py-1 bg-green-500 text-white rounded-md text-xs hover:bg-green-600"
                    >
                      Acknowledge
                    </motion.button>
                  )}
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                  {expandedMessageId === message.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700"
                    >
                      <div className="space-y-2 text-xs">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Message ID:</span>
                          <span className="ml-2 text-gray-900 dark:text-white font-mono">{message.id}</span>
                        </div>
                        {message.response_to && (
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Response To:</span>
                            <span className="ml-2 text-gray-900 dark:text-white font-mono">{message.response_to}</span>
                          </div>
                        )}
                        {message.ack_timestamp && (
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Acknowledged At:</span>
                            <span className="ml-2 text-gray-900 dark:text-white">{formatTime(message.ack_timestamp)}</span>
                          </div>
                        )}
                        {message.metadata && Object.keys(message.metadata).length > 0 && (
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Metadata:</span>
                            <pre className="mt-1 p-2 bg-gray-100 dark:bg-gray-800 rounded text-xs overflow-auto">
                              {JSON.stringify(message.metadata, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};
