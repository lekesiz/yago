/**
 * YAGO v8.3 - Environment Configuration
 * Centralized configuration for all environment variables
 */

interface EnvironmentConfig {
  // API Configuration
  apiBaseUrl: string;
  apiTimeout: number;

  // WebSocket Configuration
  wsBaseUrl: string;

  // Environment
  isDevelopment: boolean;
  isProduction: boolean;
  environment: 'development' | 'production' | 'test';

  // Feature Flags
  enableAnalytics: boolean;
  enableErrorReporting: boolean;
  enableDebugMode: boolean;

  // App Info
  appName: string;
  appVersion: string;
}

/**
 * Get environment variable with fallback
 */
function getEnv(key: string, defaultValue: string = ''): string {
  return import.meta.env[key] || defaultValue;
}

/**
 * Get boolean environment variable
 */
function getBooleanEnv(key: string, defaultValue: boolean = false): boolean {
  const value = getEnv(key, String(defaultValue));
  return value === 'true' || value === '1';
}

/**
 * Get number environment variable
 */
function getNumberEnv(key: string, defaultValue: number = 0): number {
  const value = getEnv(key, String(defaultValue));
  return parseInt(value, 10) || defaultValue;
}

/**
 * Validate required environment variables
 */
function validateEnvironment(): void {
  const required: string[] = [
    // Add required env vars here if needed
  ];

  const missing = required.filter((key) => !import.meta.env[key]);

  if (missing.length > 0) {
    console.error('❌ Missing required environment variables:', missing);
    console.error('Please check your .env file');
  }
}

// Validate on load
validateEnvironment();

// Determine environment
const nodeEnv = getEnv('MODE', 'development');
const isDevelopment = nodeEnv === 'development';
const isProduction = nodeEnv === 'production';

// API Configuration
const apiBaseUrl = getEnv('VITE_API_BASE_URL', 'http://localhost:8000');
const wsProtocol = apiBaseUrl.startsWith('https') ? 'wss' : 'ws';
const wsHost = apiBaseUrl.replace(/^https?:\/\//, '');
const wsBaseUrl = `${wsProtocol}://${wsHost}`;

/**
 * Environment configuration object
 */
export const config: EnvironmentConfig = {
  // API
  apiBaseUrl,
  apiTimeout: getNumberEnv('VITE_API_TIMEOUT', 30000),

  // WebSocket
  wsBaseUrl,

  // Environment
  isDevelopment,
  isProduction,
  environment: isProduction ? 'production' : isDevelopment ? 'development' : 'test',

  // Feature Flags
  enableAnalytics: getBooleanEnv('VITE_ENABLE_ANALYTICS', isProduction),
  enableErrorReporting: getBooleanEnv('VITE_ENABLE_ERROR_REPORTING', true),
  enableDebugMode: getBooleanEnv('VITE_ENABLE_DEBUG', isDevelopment),

  // App Info
  appName: getEnv('VITE_APP_NAME', 'YAGO'),
  appVersion: getEnv('VITE_APP_VERSION', '8.3.1'),
};

// Log configuration in development
if (config.isDevelopment && config.enableDebugMode) {
  console.log('🔧 Environment Configuration:', {
    environment: config.environment,
    apiBaseUrl: config.apiBaseUrl,
    wsBaseUrl: config.wsBaseUrl,
    appVersion: config.appVersion,
  });
}

// Export individual values for convenience
export const {
  apiBaseUrl: API_BASE_URL,
  wsBaseUrl: WS_BASE_URL,
  isDevelopment: IS_DEVELOPMENT,
  isProduction: IS_PRODUCTION,
  environment: ENVIRONMENT,
  enableDebugMode: DEBUG_MODE,
} = config;

export default config;
