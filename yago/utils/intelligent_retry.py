"""
Intelligent Retry System for YAGO
Automatically retries failed operations with smart backoff
"""

import time
import logging
from typing import Callable, Any, Optional, List
from functools import wraps

logger = logging.getLogger("YAGO")


class RetryConfig:
    """Retry configuration"""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def intelligent_retry(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: tuple = (Exception,)
):
    """
    Decorator for intelligent retry with exponential backoff

    Usage:
        @intelligent_retry()
        def my_function():
            # code that might fail
            pass
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == config.max_attempts:
                        logger.error(f"❌ All {config.max_attempts} attempts failed for {func.__name__}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.initial_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay
                    )

                    # Add jitter if enabled
                    if config.jitter:
                        import random
                        delay = delay * (0.5 + random.random())

                    logger.warning(
                        f"⚠️  Attempt {attempt}/{config.max_attempts} failed for {func.__name__}. "
                        f"Retrying in {delay:.1f}s... Error: {str(e)}"
                    )

                    time.sleep(delay)

            raise last_exception

        return wrapper
    return decorator


# Default config instances
default_config = RetryConfig()
aggressive_config = RetryConfig(max_attempts=5, initial_delay=0.5)
conservative_config = RetryConfig(max_attempts=2, initial_delay=2.0)
