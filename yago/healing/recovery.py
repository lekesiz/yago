"""
YAGO v8.0 - Recovery Engine
Orchestrates automatic error recovery
"""

import asyncio
import logging
from typing import Dict, Optional, Callable, Any, List
from datetime import datetime

from .base import (
    ErrorContext,
    RecoveryAction,
    RecoveryResult,
    ErrorSeverity,
    ErrorCategory,
    RetryConfig,
    CircuitBreakerConfig,
)
from .detector import ErrorDetector
from .monitor import HealthMonitor
from .strategies import (
    RecoveryStrategy,
    RetryStrategy,
    CircuitBreakerStrategy,
    FallbackStrategy,
    RollbackStrategy,
)

logger = logging.getLogger(__name__)


class RecoveryEngine:
    """
    Automatic error recovery orchestration engine
    """

    def __init__(
        self,
        health_monitor: Optional[HealthMonitor] = None,
        error_detector: Optional[ErrorDetector] = None
    ):
        self.health_monitor = health_monitor or HealthMonitor()
        self.error_detector = error_detector or ErrorDetector()

        # Recovery strategies
        self.retry_strategy = RetryStrategy()
        self.circuit_breakers: Dict[str, CircuitBreakerStrategy] = {}
        self.fallback_operations: Dict[str, List[Callable]] = {}
        self.rollback_strategy = RollbackStrategy()

        # Recovery history
        self.recovery_history: List[RecoveryResult] = []
        self.max_history = 100

    def register_circuit_breaker(
        self,
        component: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """Register circuit breaker for a component"""
        self.circuit_breakers[component] = CircuitBreakerStrategy(config)
        logger.info(f"Registered circuit breaker for: {component}")

    def register_fallback(
        self,
        component: str,
        fallback_operations: List[Callable]
    ):
        """Register fallback operations for a component"""
        self.fallback_operations[component] = fallback_operations
        logger.info(
            f"Registered {len(fallback_operations)} fallback operations "
            f"for: {component}"
        )

    async def execute_with_recovery(
        self,
        operation: Callable,
        component: str,
        operation_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation with automatic recovery

        Args:
            operation: Operation to execute
            component: Component name
            operation_name: Operation name
            *args: Operation arguments
            **kwargs: Operation keyword arguments

        Returns:
            Operation result

        Raises:
            Exception if recovery fails
        """
        start_time = datetime.utcnow()

        try:
            # Execute with circuit breaker if registered
            if component in self.circuit_breakers:
                result = await self._execute_with_circuit_breaker(
                    operation,
                    component,
                    operation_name,
                    *args,
                    **kwargs
                )
            else:
                # Execute normally
                if asyncio.iscoroutinefunction(operation):
                    result = await operation(*args, **kwargs)
                else:
                    result = operation(*args, **kwargs)

            # Record success
            response_time = (
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
            self.health_monitor.record_success(component, response_time)

            return result

        except Exception as e:
            # Detect and classify error
            error_context = self.error_detector.detect(
                e,
                component,
                operation_name,
                **kwargs
            )

            # Record failure
            self.health_monitor.record_failure(component, error_context)

            # Attempt recovery
            recovery_result = await self._attempt_recovery(
                operation,
                error_context,
                *args,
                **kwargs
            )

            # Store recovery result
            self._store_recovery(recovery_result)

            if recovery_result.success:
                logger.info(
                    f"Successfully recovered from error: {error_context.error_id}"
                )
                return recovery_result.metadata.get('result')
            else:
                logger.error(
                    f"Failed to recover from error: {error_context.error_id}"
                )
                raise e

    async def _attempt_recovery(
        self,
        operation: Callable,
        error_context: ErrorContext,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """
        Attempt to recover from an error

        Args:
            operation: Original operation
            error_context: Error context
            *args: Operation arguments
            **kwargs: Operation keyword arguments

        Returns:
            Recovery result
        """
        component = error_context.component

        # Determine recovery action
        action = self._determine_recovery_action(error_context)

        logger.info(
            f"Attempting recovery for {error_context.error_id} "
            f"using action: {action.value}"
        )

        try:
            if action == RecoveryAction.RETRY_WITH_BACKOFF:
                return await self._retry_with_backoff(
                    operation,
                    error_context,
                    *args,
                    **kwargs
                )

            elif action == RecoveryAction.FALLBACK:
                return await self._try_fallback(
                    operation,
                    error_context,
                    *args,
                    **kwargs
                )

            elif action == RecoveryAction.ROLLBACK:
                return await self._rollback(
                    operation,
                    error_context,
                    *args,
                    **kwargs
                )

            elif action == RecoveryAction.CIRCUIT_BREAK:
                # Circuit breaker already handled
                return RecoveryResult(
                    success=False,
                    action=action,
                    error_context=error_context,
                    attempts=0,
                    duration_ms=0,
                    message="Circuit breaker opened"
                )

            elif action == RecoveryAction.IGNORE:
                return RecoveryResult(
                    success=False,
                    action=action,
                    error_context=error_context,
                    attempts=0,
                    duration_ms=0,
                    message="Error ignored based on severity"
                )

            else:
                return RecoveryResult(
                    success=False,
                    action=action,
                    error_context=error_context,
                    attempts=0,
                    duration_ms=0,
                    message=f"No recovery strategy for action: {action.value}"
                )

        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            return RecoveryResult(
                success=False,
                action=action,
                error_context=error_context,
                attempts=1,
                duration_ms=0,
                message=f"Recovery failed: {str(e)}"
            )

    def _determine_recovery_action(
        self,
        error_context: ErrorContext
    ) -> RecoveryAction:
        """Determine appropriate recovery action"""
        component = error_context.component

        # Check if circuit breaker should open
        if self.error_detector.should_circuit_break(error_context):
            return RecoveryAction.CIRCUIT_BREAK

        # Check if fallback available and should be used
        if (component in self.fallback_operations and
                self.error_detector.should_fallback(error_context)):
            return RecoveryAction.FALLBACK

        # Check if should retry
        if self.error_detector.should_retry(error_context):
            return RecoveryAction.RETRY_WITH_BACKOFF

        # Check if should rollback
        if error_context.severity >= ErrorSeverity.HIGH:
            return RecoveryAction.ROLLBACK

        # Default: ignore low severity errors
        if error_context.severity == ErrorSeverity.LOW:
            return RecoveryAction.IGNORE

        # Escalate critical errors
        if error_context.severity == ErrorSeverity.CRITICAL:
            return RecoveryAction.ESCALATE

        return RecoveryAction.ALERT

    async def _retry_with_backoff(
        self,
        operation: Callable,
        error_context: ErrorContext,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Retry operation with backoff"""
        return await self.retry_strategy.execute(
            operation,
            error_context,
            *args,
            **kwargs
        )

    async def _execute_with_circuit_breaker(
        self,
        operation: Callable,
        component: str,
        operation_name: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation through circuit breaker"""
        circuit_breaker = self.circuit_breakers[component]

        # Create minimal error context for circuit breaker
        error_context = ErrorContext(
            error_id="cb_check",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.UNKNOWN,
            error_type="CircuitBreakerCheck",
            error_message="Circuit breaker check",
            component=component,
            operation=operation_name
        )

        result = await circuit_breaker.execute(
            operation,
            error_context,
            *args,
            **kwargs
        )

        if result.success:
            return result.metadata.get('result')
        else:
            raise Exception(result.message)

    async def _try_fallback(
        self,
        operation: Callable,
        error_context: ErrorContext,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Try fallback operations"""
        component = error_context.component

        if component not in self.fallback_operations:
            return RecoveryResult(
                success=False,
                action=RecoveryAction.FALLBACK,
                error_context=error_context,
                attempts=0,
                duration_ms=0,
                message="No fallback operations registered"
            )

        fallback_strategy = FallbackStrategy(
            self.fallback_operations[component]
        )

        return await fallback_strategy.execute(
            operation,
            error_context,
            *args,
            **kwargs
        )

    async def _rollback(
        self,
        operation: Callable,
        error_context: ErrorContext,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Rollback to previous state"""
        return await self.rollback_strategy.execute(
            operation,
            error_context,
            *args,
            **kwargs
        )

    def _store_recovery(self, result: RecoveryResult):
        """Store recovery result in history"""
        self.recovery_history.append(result)

        # Keep history size limited
        if len(self.recovery_history) > self.max_history:
            self.recovery_history.pop(0)

    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        if not self.recovery_history:
            return {
                "total_recoveries": 0,
                "success_rate": 0.0,
                "by_action": {},
                "by_component": {}
            }

        total = len(self.recovery_history)
        successful = sum(1 for r in self.recovery_history if r.success)

        # Group by action
        by_action = {}
        for result in self.recovery_history:
            action = result.action.value
            if action not in by_action:
                by_action[action] = {"total": 0, "successful": 0}

            by_action[action]["total"] += 1
            if result.success:
                by_action[action]["successful"] += 1

        # Group by component
        by_component = {}
        for result in self.recovery_history:
            component = result.error_context.component
            if component not in by_component:
                by_component[component] = {"total": 0, "successful": 0}

            by_component[component]["total"] += 1
            if result.success:
                by_component[component]["successful"] += 1

        # Calculate average duration
        avg_duration = (
            sum(r.duration_ms for r in self.recovery_history) / total
        )

        return {
            "total_recoveries": total,
            "successful_recoveries": successful,
            "failed_recoveries": total - successful,
            "success_rate": successful / total,
            "avg_duration_ms": avg_duration,
            "by_action": by_action,
            "by_component": by_component
        }

    def get_circuit_breaker_status(self) -> Dict[str, Dict]:
        """Get status of all circuit breakers"""
        return {
            component: breaker.get_state()
            for component, breaker in self.circuit_breakers.items()
        }

    def reset_circuit_breaker(self, component: str):
        """Reset a circuit breaker"""
        if component in self.circuit_breakers:
            self.circuit_breakers[component].reset()
            logger.info(f"Reset circuit breaker for: {component}")

    def get_recent_recoveries(
        self,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent recovery attempts"""
        recent = self.recovery_history[-count:]

        return [
            {
                "error_id": r.error_context.error_id,
                "component": r.error_context.component,
                "operation": r.error_context.operation,
                "action": r.action.value,
                "success": r.success,
                "attempts": r.attempts,
                "duration_ms": r.duration_ms,
                "message": r.message,
                "timestamp": r.error_context.timestamp.isoformat()
            }
            for r in recent
        ]
