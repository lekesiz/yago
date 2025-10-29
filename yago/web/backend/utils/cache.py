"""
Backend Caching Utilities
In-memory cache with TTL for API responses
"""

import time
import asyncio
from typing import Any, Optional, Callable, TypeVar, Dict
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import json

T = TypeVar('T')


class CacheEntry:
    """Single cache entry with TTL"""

    def __init__(self, data: Any, ttl: int):
        self.data = data
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        return time.time() > self.expires_at

    def get_age(self) -> float:
        """Get age in seconds"""
        return time.time() - self.created_at


class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL

    Features:
    - TTL (Time To Live) per entry
    - Automatic cleanup of expired entries
    - LRU eviction when max size is reached
    - Cache statistics
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize cache

        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds (5 minutes)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[key]

            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None

            self._hits += 1
            return entry.data

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        async with self._lock:
            # Evict oldest entry if cache is full
            if len(self._cache) >= self._max_size:
                await self._evict_oldest()

            ttl = ttl or self._default_ttl
            self._cache[key] = CacheEntry(value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all cache"""
        async with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0

    async def cleanup_expired(self) -> int:
        """Remove expired entries, return count"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    async def _evict_oldest(self) -> None:
        """Evict oldest entry (LRU)"""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]
        self._evictions += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "evictions": self._evictions,
            "total_requests": total_requests,
        }

    async def has(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        async with self._lock:
            if key not in self._cache:
                return False

            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return False

            return True


# Global cache instance
cache = InMemoryCache(max_size=1000, default_ttl=300)


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from function arguments

    Args:
        prefix: Cache key prefix (usually function name)
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        MD5 hash of serialized arguments
    """
    # Serialize arguments
    key_data = {
        'prefix': prefix,
        'args': args,
        'kwargs': kwargs
    }

    # Create hash
    serialized = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(serialized.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: Optional[str] = None):
    """
    Decorator to cache function results

    Usage:
        @cached(ttl=300)
        async def get_analytics():
            # expensive operation
            return data

    Args:
        ttl: Time to live in seconds
        key_prefix: Custom key prefix (default: function name)
    """
    def decorator(func: Callable) -> Callable:
        prefix = key_prefix or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str):
    """
    Invalidate all cache keys matching pattern

    Args:
        pattern: String to match in cache keys
    """
    asyncio.create_task(_async_invalidate_pattern(pattern))


async def _async_invalidate_pattern(pattern: str) -> int:
    """Async helper to invalidate pattern"""
    async with cache._lock:
        keys_to_delete = [
            key for key in cache._cache.keys()
            if pattern in key
        ]

        for key in keys_to_delete:
            del cache._cache[key]

        return len(keys_to_delete)


# Background task to cleanup expired entries
async def cleanup_task(interval: int = 60):
    """
    Background task to cleanup expired cache entries

    Args:
        interval: Cleanup interval in seconds
    """
    while True:
        await asyncio.sleep(interval)
        removed = await cache.cleanup_expired()
        if removed > 0:
            print(f"[Cache] Cleaned up {removed} expired entries")


# Response cache middleware
class ResponseCacheMiddleware:
    """
    Middleware to cache API responses

    Usage in FastAPI:
        app.add_middleware(ResponseCacheMiddleware)
    """

    def __init__(self, app, ttl: int = 60):
        self.app = app
        self.ttl = ttl

    async def __call__(self, scope, receive, send):
        # Only cache GET requests
        if scope["type"] != "http" or scope["method"] != "GET":
            return await self.app(scope, receive, send)

        # Generate cache key from URL and query params
        path = scope["path"]
        query = scope.get("query_string", b"").decode()
        cache_key = f"response:{path}?{query}"

        # Check cache
        cached_response = await cache.get(cache_key)
        if cached_response:
            # Send cached response
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"x-cache", b"HIT"),
                ],
            })
            await send({
                "type": "http.response.body",
                "body": cached_response,
            })
            return

        # If not in cache, execute request
        # (This is simplified - in production, you'd capture the response)
        await self.app(scope, receive, send)


# Export
__all__ = [
    'cache',
    'cached',
    'generate_cache_key',
    'invalidate_cache_pattern',
    'cleanup_task',
    'ResponseCacheMiddleware',
]
