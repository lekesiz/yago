"""
YAGO v8.4 - API Request/Response Logging Middleware
Comprehensive logging for API requests and responses
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from datetime import datetime
import logging
import time
import json

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for logging requests and responses

    Features:
    - Log all incoming requests
    - Log response status and timing
    - Track slow requests
    - Exclude sensitive paths from detailed logging
    - Log request/response bodies (configurable)
    """

    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False,
        slow_request_threshold: float = 1.0,  # seconds
        exclude_paths: Optional[list] = None,
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.slow_request_threshold = slow_request_threshold
        self.exclude_paths = exclude_paths or [
            "/health",  # Exclude health checks
            "/docs",  # Exclude API docs
            "/openapi.json",  # Exclude OpenAPI spec
            "/favicon.ico",  # Exclude favicon
        ]

    def _should_log(self, path: str) -> bool:
        """Determine if request should be logged in detail"""
        for excluded in self.exclude_paths:
            if path.startswith(excluded):
                return False
        return True

    def _mask_sensitive_data(self, data: dict) -> dict:
        """Mask sensitive fields in request/response data"""
        sensitive_fields = [
            "password",
            "token",
            "secret",
            "api_key",
            "access_token",
            "refresh_token",
            "authorization",
        ]

        masked_data = data.copy()

        for key in list(masked_data.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                masked_data[key] = "***MASKED***"

        return masked_data

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return "unknown"

    async def dispatch(self, request: Request, call_next):
        """Process and log request/response"""
        # Generate request ID
        request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")

        # Get client info
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "unknown")

        # Start timing
        start_time = time.time()

        # Check if we should log this request
        should_log = self._should_log(request.url.path)

        # Log incoming request
        if should_log:
            request_log = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
            }

            # Log request body if enabled (for POST/PUT)
            if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        body_dict = json.loads(body.decode())
                        request_log["body"] = self._mask_sensitive_data(body_dict)
                except Exception as e:
                    request_log["body_parse_error"] = str(e)

            logger.info(f"Incoming request: {json.dumps(request_log)}")

        # Process request
        try:
            response = await call_next(request)

            # Calculate response time
            response_time = time.time() - start_time
            response_time_ms = round(response_time * 1000, 2)

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{response_time_ms}ms"

            # Log response
            if should_log:
                response_log = {
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "response_time_ms": response_time_ms,
                    "client_ip": client_ip,
                }

                # Log slow requests
                if response_time > self.slow_request_threshold:
                    logger.warning(
                        f"SLOW REQUEST: {request.method} {request.url.path} "
                        f"took {response_time_ms}ms (threshold: {self.slow_request_threshold * 1000}ms)"
                    )
                    response_log["slow_request"] = True

                # Determine log level based on status code
                if 200 <= response.status_code < 300:
                    log_level = logging.INFO
                elif 400 <= response.status_code < 500:
                    log_level = logging.WARNING
                else:
                    log_level = logging.ERROR

                logger.log(log_level, f"Response: {json.dumps(response_log)}")

            return response

        except Exception as e:
            # Calculate response time even for errors
            response_time = time.time() - start_time
            response_time_ms = round(response_time * 1000, 2)

            # Log error
            error_log = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "error_type": type(e).__name__,
                "response_time_ms": response_time_ms,
                "client_ip": client_ip,
            }

            logger.error(f"Request error: {json.dumps(error_log)}")

            # Re-raise the exception
            raise


class APIMetricsMiddleware(BaseHTTPMiddleware):
    """
    Track API metrics for monitoring

    Tracks:
    - Request count by endpoint
    - Response time statistics
    - Status code distribution
    - Error rates
    """

    def __init__(self, app):
        super().__init__(app)
        self.metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "endpoints": {},  # endpoint -> stats
        }

    async def dispatch(self, request: Request, call_next):
        """Track request metrics"""
        start_time = time.time()

        # Increment total requests
        self.metrics["total_requests"] += 1

        # Get or create endpoint metrics
        endpoint = f"{request.method} {request.url.path}"
        if endpoint not in self.metrics["endpoints"]:
            self.metrics["endpoints"][endpoint] = {
                "count": 0,
                "errors": 0,
                "total_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0,
                "status_codes": {},
            }

        endpoint_metrics = self.metrics["endpoints"][endpoint]

        try:
            response = await call_next(request)

            # Calculate response time
            response_time = time.time() - start_time

            # Update metrics
            endpoint_metrics["count"] += 1
            endpoint_metrics["total_time"] += response_time
            endpoint_metrics["min_time"] = min(endpoint_metrics["min_time"], response_time)
            endpoint_metrics["max_time"] = max(endpoint_metrics["max_time"], response_time)

            # Track status codes
            status_code = str(response.status_code)
            endpoint_metrics["status_codes"][status_code] = (
                endpoint_metrics["status_codes"].get(status_code, 0) + 1
            )

            # Track errors (4xx and 5xx)
            if response.status_code >= 400:
                endpoint_metrics["errors"] += 1
                self.metrics["total_errors"] += 1

            return response

        except Exception as e:
            # Track error
            endpoint_metrics["errors"] += 1
            self.metrics["total_errors"] += 1
            raise

    def get_metrics(self) -> dict:
        """Get current metrics"""
        # Calculate average response times
        metrics_copy = {
            "total_requests": self.metrics["total_requests"],
            "total_errors": self.metrics["total_errors"],
            "error_rate": (
                round((self.metrics["total_errors"] / self.metrics["total_requests"]) * 100, 2)
                if self.metrics["total_requests"] > 0
                else 0
            ),
            "endpoints": {},
        }

        for endpoint, stats in self.metrics["endpoints"].items():
            metrics_copy["endpoints"][endpoint] = {
                "count": stats["count"],
                "errors": stats["errors"],
                "error_rate": (
                    round((stats["errors"] / stats["count"]) * 100, 2)
                    if stats["count"] > 0
                    else 0
                ),
                "avg_response_time_ms": (
                    round((stats["total_time"] / stats["count"]) * 1000, 2)
                    if stats["count"] > 0
                    else 0
                ),
                "min_response_time_ms": (
                    round(stats["min_time"] * 1000, 2)
                    if stats["min_time"] != float("inf")
                    else 0
                ),
                "max_response_time_ms": round(stats["max_time"] * 1000, 2),
                "status_codes": stats["status_codes"],
            }

        return metrics_copy

    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "endpoints": {},
        }
