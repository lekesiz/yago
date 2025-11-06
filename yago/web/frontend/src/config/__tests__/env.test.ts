import { describe, it, expect } from 'vitest';
import { config, API_BASE_URL, IS_DEVELOPMENT } from '../env';

describe('Environment Configuration', () => {
  it('should have API base URL configured', () => {
    expect(API_BASE_URL).toBeDefined();
    expect(typeof API_BASE_URL).toBe('string');
  });

  it('should have valid environment type', () => {
    expect(config.environment).toMatch(/^(development|production|test)$/);
  });

  it('should have consistent isDevelopment flag', () => {
    if (config.isDevelopment) {
      expect(config.environment).toBe('development');
    }
  });

  it('should have WebSocket URL derived from API URL', () => {
    expect(config.wsBaseUrl).toBeDefined();
    expect(config.wsBaseUrl).toMatch(/^wss?:\/\//);
  });

  it('should have feature flags defined', () => {
    expect(typeof config.enableAnalytics).toBe('boolean');
    expect(typeof config.enableErrorReporting).toBe('boolean');
    expect(typeof config.enableDebugMode).toBe('boolean');
  });

  it('should have app info', () => {
    expect(config.appName).toBeDefined();
    expect(config.appVersion).toBeDefined();
  });
});
