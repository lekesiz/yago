"""
YAGO v8.3 - Rate Limiting Middleware
Protects API endpoints from abuse with configurable rate limits
"""
import time
from typing import Dict, Optional, Callable
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import re


class RateLimiter:
    """
    Token bucket rate limiter

    Supports:
    - Per-IP rate limiting
    - Per-user rate limiting
    - Per-endpoint rate limiting
    - Configurable windows and limits
    """

    def __init__(self):
        # Store: key -> (count, window_start)
        self.requests: Dict[str, tuple[int, float]] = {}
        self.blocked_until: Dict[str, float] = {}

    def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
        block_duration: Optional[int] = None
    ) -> tuple[bool, Optional[Dict[str, any]]]:
        """
        Check if request is allowed

        Args:
            key: Unique identifier (IP, user_id, etc.)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            block_duration: How long to block after limit exceeded (optional)

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = time.time()

        # Check if blocked
        if key in self.blocked_until:
            if now < self.blocked_until[key]:
                retry_after = int(self.blocked_until[key] - now)
                return False, {
                    "blocked": True,
                    "retry_after": retry_after,
                    "limit": max_requests,
                    "window": window_seconds
                }
            else:
                # Unblock
                del self.blocked_until[key]

        # Get or initialize request count
        if key not in self.requests:
            self.requests[key] = (1, now)
            return True, {
                "remaining": max_requests - 1,
                "limit": max_requests,
                "reset": int(now + window_seconds)
            }

        count, window_start = self.requests[key]

        # Check if window expired
        if now - window_start > window_seconds:
            # Reset window
            self.requests[key] = (1, now)
            return True, {
                "remaining": max_requests - 1,
                "limit": max_requests,
                "reset": int(now + window_seconds)
            }

        # Increment count
        count += 1
        self.requests[key] = (count, window_start)

        # Check if limit exceeded
        if count > max_requests:
            # Block if configured
            if block_duration:
                self.blocked_until[key] = now + block_duration

            return False, {
                "blocked": block_duration is not None,
                "retry_after": block_duration or int(window_start + window_seconds - now),
                "limit": max_requests,
                "window": window_seconds
            }

        return True, {
            "remaining": max_requests - count,
            "limit": max_requests,
            "reset": int(window_start + window_seconds)
        }

    def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """Clean up old entries to prevent memory leak"""
        now = time.time()

        # Clean up requests
        keys_to_remove = [
            key for key, (_, window_start) in self.requests.items()
            if now - window_start > max_age_seconds
        ]
        for key in keys_to_remove:
            del self.requests[key]

        # Clean up blocks
        blocks_to_remove = [
            key for key, blocked_until in self.blocked_until.items()
            if now > blocked_until
        ]
        for key in blocks_to_remove:
            del self.blocked_until[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting

    Configuration:
    - Global rate limit (all endpoints)
    - Per-endpoint rate limits
    - Exempted paths (health checks, static files, etc.)
    """

    def __init__(
        self,
        app,
        global_limit: int = 100,
        global_window: int = 60,
        endpoint_limits: Optional[Dict[str, tuple[int, int]]] = None,
        exempt_paths: Optional[list[str]] = None,
        block_duration: Optional[int] = 300,  # 5 minutes
        enable_user_limits: bool = True
    ):
        super().__init__(app)
        self.limiter = RateLimiter()
        self.global_limit = global_limit
        self.global_window = global_window
        self.endpoint_limits = endpoint_limits or {}
        self.exempt_paths = exempt_paths or [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]
        self.block_duration = block_duration
        self.enable_user_limits = enable_user_limits

        # Cleanup task (run periodically)
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes

    def get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for client"""
        # Try to get user ID from JWT token
        if self.enable_user_limits and hasattr(request.state, 'user'):
            return f"user:{request.state.user.id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"

    def is_exempt(self, path: str) -> bool:
        """Check if path is exempt from rate limiting"""
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False

    def get_endpoint_limit(self, path: str) -> Optional[tuple[int, int]]:
        """Get specific rate limit for endpoint"""
        for pattern, (limit, window) in self.endpoint_limits.items():
            if re.match(pattern, path):
                return (limit, window)
        return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""
        path = request.url.path

        # Skip exempt paths
        if self.is_exempt(path):
            return await call_next(request)

        # Periodic cleanup
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            self.limiter.cleanup_old_entries()
            self.last_cleanup = now

        # Get client identifier
        client_id = self.get_client_identifier(request)

        # Get rate limit for this endpoint
        endpoint_limit = self.get_endpoint_limit(path)
        if endpoint_limit:
            max_requests, window = endpoint_limit
        else:
            max_requests, window = self.global_limit, self.global_window

        # Check rate limit
        is_allowed, info = self.limiter.is_allowed(
            key=f"{client_id}:{path}",
            max_requests=max_requests,
            window_seconds=window,
            block_duration=self.block_duration
        )

        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(info.get("limit", max_requests)),
            "X-RateLimit-Remaining": str(info.get("remaining", 0)),
            "X-RateLimit-Reset": str(info.get("reset", 0))
        }

        if not is_allowed:
            # Rate limit exceeded
            headers["Retry-After"] = str(info.get("retry_after", window))

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {info.get('retry_after', window)} seconds.",
                    "limit": info.get("limit"),
                    "retry_after": info.get("retry_after")
                },
                headers=headers
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response


# Predefined rate limit configurations

# Conservative (for production)
CONSERVATIVE_LIMITS = {
    r"^/api/v1/auth/.*": (10, 60),  # Auth endpoints: 10/min
    r"^/api/v1/projects$": (20, 60),  # Create project: 20/min
    r"^/api/v1/projects/.*/execute$": (5, 60),  # Execute: 5/min
    r"^/api/v1/clarifications$": (30, 60),  # Start session: 30/min
    r"^/api/v1/errors/log$": (100, 60),  # Error logging: 100/min (public)
}

# Standard (balanced)
STANDARD_LIMITS = {
    r"^/api/v1/auth/.*": (20, 60),
    r"^/api/v1/projects$": (40, 60),
    r"^/api/v1/projects/.*/execute$": (10, 60),
    r"^/api/v1/clarifications$": (60, 60),
    r"^/api/v1/errors/log$": (200, 60),
}

# Generous (for development)
GENEROUS_LIMITS = {
    r"^/api/v1/auth/.*": (50, 60),
    r"^/api/v1/projects$": (100, 60),
    r"^/api/v1/projects/.*/execute$": (20, 60),
    r"^/api/v1/clarifications$": (120, 60),
    r"^/api/v1/errors/log$": (500, 60),
}


def create_rate_limiter(
    env: str = "production",
    global_limit: Optional[int] = None,
    global_window: Optional[int] = None
) -> RateLimitMiddleware:
    """
    Create rate limiter middleware with environment-based defaults

    Args:
        env: Environment ("development", "staging", "production")
        global_limit: Override global limit
        global_window: Override global window
    """
    if env == "development":
        limits = GENEROUS_LIMITS
        default_global = 200
    elif env == "staging":
        limits = STANDARD_LIMITS
        default_global = 120
    else:  # production
        limits = CONSERVATIVE_LIMITS
        default_global = 100

    return RateLimitMiddleware(
        app=None,  # Will be set by FastAPI
        global_limit=global_limit or default_global,
        global_window=global_window or 60,
        endpoint_limits=limits,
        block_duration=300,  # 5 minutes
        enable_user_limits=True
    )
