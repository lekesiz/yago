/**
 * YAGO v8.3 - Error Logging Service
 * Centralized error logging to backend
 */

import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

// Get or create session ID
const getSessionId = (): string => {
  let sessionId = sessionStorage.getItem('yago_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    sessionStorage.setItem('yago_session_id', sessionId);
  }
  return sessionId;
};

// Parse stack trace to extract file and line info
const parseStackTrace = (stack?: string): { file_path?: string; line_number?: number } => {
  if (!stack) return {};

  // Try to find first line with file:line:col format
  const match = stack.match(/(?:https?:)?\/\/[^:]+:(\d+):(\d+)/);
  if (match) {
    return {
      file_path: stack.split('\n')[1]?.trim() || undefined,
      line_number: parseInt(match[1], 10)
    };
  }

  return {};
};

// Extract component name from stack trace
const extractComponentName = (stack?: string): string | undefined => {
  if (!stack) return undefined;

  // Try to find React component name
  const componentMatch = stack.match(/at (\w+) \(/);
  if (componentMatch) {
    return componentMatch[1];
  }

  return undefined;
};

export interface ErrorContext {
  component?: string;
  action?: string;
  userId?: string;
  projectId?: string;
  [key: string]: any;
}

export interface LogErrorOptions {
  error: Error;
  context?: ErrorContext;
  severity?: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  source?: 'frontend' | 'backend';
}

/**
 * Log an error to the backend
 */
export const logError = async (options: LogErrorOptions): Promise<void> => {
  const { error, context = {}, severity = 'error', source = 'frontend' } = options;

  try {
    const { file_path, line_number } = parseStackTrace(error.stack);
    const component = context.component || extractComponentName(error.stack);

    const payload = {
      error_type: error.name || 'Error',
      error_message: error.message,
      stack_trace: error.stack,
      source,
      component,
      file_path,
      line_number,
      session_id: getSessionId(),
      user_agent: navigator.userAgent,
      url: window.location.href,
      environment: import.meta.env.MODE,
      metadata: context,
      severity
    };

    // Don't await - fire and forget to avoid blocking UI
    axios.post(`${API_BASE}/errors/log`, payload).catch(err => {
      console.error('Failed to log error to backend:', err);
    });
  } catch (e) {
    // Silently fail - we don't want error logging to cause more errors
    console.error('Error logger failed:', e);
  }
};

/**
 * Log a custom message (not an error)
 */
export const logMessage = async (
  message: string,
  severity: 'debug' | 'info' | 'warning' = 'info',
  context?: ErrorContext
): Promise<void> => {
  const fakeError = new Error(message);
  fakeError.name = 'LogMessage';

  await logError({
    error: fakeError,
    context,
    severity,
    source: 'frontend'
  });
};

/**
 * Log API errors
 */
export const logApiError = async (
  error: any,
  endpoint: string,
  method: string = 'GET'
): Promise<void> => {
  const err = new Error(error.response?.data?.detail || error.message || 'API Error');
  err.name = 'ApiError';

  await logError({
    error: err,
    context: {
      endpoint,
      method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      responseData: error.response?.data
    },
    severity: 'error'
  });
};

/**
 * Setup global error handlers
 */
export const setupGlobalErrorHandlers = (): void => {
  // Handle unhandled errors
  window.onerror = (message, source, lineno, colno, error) => {
    const err = error || new Error(String(message));
    logError({
      error: err,
      context: {
        source: source,
        line: lineno,
        column: colno
      },
      severity: 'error'
    });

    return false; // Let default handler run too
  };

  // Handle unhandled promise rejections
  window.onunhandledrejection = (event) => {
    const err = event.reason instanceof Error
      ? event.reason
      : new Error(String(event.reason));
    err.name = 'UnhandledPromiseRejection';

    logError({
      error: err,
      context: {
        type: 'unhandled_promise_rejection',
        reason: event.reason
      },
      severity: 'error'
    });
  };

  console.log('✅ Global error handlers initialized');
};
