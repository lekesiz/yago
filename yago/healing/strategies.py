"""
YAGO v8.0 - Recovery Strategies
Implementation of various recovery strategies
"""

import asyncio
import logging
import random
from typing import Any, Callable, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from .base import (
    ErrorContext,
    RecoveryAction,
    RecoveryResult,
    RetryConfig,
    CircuitBreakerConfig,
    CircuitState,
)

logger = logging.getLogger(__name__)


class RecoveryStrategy(ABC):
    """Abstract base class for recovery strategies"""

    @abstractmethod
    async def execute(
        self,
        operation: Callable,
        error_context: ErrorContext,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """
        Execute recovery strategy

        Args:
            operation: Operation to recover
            error_context: Context of the error
            *args: Operation arguments
            **kwargs: Operation keyword arguments

        Returns:
            Recovery result
        """
        pass


class RetryStrategy(RecoveryStrategy):
    """
    Retry strategy with exponential backoff and jitter
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()

    async def execute(
        self,
        operation: Callable,
        error_context: ErrorContext,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Execute retry strategy"""
        start_time = datetime.utcnow()
        attempts = 0
        last_error = None

        while attempts < self.config.max_attempts:
            attempts += 1

            # Calculate delay
            if attempts > 1:
                delay_ms = self._calculate_delay(attempts - 1)
                logger.info(
                    f"Retrying {error_context.component}.{error_context.operation} "
                    f"(attempt {attempts}/{self.config.max_attempts}) "
                    f"after {delay_ms:.0f}ms"
                )
                await asyncio.sleep(delay_ms / 1000.0)

            try:
                # Execute operation
                if asyncio.iscoroutinefunction(operation):
                    result = await operation(*args, **kwargs)
                else:
                    result = operation(*args, **kwargs)

                # Success!
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000

                return RecoveryResult(
                    success=True,
                    action=RecoveryAction.RETRY_WITH_BACKOFF,
                    error_context=error_context,
                    attempts=attempts,
                    duration_ms=duration,
                    resolved_at=datetime.utcnow(),
                    message=f"Successfully recovered after {attempts} attempts",
                    metadata={"result": result}
                )

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Retry attempt {attempts} failed: {str(e)}"
                )

        # All retries failed
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        return RecoveryResult(
            success=False,
            action=RecoveryAction.RETRY_WITH_BACKOFF,
            error_context=error_context,
            attempts=attempts,
            duration_ms=duration,
            message=f"Failed after {attempts} retries: {str(last_error)}",
            metadata={"last_error": str(last_error)}
        )

    def _calculate_delay(self, retry_num: int) -> float:
        """Calculate delay with exponential backoff and jitter"""
        # Exponential backoff
        delay = (
            self.config.initial_delay_ms *
            (self.config.exponential_base ** retry_num)
        )

        # Add jitter if enabled
        if self.config.jitter:
            jitter = random.uniform(0, delay * 0.1)  # 10% jitter
            delay += jitter

        # Cap at max delay
        return min(delay, self.config.max_delay_ms)


