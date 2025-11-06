import { describe, it, expect, beforeEach, vi } from 'vitest';
import { logger, LogLevel } from '../logger';

describe('Logger Service', () => {
  beforeEach(() => {
    // Clear buffer before each test
    logger.clearBuffer();

    // Mock console methods
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('should log debug messages', () => {
    logger.debug('Test debug message');
    const logs = logger.getRecentLogs();

    expect(logs.length).toBeGreaterThan(0);
    expect(logs[logs.length - 1].level).toBe(LogLevel.DEBUG);
    expect(logs[logs.length - 1].message).toBe('Test debug message');
  });

  it('should log info messages', () => {
    logger.info('Test info message', { userId: '123' });
    const logs = logger.getRecentLogs();

    const lastLog = logs[logs.length - 1];
    expect(lastLog.level).toBe(LogLevel.INFO);
    expect(lastLog.message).toBe('Test info message');
    expect(lastLog.metadata).toEqual({ userId: '123' });
  });

  it('should log warnings', () => {
    logger.warn('Test warning');
    const logs = logger.getRecentLogs();

    expect(logs[logs.length - 1].level).toBe(LogLevel.WARN);
  });

  it('should log errors with Error objects', () => {
    const error = new Error('Test error');
    logger.error('Error occurred', error);

    const logs = logger.getRecentLogs();
    const lastLog = logs[logs.length - 1];

    expect(lastLog.level).toBe(LogLevel.ERROR);
    expect(lastLog.message).toBe('Error occurred');
    expect(lastLog.metadata?.error).toBeDefined();
  });

  it('should maintain log buffer with max size', () => {
    // Add more than buffer size
    for (let i = 0; i < 150; i++) {
      logger.info(`Message ${i}`);
    }

    const logs = logger.getRecentLogs();
    expect(logs.length).toBeLessThanOrEqual(100); // Max buffer size
  });

  it('should clear buffer', () => {
    logger.info('Test message');
    expect(logger.getRecentLogs().length).toBeGreaterThan(0);

    logger.clearBuffer();
    expect(logger.getRecentLogs().length).toBe(0);
  });

  it('should truncate long messages', () => {
    const longMessage = 'a'.repeat(2000);
    logger.info(longMessage);

    const logs = logger.getRecentLogs();
    const lastLog = logs[logs.length - 1];

    expect(lastLog.message.length).toBeLessThanOrEqual(1000);
  });
});
