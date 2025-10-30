/**
 * YAGO v8.3 - Real-time Progress Component
 * Display live progress updates via WebSocket
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWebSocket } from '../hooks/useWebSocket';
import toast from 'react-hot-toast';

interface RealtimeProgressProps {
  projectId: string;
  projectName: string;
  onComplete?: (success: boolean, data: any) => void;
  onClose?: () => void;
}

interface LogEntry {
  id: string;
  timestamp: string;
  log: string;
  level: string;
}

export const RealtimeProgress: React.FC<RealtimeProgressProps> = ({
  projectId,
  projectName,
  onComplete,
  onClose,
}) => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('connecting');
  const [message, setMessage] = useState('Connecting to server...');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [hasError, setHasError] = useState(false);
  const [completionData, setCompletionData] = useState<any>(null);

  const { isConnected, connectionError } = useWebSocket({
    projectId,
    onProgress: (prog, stat, msg) => {
      setProgress(prog);
      setStatus(stat);
      setMessage(msg);
    },
    onLog: (log, level) => {
      setLogs((prev) => [
        ...prev,
        {
          id: `${Date.now()}-${Math.random()}`,
          timestamp: new Date().toISOString(),
          log,
          level,
        },
      ]);
    },
    onError: (error) => {
      setHasError(true);
      setMessage(`Error: ${error}`);
      toast.error(error);
    },
    onCompletion: (success, data) => {
      setCompletionData(data);
      if (success) {
        setProgress(100);
        setStatus('completed');
        setMessage('✅ Code generation completed!');
        toast.success('Project completed successfully!');
      } else {
        setHasError(true);
        setStatus('failed');
        setMessage('❌ Code generation failed');
        toast.error('Project failed');
      }
      onComplete?.(success, data);
    },
    autoConnect: true,
  });

  useEffect(() => {
    if (connectionError) {
      toast.error(`WebSocket error: ${connectionError}`);
    }
  }, [connectionError]);

  const getStatusColor = () => {
    if (hasError) return 'from-red-600 to-red-800';
    if (status === 'completed') return 'from-green-600 to-green-800';
    if (status === 'executing') return 'from-blue-600 to-blue-800';
    return 'from-gray-600 to-gray-800';
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-red-400';
      case 'warning':
        return 'text-yellow-400';
      case 'success':
        return 'text-green-400';
      default:
        return 'text-gray-300';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={status === 'completed' || hasError ? onClose : undefined}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-gray-900 rounded-lg w-full max-w-4xl max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className={`p-6 bg-gradient-to-r ${getStatusColor()} rounded-t-lg`}>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                {isConnected ? (
                  <>
                    <span className="animate-pulse">⚡</span>
                    <span>Live Progress</span>
                  </>
                ) : (
                  <>
                    <span>⏳</span>
                    <span>Connecting...</span>
                  </>
                )}
              </h2>
              <p className="text-white/80 mt-1">{projectName}</p>
            </div>
            {(status === 'completed' || hasError) && (
              <button
                onClick={onClose}
                className="text-white hover:text-gray-300 transition text-2xl"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4 border-b border-white/10">
          <div className="flex items-center justify-between mb-2">
            <span className="text-white font-medium">{message}</span>
            <span className="text-white font-bold">{progress}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className={`h-full bg-gradient-to-r ${getStatusColor()} relative`}
            >
              {status === 'executing' && (
                <motion.div
                  animate={{
                    x: ['0%', '100%'],
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                />
              )}
            </motion.div>
          </div>
        </div>

        {/* Logs */}
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="px-6 py-3 border-b border-white/10">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">
              Activity Log {logs.length > 0 && `(${logs.length})`}
            </h3>
          </div>
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2 font-mono text-sm">
            {logs.length > 0 ? (
              logs.map((log) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`${getLogLevelColor(log.level)}`}
                >
                  <span className="text-gray-500 mr-2">
                    [{new Date(log.timestamp).toLocaleTimeString()}]
                  </span>
                  {log.log}
                </motion.div>
              ))
            ) : (
              <div className="text-gray-500 text-center py-8">
                {isConnected ? 'Waiting for updates...' : 'Establishing connection...'}
              </div>
            )}
          </div>
        </div>

        {/* Completion Stats */}
        {completionData && status === 'completed' && (
          <div className="px-6 py-4 border-t border-white/10 bg-green-500/10">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-white">
                  {completionData.files_generated || 0}
                </div>
                <div className="text-sm text-gray-400">Files Generated</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">
                  {completionData.lines_of_code || 0}
                </div>
                <div className="text-sm text-gray-400">Lines of Code</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">
                  ${completionData.cost?.toFixed(2) || '0.00'}
                </div>
                <div className="text-sm text-gray-400">Cost</div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-4 border-t border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm">
            {isConnected ? (
              <>
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-green-400">Connected</span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                <span className="text-red-400">Disconnected</span>
              </>
            )}
          </div>
          {(status === 'completed' || hasError) && (
            <button
              onClick={onClose}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
            >
              Close
            </button>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};
