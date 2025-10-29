"""
Rate Limiting Middleware for FastAPI
Protects API from abuse and DoS attacks
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import asyncio


class RateLimitInfo:
    """Track rate limit info for a client"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: list = []

    def is_allowed(self) -> Tuple[bool, Dict]:
        """Check if request is allowed"""
        now = time.time()
        window_start = now - self.window_seconds

        # Remove old requests outside window
        self.requests = [req_time for req_time in self.requests if req_time > window_start]

        # Check if under limit
        allowed = len(self.requests) < self.max_requests

        # Add current request
        if allowed:
            self.requests.append(now)

        # Calculate rate limit headers
        remaining = max(0, self.max_requests - len(self.requests))
        reset_time = int(window_start + self.window_seconds)

        return allowed, {
            "limit": self.max_requests,
            "remaining": remaining,
            "reset": reset_time,
            "used": len(self.requests),
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm

    Features:
    - Per-IP rate limiting
    - Configurable limits per endpoint
    - Rate limit headers in response
    - Automatic cleanup of old entries
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 100,
        window_seconds: int = 60,
        exclude_paths: list = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]

        # Storage for rate limit info per IP
        self.clients: Dict[str, RateLimitInfo] = {}
        self.lock = asyncio.Lock()

        # Start cleanup task
        asyncio.create_task(self._cleanup_task())

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""

        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limit
        async with self.lock:
            if client_ip not in self.clients:
                self.clients[client_ip] = RateLimitInfo(
                    self.requests_per_minute,
                    self.window_seconds
                )

            allowed, rate_info = self.clients[client_ip].is_allowed()

        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(rate_info["limit"]),
            "X-RateLimit-Remaining": str(rate_info["remaining"]),
            "X-RateLimit-Reset": str(rate_info["reset"]),
            "X-RateLimit-Used": str(rate_info["used"]),
        }

        # If rate limit exceeded, return 429
        if not allowed:
            retry_after = rate_info["reset"] - int(time.time())
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                    "limit": rate_info["limit"],
                    "window": f"{self.window_seconds}s",
                },
                headers={
                    **headers,
                    "Retry-After": str(retry_after),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address, considering proxies

        Priority:
        1. X-Forwarded-For (if behind proxy)
        2. X-Real-IP (if behind nginx)
        3. client.host (direct connection)
        """
        # Check for proxy headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take first IP (original client)
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        # Direct connection
        if request.client:
            return request.client.host

        return "unknown"

    async def _cleanup_task(self):
        """Background task to cleanup old rate limit entries"""
        while True:
            await asyncio.sleep(300)  # Run every 5 minutes

            async with self.lock:
                now = time.time()
                to_delete = []

                for ip, info in self.clients.items():
                    # Remove entries with no recent requests
                    window_start = now - info.window_seconds - 300  # Add 5 min buffer
                    info.requests = [req_time for req_time in info.requests if req_time > window_start]

                    # Mark for deletion if no recent requests
                    if not info.requests:
                        to_delete.append(ip)

                # Delete old entries
                for ip in to_delete:
                    del self.clients[ip]

                if to_delete:
                    print(f"[RateLimit] Cleaned up {len(to_delete)} inactive clients")

    def get_stats(self) -> Dict:
        """Get rate limiting statistics"""
        return {
            "tracked_clients": len(self.clients),
            "requests_per_minute": self.requests_per_minute,
            "window_seconds": self.window_seconds,
        }


# Advanced rate limiter with different limits per endpoint
class AdaptiveRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Advanced rate limiter with per-endpoint limits

    Example usage:
        limits = {
            "/api/v1/analytics": (10, 60),  # 10 requests per minute
            "/api/v1/projects": (50, 60),   # 50 requests per minute
            "default": (100, 60),            # Default: 100 requests per minute
        }
        app.add_middleware(AdaptiveRateLimitMiddleware, limits=limits)
    """

    def __init__(self, app, limits: Dict[str, Tuple[int, int]] = None):
        super().__init__(app)
        self.limits = limits or {"default": (100, 60)}
        self.clients: Dict[str, Dict[str, RateLimitInfo]] = defaultdict(dict)
        self.lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        """Process request with adaptive rate limiting"""

        # Get client IP and path
        client_ip = self._get_client_ip(request)
        path = request.url.path

        # Find matching limit
        max_requests, window_seconds = self._get_limit_for_path(path)

        # Check rate limit
        async with self.lock:
            if path not in self.clients[client_ip]:
                self.clients[client_ip][path] = RateLimitInfo(max_requests, window_seconds)

            allowed, rate_info = self.clients[client_ip][path].is_allowed()

        # Add headers
        headers = {
            "X-RateLimit-Limit": str(rate_info["limit"]),
            "X-RateLimit-Remaining": str(rate_info["remaining"]),
            "X-RateLimit-Reset": str(rate_info["reset"]),
        }

        if not allowed:
            retry_after = rate_info["reset"] - int(time.time())
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests to {path}",
                    "retry_after": retry_after,
                },
                headers={**headers, "Retry-After": str(retry_after)},
            )

        response = await call_next(request)

        for key, value in headers.items():
            response.headers[key] = value

        return response

    def _get_limit_for_path(self, path: str) -> Tuple[int, int]:
        """Get rate limit for specific path"""
        # Check exact match
        if path in self.limits:
            return self.limits[path]

        # Check prefix match
        for pattern, limit in self.limits.items():
            if path.startswith(pattern):
                return limit

        # Return default
        return self.limits.get("default", (100, 60))

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        if request.client:
            return request.client.host

        return "unknown"
