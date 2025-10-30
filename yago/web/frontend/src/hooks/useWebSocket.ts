/**
 * YAGO v8.3 - WebSocket Hook
 * Real-time project updates via WebSocket
 */
import { useEffect, useRef, useState, useCallback } from 'react';

export interface WebSocketMessage {
  type: 'connection' | 'progress' | 'log' | 'error' | 'completion' | 'clarification' | 'file_created' | 'pong';
  project_id?: string;
  status?: string;
  progress?: number;
  message?: string;
  details?: any;
  log?: string;
  level?: string;
  error?: string;
  success?: boolean;
  files_generated?: number;
  lines_of_code?: number;
  cost?: number;
  timestamp?: string;
}

interface UseWebSocketOptions {
  projectId: string;
  onMessage?: (message: WebSocketMessage) => void;
  onProgress?: (progress: number, status: string, message: string) => void;
  onLog?: (log: string, level: string) => void;
  onError?: (error: string) => void;
  onCompletion?: (success: boolean, data: any) => void;
  autoConnect?: boolean;
}

export const useWebSocket = ({
  projectId,
  onMessage,
  onProgress,
  onLog,
  onError,
  onCompletion,
  autoConnect = true,
}: UseWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      const wsUrl = `ws://localhost:8000/ws/projects/${projectId}`;
      console.log(`Connecting to WebSocket: ${wsUrl}`);

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttemptsRef.current = 0;

        // Send ping every 30 seconds to keep connection alive
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);

        // Store interval reference for cleanup
        (ws as any).pingInterval = pingInterval;
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('WebSocket message:', message);

          setLastMessage(message);

          // Call general onMessage callback
          onMessage?.(message);

          // Call specific callbacks based on message type
          switch (message.type) {
            case 'progress':
              if (message.progress !== undefined && message.status && message.message) {
                onProgress?.(message.progress, message.status, message.message);
              }
              break;

            case 'log':
              if (message.log && message.level) {
                onLog?.(message.log, message.level);
              }
              break;

            case 'error':
              if (message.error) {
                onError?.(message.error);
              }
              break;

            case 'completion':
              onCompletion?.(message.success ?? false, {
                files_generated: message.files_generated,
                lines_of_code: message.lines_of_code,
                cost: message.cost,
              });
              break;

            case 'connection':
              console.log('Connection established:', message.status);
              break;

            case 'pong':
              // Received pong response
              break;

            default:
              console.log('Unknown message type:', message.type);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionError('WebSocket connection error');
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);

        // Clear ping interval
        if ((ws as any).pingInterval) {
          clearInterval((ws as any).pingInterval);
        }

        // Attempt to reconnect if not manually closed
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);

          console.log(
            `Reconnecting in ${delay / 1000}s (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setConnectionError('Failed to reconnect after multiple attempts');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnectionError('Failed to create WebSocket connection');
    }
  }, [projectId, onMessage, onProgress, onLog, onError, onCompletion]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      // Clear ping interval
      if ((wsRef.current as any).pingInterval) {
        clearInterval((wsRef.current as any).pingInterval);
      }

      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  }, []);

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    connectionError,
    connect,
    disconnect,
    sendMessage,
  };
};
