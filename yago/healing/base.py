"""
YAGO v8.0 - Auto-Healing Base Classes
Core abstractions for the auto-healing system
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"              # Minor issues, can be ignored
    MEDIUM = "medium"        # Needs attention but not critical
    HIGH = "high"            # Requires immediate action
    CRITICAL = "critical"    # System-threatening, urgent recovery


class ErrorCategory(str, Enum):
    """Error categories for classification"""
    NETWORK = "network"              # Network connectivity issues
    API = "api"                      # API call failures
    RATE_LIMIT = "rate_limit"        # Rate limiting errors
    AUTHENTICATION = "authentication" # Auth/permission errors
    RESOURCE = "resource"            # Resource exhaustion (memory, CPU)
    DATABASE = "database"            # Database errors
    VALIDATION = "validation"        # Data validation errors
    TIMEOUT = "timeout"              # Timeout errors
    CONFIGURATION = "configuration"  # Configuration errors
    UNKNOWN = "unknown"              # Unknown errors


class HealthStatus(str, Enum):
    """System health status"""
    HEALTHY = "healthy"          # All systems operational
    DEGRADED = "degraded"        # Some issues but operational
    UNHEALTHY = "unhealthy"      # Major issues, limited functionality
    CRITICAL = "critical"        # System failure, needs recovery


class ErrorContext(BaseModel):
    """
    Context information about an error
    """
    error_id: str = Field(description="Unique error identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: ErrorSeverity = Field(description="Error severity level")
    category: ErrorCategory = Field(description="Error category")

    # Error details
    error_type: str = Field(description="Error class name")
    error_message: str = Field(description="Error message")
    stack_trace: Optional[str] = None

    # Context
    component: str = Field(description="Component where error occurred")
    operation: str = Field(description="Operation being performed")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Recovery
    retry_count: int = Field(default=0)
    recovery_attempted: bool = Field(default=False)
    recovered: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "error_id": "err_abc123",
                "severity": "high",
                "category": "api",
                "error_type": "OpenAIError",
                "error_message": "Rate limit exceeded",
                "component": "model_adapter",
                "operation": "generate",
                "retry_count": 0
            }
        }


class RecoveryAction(str, Enum):
    """Available recovery actions"""
    RETRY = "retry"                      # Retry the operation
    RETRY_WITH_BACKOFF = "retry_backoff" # Retry with exponential backoff
    FALLBACK = "fallback"                # Switch to fallback option
    ROLLBACK = "rollback"                # Rollback to previous state
    CIRCUIT_BREAK = "circuit_break"      # Open circuit breaker
    RESTART = "restart"                  # Restart component
    ALERT = "alert"                      # Alert administrators
    IGNORE = "ignore"                    # Ignore and continue
    ESCALATE = "escalate"                # Escalate to higher level


class RecoveryResult(BaseModel):
    """
    Result of a recovery attempt
    """
    success: bool = Field(description="Whether recovery succeeded")
    action: RecoveryAction = Field(description="Action that was taken")
    error_context: ErrorContext = Field(description="Original error context")

    # Recovery details
    attempts: int = Field(default=1, description="Number of attempts made")
    duration_ms: float = Field(description="Recovery duration in milliseconds")
    resolved_at: Optional[datetime] = None

    # Additional info
    message: str = Field(description="Human-readable result message")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "action": "retry_backoff",
                "attempts": 3,
                "duration_ms": 5000,
                "message": "Successfully recovered after 3 retries with backoff"
            }
        }


class HealthCheckResult(BaseModel):
    """
    Result of a health check
    """
    component: str = Field(description="Component name")
    status: HealthStatus = Field(description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Metrics
    response_time_ms: Optional[float] = None
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0)

    # Details
    message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    issues: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "component": "openai_adapter",
                "status": "healthy",
                "response_time_ms": 250.5,
                "error_rate": 0.01,
                "success_rate": 0.99,
                "message": "All systems operational"
            }
        }


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit open, requests blocked
    HALF_OPEN = "half_open" # Testing if service recovered


class CircuitBreakerConfig(BaseModel):
    """
    Circuit breaker configuration
    """
    failure_threshold: int = Field(default=5, ge=1)
    success_threshold: int = Field(default=2, ge=1)
    timeout_seconds: float = Field(default=60.0, gt=0)
    half_open_max_calls: int = Field(default=1, ge=1)


class RetryConfig(BaseModel):
    """
    Retry strategy configuration
    """
    max_attempts: int = Field(default=3, ge=1, le=10)
    initial_delay_ms: float = Field(default=1000.0, gt=0)
    max_delay_ms: float = Field(default=60000.0, gt=0)
    exponential_base: float = Field(default=2.0, gt=1)
    jitter: bool = Field(default=True)
