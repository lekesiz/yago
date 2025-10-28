"""
YAGO v8.0 - Auto-Healing System
Automatic error recovery and self-diagnosis
"""

from .base import (
    ErrorSeverity,
    ErrorCategory,
    HealthStatus,
    ErrorContext,
    RecoveryAction,
    RecoveryResult,
)
from .monitor import HealthMonitor
from .detector import ErrorDetector
from .recovery import RecoveryEngine
from .strategies import (
    RetryStrategy,
    CircuitBreakerStrategy,
    RollbackStrategy,
    FallbackStrategy,
)

__all__ = [
    # Base
    'ErrorSeverity',
    'ErrorCategory',
    'HealthStatus',
    'ErrorContext',
    'RecoveryAction',
    'RecoveryResult',

    # Core Components
    'HealthMonitor',
    'ErrorDetector',
    'RecoveryEngine',

    # Strategies
    'RetryStrategy',
    'CircuitBreakerStrategy',
    'RollbackStrategy',
    'FallbackStrategy',
]