class CircuitBreakerStrategy(RecoveryStrategy):
    """
    Circuit breaker pattern for preventing cascading failures
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0

    async def execute(
        self,
        operation: Callable,
        error_context: ErrorContext,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Execute with circuit breaker"""
        start_time = datetime.utcnow()

        # Check circuit state
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
                logger.info("Circuit breaker: OPEN -> HALF_OPEN")
            else:
                # Circuit is open, reject immediately
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000

                return RecoveryResult(
                    success=False,
                    action=RecoveryAction.CIRCUIT_BREAK,
                    error_context=error_context,
                    attempts=0,
                    duration_ms=duration,
                    message="Circuit breaker is OPEN, request rejected",
                    metadata={"circuit_state": self.state.value}
                )

        # Check half-open limit
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.config.half_open_max_calls:
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000

                return RecoveryResult(
                    success=False,
                    action=RecoveryAction.CIRCUIT_BREAK,
                    error_context=error_context,
                    attempts=0,
                    duration_ms=duration,
                    message="Circuit breaker HALF_OPEN limit reached",
                    metadata={"circuit_state": self.state.value}
                )

            self.half_open_calls += 1

        # Execute operation
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation(*args, **kwargs)
            else:
                result = operation(*args, **kwargs)

            # Success!
            self._record_success()
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            return RecoveryResult(
                success=True,
                action=RecoveryAction.CIRCUIT_BREAK,
                error_context=error_context,
                attempts=1,
                duration_ms=duration,
                resolved_at=datetime.utcnow(),
                message=f"Success (circuit: {self.state.value})",
                metadata={
                    "result": result,
                    "circuit_state": self.state.value
                }
            )

        except Exception as e:
            self._record_failure()
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            return RecoveryResult(
                success=False,
                action=RecoveryAction.CIRCUIT_BREAK,
                error_context=error_context,
                attempts=1,
                duration_ms=duration,
                message=f"Failed (circuit: {self.state.value}): {str(e)}",
                metadata={
                    "error": str(e),
                    "circuit_state": self.state.value
                }
            )

    def _record_success(self):
        """Record successful operation"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1

            # Check if we should close
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker: HALF_OPEN -> CLOSED")
        else:
            # Reset failure count on success in closed state
            self.failure_count = 0

    def _record_failure(self):
        """Record failed operation"""
        self.last_failure_time = datetime.utcnow()

        if self.state == CircuitState.HALF_OPEN:
            # Failure in half-open, reopen circuit
            self.state = CircuitState.OPEN
            self.failure_count = self.config.failure_threshold
            self.success_count = 0
            logger.warning("Circuit breaker: HALF_OPEN -> OPEN")
        else:
            self.failure_count += 1

            # Check if we should open
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self.success_count = 0
                logger.warning("Circuit breaker: CLOSED -> OPEN")

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset"""
        if not self.last_failure_time:
            return True

        timeout = timedelta(seconds=self.config.timeout_seconds)
        return datetime.utcnow() - self.last_failure_time >= timeout

    def reset(self):
        """Reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        logger.info("Circuit breaker reset to CLOSED")

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": (
                self.last_failure_time.isoformat()
                if self.last_failure_time else None
            )
        }


class FallbackStrategy(RecoveryStrategy):
    """
    Fallback strategy with alternative operations
    """

    def __init__(self, fallback_operations: list[Callable]):
        self.fallback_operations = fallback_operations

    async def execute(
        self,
        operation: Callable,
        error_context: ErrorContext,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Execute with fallback"""
        start_time = datetime.utcnow()
        attempts = 0
        last_error = None

        # Try primary operation
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation(*args, **kwargs)
            else:
                result = operation(*args, **kwargs)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            return RecoveryResult(
                success=True,
                action=RecoveryAction.FALLBACK,
                error_context=error_context,
                attempts=1,
                duration_ms=duration,
                resolved_at=datetime.utcnow(),
                message="Primary operation succeeded",
                metadata={"result": result, "used_fallback": False}
            )

        except Exception as e:
            last_error = e
            logger.warning(f"Primary operation failed: {str(e)}, trying fallback")

        # Try fallback operations
        for i, fallback_op in enumerate(self.fallback_operations):
            attempts += 1

            try:
                logger.info(f"Trying fallback operation {i+1}/{len(self.fallback_operations)}")

                if asyncio.iscoroutinefunction(fallback_op):
                    result = await fallback_op(*args, **kwargs)
                else:
                    result = fallback_op(*args, **kwargs)

                duration = (datetime.utcnow() - start_time).total_seconds() * 1000

                return RecoveryResult(
                    success=True,
                    action=RecoveryAction.FALLBACK,
                    error_context=error_context,
                    attempts=attempts + 1,
                    duration_ms=duration,
                    resolved_at=datetime.utcnow(),
                    message=f"Fallback operation {i+1} succeeded",
                    metadata={
                        "result": result,
                        "used_fallback": True,
                        "fallback_index": i
                    }
                )

            except Exception as e:
                last_error = e
                logger.warning(f"Fallback operation {i+1} failed: {str(e)}")

        # All fallbacks failed
        duration = (datetime.utcnow() - start_time).total_seconds() * 1000

        return RecoveryResult(
            success=False,
            action=RecoveryAction.FALLBACK,
            error_context=error_context,
            attempts=attempts + 1,
            duration_ms=duration,
            message=f"All fallback operations failed: {str(last_error)}",
            metadata={"last_error": str(last_error)}
        )


class RollbackStrategy(RecoveryStrategy):
    """
    Rollback strategy with state restoration
    """

    def __init__(self):
        self.state_history: list[Any] = []
        self.max_history = 10

    async def execute(
        self,
        operation: Callable,
        error_context: ErrorContext,
        *args,
        **kwargs
    ) -> RecoveryResult:
        """Execute with rollback capability"""
        start_time = datetime.utcnow()

        # Save current state if provided
        current_state = kwargs.get('state')
        if current_state:
            self._save_state(current_state)

        try:
            # Execute operation
            if asyncio.iscoroutinefunction(operation):
                result = await operation(*args, **kwargs)
            else:
                result = operation(*args, **kwargs)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            return RecoveryResult(
                success=True,
                action=RecoveryAction.ROLLBACK,
                error_context=error_context,
                attempts=1,
                duration_ms=duration,
                resolved_at=datetime.utcnow(),
                message="Operation succeeded, no rollback needed",
                metadata={"result": result}
            )

        except Exception as e:
            # Rollback to previous state
            previous_state = self._get_previous_state()

            if previous_state:
                logger.info("Rolling back to previous state")
                # In a real implementation, this would restore the state
                # For now, we just log it

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            return RecoveryResult(
                success=False,
                action=RecoveryAction.ROLLBACK,
                error_context=error_context,
                attempts=1,
                duration_ms=duration,
                message=f"Operation failed, rolled back: {str(e)}",
                metadata={
                    "error": str(e),
                    "rolled_back": previous_state is not None,
                    "previous_state": previous_state
                }
            )

    def _save_state(self, state: Any):
        """Save state to history"""
        self.state_history.append(state)

        # Keep history size limited
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)

    def _get_previous_state(self) -> Optional[Any]:
        """Get previous state from history"""
        if len(self.state_history) < 2:
            return None

        # Remove current state and return previous
        self.state_history.pop()
        return self.state_history[-1]

    def clear_history(self):
        """Clear state history"""
        self.state_history.clear()
