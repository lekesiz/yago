/**
 * API Response Caching Layer
 * In-memory cache with TTL and request deduplication
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

interface CacheOptions {
  ttl?: number; // Time to live in milliseconds (default: 5 minutes)
  key?: string; // Custom cache key
}

interface PendingRequest {
  promise: Promise<any>;
  timestamp: number;
}

/**
 * Simple in-memory cache with TTL
 */
class APICache {
  private cache: Map<string, CacheEntry<any>>;
  private pendingRequests: Map<string, PendingRequest>;
  private defaultTTL: number;
  private maxSize: number;

  constructor(defaultTTL: number = 5 * 60 * 1000, maxSize: number = 100) {
    this.cache = new Map();
    this.pendingRequests = new Map();
    this.defaultTTL = defaultTTL;
    this.maxSize = maxSize;

    // Clean up expired entries every minute
    if (typeof window !== 'undefined') {
      setInterval(() => this.cleanup(), 60000);
    }
  }

  /**
   * Get data from cache or execute fetcher function
   */
  async get<T>(
    key: string,
    fetcher: () => Promise<T>,
    options: CacheOptions = {}
  ): Promise<T> {
    const { ttl = this.defaultTTL } = options;

    // Check if data is in cache and not expired
    const cached = this.cache.get(key);
    if (cached && Date.now() < cached.expiresAt) {
      console.log(`[Cache] HIT: ${key}`);
      return cached.data as T;
    }

    // Check if there's a pending request for this key (request deduplication)
    const pending = this.pendingRequests.get(key);
    if (pending) {
      console.log(`[Cache] DEDUPE: ${key}`);
      return pending.promise;
    }

    // Execute fetcher and cache result
    console.log(`[Cache] MISS: ${key}`);
    const promise = fetcher()
      .then((data) => {
        this.set(key, data, ttl);
        this.pendingRequests.delete(key);
        return data;
      })
      .catch((error) => {
        this.pendingRequests.delete(key);
        throw error;
      });

    // Store pending request
    this.pendingRequests.set(key, {
      promise,
      timestamp: Date.now(),
    });

    return promise;
  }

  /**
   * Set data in cache
   */
  set<T>(key: string, data: T, ttl: number = this.defaultTTL): void {
    // Enforce max size by removing oldest entries
    if (this.cache.size >= this.maxSize) {
      const oldestKey = Array.from(this.cache.keys())[0];
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      expiresAt: Date.now() + ttl,
    });
  }

  /**
   * Invalidate specific cache key
   */
  invalidate(key: string): void {
    this.cache.delete(key);
    this.pendingRequests.delete(key);
    console.log(`[Cache] INVALIDATE: ${key}`);
  }

  /**
   * Invalidate all keys matching pattern
   */
  invalidatePattern(pattern: string | RegExp): void {
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern;

    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }

    for (const key of this.pendingRequests.keys()) {
      if (regex.test(key)) {
        this.pendingRequests.delete(key);
      }
    }

    console.log(`[Cache] INVALIDATE PATTERN: ${pattern}`);
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
    this.pendingRequests.clear();
    console.log('[Cache] CLEAR ALL');
  }

  /**
   * Clean up expired entries
   */
  private cleanup(): void {
    const now = Date.now();
    let removed = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (now >= entry.expiresAt) {
        this.cache.delete(key);
        removed++;
      }
    }

    // Clean up stale pending requests (older than 30 seconds)
    for (const [key, pending] of this.pendingRequests.entries()) {
      if (now - pending.timestamp > 30000) {
        this.pendingRequests.delete(key);
        removed++;
      }
    }

    if (removed > 0) {
      console.log(`[Cache] CLEANUP: Removed ${removed} expired entries`);
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      pendingRequests: this.pendingRequests.size,
      maxSize: this.maxSize,
      defaultTTL: this.defaultTTL,
    };
  }

  /**
   * Check if key exists and is valid
   */
  has(key: string): boolean {
    const cached = this.cache.get(key);
    return cached !== undefined && Date.now() < cached.expiresAt;
  }
}

// Global cache instance
export const apiCache = new APICache();

/**
 * Generate cache key from URL and params
 */
export const generateCacheKey = (
  url: string,
  params?: Record<string, any>
): string => {
  if (!params) return url;

  const sortedParams = Object.keys(params)
    .sort()
    .map((key) => `${key}=${JSON.stringify(params[key])}`)
    .join('&');

  return `${url}?${sortedParams}`;
};

/**
 * Cached fetch wrapper
 */
export const cachedFetch = async <T>(
  url: string,
  options: RequestInit & { cache?: CacheOptions } = {}
): Promise<T> => {
  const { cache: cacheOptions, ...fetchOptions } = options;
  const cacheKey = generateCacheKey(url, fetchOptions.body ? JSON.parse(fetchOptions.body as string) : undefined);

  return apiCache.get(
    cacheKey,
    async () => {
      const response = await fetch(url, fetchOptions);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    },
    cacheOptions
  );
};

/**
 * React hook for cached API calls
 */
export const useCachedAPI = <T>(
  key: string,
  fetcher: () => Promise<T>,
  options: CacheOptions = {}
) => {
  const [data, setData] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    let mounted = true;

    apiCache
      .get(key, fetcher, options)
      .then((result) => {
        if (mounted) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [key]);

  return { data, loading, error, invalidate: () => apiCache.invalidate(key) };
};

// Import React for the hook
import React from 'react';

export default apiCache;
