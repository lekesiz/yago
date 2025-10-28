"""
YAGO v8.0 - Error Detector
Intelligent error detection and classification
"""

import logging
import traceback
import uuid
from typing import Optional, Type
from datetime import datetime

from .base import (
    ErrorContext,
    ErrorSeverity,
    ErrorCategory,
)

logger = logging.getLogger(__name__)


class ErrorDetector:
    """
    Intelligent error detection and classification
    """

    def __init__(self):
        # Error patterns for classification
        self.category_patterns = {
            ErrorCategory.NETWORK: [
                "connection", "network", "socket", "dns", "host"
            ],
            ErrorCategory.API: [
                "api", "request", "response", "http", "status code"
            ],
            ErrorCategory.RATE_LIMIT: [
                "rate limit", "quota", "throttle", "too many requests"
            ],
            ErrorCategory.AUTHENTICATION: [
                "auth", "permission", "unauthorized", "forbidden", "token"
            ],
            ErrorCategory.RESOURCE: [
                "memory", "cpu", "disk", "resource", "capacity"
            ],
            ErrorCategory.DATABASE: [
                "database", "sql", "query", "connection pool"
            ],
            ErrorCategory.VALIDATION: [
                "validation", "invalid", "schema", "format"
            ],
            ErrorCategory.TIMEOUT: [
                "timeout", "timed out", "deadline"
            ],
            ErrorCategory.CONFIGURATION: [
                "config", "setting", "environment", "missing"
            ],
        }

        # Severity patterns
        self.severity_patterns = {
            ErrorSeverity.CRITICAL: [
                "critical", "fatal", "crash", "panic", "emergency"
            ],
            ErrorSeverity.HIGH: [
                "error", "failed", "failure", "exception"
            ],
            ErrorSeverity.MEDIUM: [
                "warning", "warn", "issue"
            ],
            ErrorSeverity.LOW: [
                "info", "notice", "minor"
            ],
        }

    def detect(
        self,
        exception: Exception,
        component: str,
        operation: str,
        **metadata
    ) -> ErrorContext:
        """
        Detect and classify an error

        Args:
            exception: The exception that occurred
            component: Component where error occurred
            operation: Operation being performed
            **metadata: Additional metadata

        Returns:
            ErrorContext with classification
        """
        error_id = f"err_{uuid.uuid4().hex[:12]}"

        # Get error details
        error_type = type(exception).__name__
        error_message = str(exception)
        stack_trace = "".join(traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__
        ))

        # Classify error
        category = self._classify_category(exception, error_message)
        severity = self._classify_severity(
            exception,
            error_message,
            category
        )

        context = ErrorContext(
            error_id=error_id,
            timestamp=datetime.utcnow(),
            severity=severity,
            category=category,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            component=component,
            operation=operation,
            metadata=metadata
        )

        logger.info(
            f"Detected error: {error_id} "
            f"[{severity.value}/{category.value}] "
            f"in {component}.{operation}: {error_message}"
        )

        return context

    def _classify_category(
        self,
        exception: Exception,
        message: str
    ) -> ErrorCategory:
        """Classify error category"""
        message_lower = message.lower()
        error_type = type(exception).__name__.lower()

        # Check known exception types
        if "timeout" in error_type:
            return ErrorCategory.TIMEOUT
        elif "auth" in error_type or "permission" in error_type:
            return ErrorCategory.AUTHENTICATION
        elif "rate" in error_type or "limit" in error_type:
            return ErrorCategory.RATE_LIMIT
        elif "network" in error_type or "connection" in error_type:
            return ErrorCategory.NETWORK
        elif "validation" in error_type:
            return ErrorCategory.VALIDATION
        elif "database" in error_type or "sql" in error_type:
            return ErrorCategory.DATABASE

        # Check message patterns
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return category

        # Default
        return ErrorCategory.UNKNOWN

    def _classify_severity(
        self,
        exception: Exception,
        message: str,
        category: ErrorCategory
    ) -> ErrorSeverity:
        """Classify error severity"""
        message_lower = message.lower()

        # Critical categories
        if category in [ErrorCategory.RESOURCE, ErrorCategory.DATABASE]:
            return ErrorSeverity.HIGH

        # Check message patterns
        for severity, patterns in self.severity_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return severity

        # Check exception type
        error_type = type(exception).__name__.lower()
        if "critical" in error_type or "fatal" in error_type:
            return ErrorSeverity.CRITICAL

        # Default based on category
        if category == ErrorCategory.RATE_LIMIT:
            return ErrorSeverity.MEDIUM
        elif category == ErrorCategory.NETWORK:
            return ErrorSeverity.HIGH
        elif category == ErrorCategory.AUTHENTICATION:
            return ErrorSeverity.HIGH
        elif category == ErrorCategory.TIMEOUT:
            return ErrorSeverity.MEDIUM

        return ErrorSeverity.MEDIUM

    def should_retry(self, context: ErrorContext) -> bool:
        """
        Determine if error should be retried

        Args:
            context: Error context

        Returns:
            True if error should be retried
        """
        # Never retry critical errors
        if context.severity == ErrorSeverity.CRITICAL:
            return False

        # Retry transient errors
        retryable_categories = [
            ErrorCategory.NETWORK,
            ErrorCategory.TIMEOUT,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.API,
        ]

        if context.category in retryable_categories:
            return True

        # Don't retry validation or auth errors
        non_retryable = [
            ErrorCategory.VALIDATION,
            ErrorCategory.AUTHENTICATION,
            ErrorCategory.CONFIGURATION,
        ]

        if context.category in non_retryable:
            return False

        # Default: retry medium severity
        return context.severity == ErrorSeverity.MEDIUM

    def should_fallback(self, context: ErrorContext) -> bool:
        """
        Determine if fallback should be used

        Args:
            context: Error context

        Returns:
            True if fallback should be used
        """
        # Use fallback for high severity errors
        if context.severity >= ErrorSeverity.HIGH:
            return True

        # Use fallback after multiple retries
        if context.retry_count >= 2:
            return True

        # Use fallback for specific categories
        fallback_categories = [
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.RESOURCE,
        ]

        return context.category in fallback_categories

    def should_circuit_break(self, context: ErrorContext) -> bool:
        """
        Determine if circuit breaker should open

        Args:
            context: Error context

        Returns:
            True if circuit should break
        """
        # Circuit break on critical errors
        if context.severity == ErrorSeverity.CRITICAL:
            return True

        # Circuit break on repeated auth failures
        if (context.category == ErrorCategory.AUTHENTICATION and
                context.retry_count >= 3):
            return True

        # Circuit break on resource exhaustion
        if context.category == ErrorCategory.RESOURCE:
            return True

        return False

    def get_retry_delay(
        self,
        context: ErrorContext,
        base_delay_ms: float = 1000.0
    ) -> float:
        """
        Calculate retry delay based on error context

        Args:
            context: Error context
            base_delay_ms: Base delay in milliseconds

        Returns:
            Delay in milliseconds
        """
        # Exponential backoff
        delay = base_delay_ms * (2 ** context.retry_count)

        # Category-specific adjustments
        if context.category == ErrorCategory.RATE_LIMIT:
            # Longer delay for rate limits
            delay *= 5
        elif context.category == ErrorCategory.NETWORK:
            # Moderate delay for network errors
            delay *= 2

        # Cap maximum delay at 60 seconds
        return min(delay, 60000.0)

    def create_context_from_error(
        self,
        error: Exception,
        component: str = "unknown",
        operation: str = "unknown",
        **metadata
    ) -> ErrorContext:
        """
        Convenience method to create ErrorContext from an exception

        Args:
            error: Exception
            component: Component name
            operation: Operation name
            **metadata: Additional metadata

        Returns:
            ErrorContext
        """
        return self.detect(error, component, operation, **metadata)
