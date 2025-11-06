/**
 * YAGO v8.3 - Centralized Logger Service
 * Production-safe logging with error tracking integration
 */
import { config } from '../config/env';
import { logError as trackError } from './errorLogger';

/**
 * Log levels
 */
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

/**
 * Log metadata
 */
interface LogMetadata {
  [key: string]: any;
}

/**
 * Logger configuration
 */
interface LoggerConfig {
  enableConsole: boolean;
  enableRemote: boolean;
  minLevel: LogLevel;
  maxLogSize: number;
}

/**
 * Log entry
 */
interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  metadata?: LogMetadata;
  stack?: string;
}

/**
 * Logger service class
 */
class LoggerService {
  private config: LoggerConfig;
  private logBuffer: LogEntry[] = [];
  private maxBufferSize = 100;

  constructor() {
    this.config = {
      enableConsole: config.isDevelopment || config.enableDebugMode,
      enableRemote: config.isProduction && config.enableErrorReporting,
      minLevel: config.isDevelopment ? LogLevel.DEBUG : LogLevel.INFO,
      maxLogSize: 1000,
    };
  }

  /**
   * Log a debug message
   */
  debug(message: string, metadata?: LogMetadata): void {
    this.log(LogLevel.DEBUG, message, metadata);
  }

  /**
   * Log an info message
   */
  info(message: string, metadata?: LogMetadata): void {
    this.log(LogLevel.INFO, message, metadata);
  }

  /**
   * Log a warning
   */
  warn(message: string, metadata?: LogMetadata): void {
    this.log(LogLevel.WARN, message, metadata);
  }

  /**
   * Log an error
   */
  error(message: string, error?: Error | unknown, metadata?: LogMetadata): void {
    const errorObj = error instanceof Error ? error : new Error(String(error));

    this.log(LogLevel.ERROR, message, {
      ...metadata,
      error: {
        name: errorObj.name,
        message: errorObj.message,
        stack: errorObj.stack,
      },
    });

    // Send to error tracking service
    if (this.config.enableRemote) {
      trackError({
        error: errorObj,
        context: { message, ...metadata },
        severity: 'error',
      });
    }
  }

  /**
   * Internal log method
   */
  private log(level: LogLevel, message: string, metadata?: LogMetadata): void {
    // Check if level is enabled
    if (!this.shouldLog(level)) {
      return;
    }

    const entry: LogEntry = {
      level,
      message: this.truncateMessage(message),
      timestamp: new Date().toISOString(),
      metadata,
    };

    // Add to buffer
    this.addToBuffer(entry);

    // Console output
    if (this.config.enableConsole) {
      this.logToConsole(entry);
    }

    // Remote logging (only for errors and warnings in production)
    if (this.config.enableRemote && (level === LogLevel.ERROR || level === LogLevel.WARN)) {
      this.logToRemote(entry);
    }
  }

  /**
   * Check if log level should be logged
   */
  private shouldLog(level: LogLevel): boolean {
    const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
    const minIndex = levels.indexOf(this.config.minLevel);
    const levelIndex = levels.indexOf(level);
    return levelIndex >= minIndex;
  }

  /**
   * Truncate long messages
   */
  private truncateMessage(message: string): string {
    if (message.length <= this.config.maxLogSize) {
      return message;
    }
    return message.substring(0, this.config.maxLogSize) + '... (truncated)';
  }

  /**
   * Add entry to buffer
   */
  private addToBuffer(entry: LogEntry): void {
    this.logBuffer.push(entry);
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer.shift(); // Remove oldest
    }
  }

  /**
   * Log to console with colors
   */
  private logToConsole(entry: LogEntry): void {
    const { level, message, metadata } = entry;

    const styles: Record<LogLevel, string> = {
      [LogLevel.DEBUG]: 'color: #888',
      [LogLevel.INFO]: 'color: #0066cc',
      [LogLevel.WARN]: 'color: #ff9900',
      [LogLevel.ERROR]: 'color: #ff0000',
    };

    const prefix = `[${entry.timestamp}] [${level.toUpperCase()}]`;
    const style = styles[level];

    if (metadata && Object.keys(metadata).length > 0) {
      console.log(`%c${prefix} ${message}`, style, metadata);
    } else {
      console.log(`%c${prefix} ${message}`, style);
    }
  }

  /**
   * Send log to remote service
   */
  private async logToRemote(entry: LogEntry): Promise<void> {
    try {
      // Here you would send to your logging service
      // For now, we'll just use the error tracking service for errors
      if (entry.level === LogLevel.ERROR && entry.metadata?.error) {
        // Already sent via trackError in error() method
        return;
      }

      // You could integrate with services like:
      // - Sentry
      // - LogRocket
      // - DataDog
      // - Custom logging endpoint
    } catch (err) {
      // Silent fail - don't log errors about logging
      console.error('Failed to send log to remote:', err);
    }
  }

  /**
   * Get recent logs from buffer
   */
  getRecentLogs(count: number = 50): LogEntry[] {
    return this.logBuffer.slice(-count);
  }

  /**
   * Clear log buffer
   */
  clearBuffer(): void {
    this.logBuffer = [];
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<LoggerConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }
}

// Singleton instance
const loggerInstance = new LoggerService();

/**
 * Convenience functions
 */
export const logger = {
  debug: (message: string, metadata?: LogMetadata) => loggerInstance.debug(message, metadata),
  info: (message: string, metadata?: LogMetadata) => loggerInstance.info(message, metadata),
  warn: (message: string, metadata?: LogMetadata) => loggerInstance.warn(message, metadata),
  error: (message: string, error?: Error | unknown, metadata?: LogMetadata) =>
    loggerInstance.error(message, error, metadata),
  getRecentLogs: (count?: number) => loggerInstance.getRecentLogs(count),
  clearBuffer: () => loggerInstance.clearBuffer(),
  updateConfig: (config: Partial<LoggerConfig>) => loggerInstance.updateConfig(config),
};

/**
 * Performance logging
 */
export class PerformanceLogger {
  private startTime: number;
  private label: string;

  constructor(label: string) {
    this.label = label;
    this.startTime = performance.now();
    logger.debug(`⏱️ ${label} started`);
  }

  end(metadata?: LogMetadata): void {
    const duration = performance.now() - this.startTime;
    logger.info(`⏱️ ${this.label} completed`, {
      duration: `${duration.toFixed(2)}ms`,
      ...metadata,
    });
  }
}

/**
 * Create a performance logger
 */
export function measurePerformance(label: string): PerformanceLogger {
  return new PerformanceLogger(label);
}

/**
 * Log API request/response
 */
export function logApiCall(
  method: string,
  url: string,
  status: number,
  duration: number,
  error?: Error
): void {
  if (error) {
    logger.error(`API ${method} ${url} failed`, error, {
      status,
      duration: `${duration}ms`,
    });
  } else if (status >= 400) {
    logger.warn(`API ${method} ${url} returned ${status}`, {
      status,
      duration: `${duration}ms`,
    });
  } else {
    logger.debug(`API ${method} ${url} succeeded`, {
      status,
      duration: `${duration}ms`,
    });
  }
}

export default logger;
