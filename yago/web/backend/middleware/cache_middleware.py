"""
YAGO v8.4 - API Response Caching Middleware
Simple in-memory caching for GET requests to improve performance
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheEntry:
    """Cache entry with expiration"""

    def __init__(self, response_body: bytes, status_code: int, headers: dict, ttl: int):
        self.response_body = response_body
        self.status_code = status_code
        self.headers = headers
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=ttl)

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.utcnow() > self.expires_at

    def get_age(self) -> int:
        """Get cache age in seconds"""
        return int((datetime.utcnow() - self.created_at).total_seconds())


class CacheMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for caching GET request responses

    Features:
    - Only caches GET requests
    - In-memory cache with configurable TTL
    - Automatic cache invalidation on expiry
    - Cache size limits
    - Exclude specific paths from caching
    """

    def __init__(
        self,
        app,
        default_ttl: int = 300,  # 5 minutes
        max_cache_size: int = 1000,  # Maximum number of cached entries
        exclude_paths: Optional[list] = None,
    ):
        super().__init__(app)
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self.max_cache_size = max_cache_size
        self.exclude_paths = exclude_paths or [
            "/ws/",  # WebSocket endpoints
            "/api/v1/auth/",  # Authentication endpoints
            "/api/v1/errors/log",  # Error logging
        ]

        # Path-specific TTL configuration
        self.path_ttl: Dict[str, int] = {
            "/api/v1/templates": 600,  # 10 minutes for templates
            "/api/v1/models": 1800,  # 30 minutes for models list
            "/api/v1/analytics": 60,  # 1 minute for analytics
            "/health": 30,  # 30 seconds for health checks
        }

    def _should_cache(self, request: Request) -> bool:
        """Determine if request should be cached"""
        # Only cache GET requests
        if request.method != "GET":
            return False

        # Check if path is excluded
        path = request.url.path
        for excluded in self.exclude_paths:
            if excluded in path:
                return False

        return True

    def _get_cache_key(self, request: Request) -> str:
        """Generate cache key from request"""
        # Include path and query parameters in cache key
        path = request.url.path
        query = str(request.url.query)

        # Create hash of path + query for compact key
        key_string = f"{path}?{query}" if query else path
        cache_key = hashlib.md5(key_string.encode()).hexdigest()

        return f"{path}:{cache_key}"

    def _get_ttl(self, path: str) -> int:
        """Get TTL for specific path"""
        # Check if path has specific TTL
        for path_prefix, ttl in self.path_ttl.items():
            if path.startswith(path_prefix):
                return ttl

        return self.default_ttl

    def _cleanup_expired(self):
        """Remove expired entries from cache"""
        expired_keys = [
            key for key, entry in self.cache.items() if entry.is_expired()
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _enforce_size_limit(self):
        """Enforce maximum cache size by removing oldest entries"""
        if len(self.cache) > self.max_cache_size:
            # Sort by creation time and remove oldest
            sorted_entries = sorted(
                self.cache.items(), key=lambda x: x[1].created_at
            )

            # Remove oldest 10%
            remove_count = len(self.cache) - self.max_cache_size
            for key, _ in sorted_entries[:remove_count]:
                del self.cache[key]

            logger.warning(
                f"Cache size limit reached. Removed {remove_count} oldest entries"
            )

    async def dispatch(self, request: Request, call_next):
        """Process request and handle caching"""
        # Check if we should cache this request
        if not self._should_cache(request):
            return await call_next(request)

        # Generate cache key
        cache_key = self._get_cache_key(request)

        # Check if response is in cache
        if cache_key in self.cache:
            entry = self.cache[cache_key]

            # Check if cache entry is still valid
            if not entry.is_expired():
                logger.debug(
                    f"Cache HIT: {request.url.path} (age: {entry.get_age()}s)"
                )

                # Create response from cache
                response = Response(
                    content=entry.response_body,
                    status_code=entry.status_code,
                    headers=entry.headers,
                )

                # Add cache headers
                response.headers["X-Cache"] = "HIT"
                response.headers["X-Cache-Age"] = str(entry.get_age())

                return response
            else:
                # Remove expired entry
                del self.cache[cache_key]
                logger.debug(f"Cache EXPIRED: {request.url.path}")

        # Cache miss - fetch response
        logger.debug(f"Cache MISS: {request.url.path}")

        response = await call_next(request)

        # Only cache successful responses (200-299)
        if 200 <= response.status_code < 300:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Get TTL for this path
            ttl = self._get_ttl(request.url.path)

            # Store in cache
            self.cache[cache_key] = CacheEntry(
                response_body=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                ttl=ttl,
            )

            # Periodic cache cleanup
            if len(self.cache) % 100 == 0:
                self._cleanup_expired()

            # Enforce size limit
            self._enforce_size_limit()

            # Create new response with cached body
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

            # Add cache headers
            response.headers["X-Cache"] = "MISS"

            logger.debug(
                f"Cached response for {request.url.path} (TTL: {ttl}s, "
                f"Cache size: {len(self.cache)})"
            )

        return response

    def clear_cache(self, path_prefix: Optional[str] = None):
        """Clear cache entries"""
        if path_prefix:
            # Clear specific path prefix
            keys_to_remove = [
                key for key in self.cache.keys() if key.startswith(path_prefix)
            ]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"Cleared cache for path prefix: {path_prefix}")
        else:
            # Clear all cache
            self.cache.clear()
            logger.info("Cleared entire cache")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())

        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "max_cache_size": self.max_cache_size,
            "utilization_percent": round((total_entries / self.max_cache_size) * 100, 2),
        }
