"""
Intelligent Rate Limiter & Error Aggregator
YAGO v5.7.0

API rate limit ve long-running istekler için akıllı bekleme sistemi:
- Exponential backoff ile otomatik retry
- Rate limit detection ve automatic waiting
- Error pattern analysis ve aggregation
- Self-healing: Hatalardan öğrenip kendini geliştirme
- Persistent retry: Başarıya ulaşana kadar durmadan deneme
"""

import time
import logging
import hashlib
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from collections import Counter

logger = logging.getLogger("YAGO.RateLimiter")


class ErrorCategory(Enum):
    """Error categories for pattern analysis"""
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    API_ERROR = "api_error"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    CONTEXT_SIZE = "context_size"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    """Record of an error occurrence"""
    timestamp: datetime
    category: ErrorCategory
    error_message: str
    provider: str
    model: str
    retry_count: int
    recovery_action: Optional[str] = None
    success_after_retry: bool = False


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    initial_wait: float = 2.0  # Initial wait time in seconds
    max_wait: float = 300.0  # Maximum wait time (5 minutes)
    exponential_base: float = 2.0  # Exponential backoff multiplier
    max_retries: int = 10  # Maximum retry attempts (-1 for infinite)
    jitter: bool = True  # Add random jitter to prevent thundering herd

    # Rate limit detection patterns
    rate_limit_keywords: List[str] = field(default_factory=lambda: [
        "rate limit",
        "rate_limit",
        "too many requests",
        "429",
        "quota exceeded",
        "throttle",
        "slow down",
    ])

    # Timeout patterns
    timeout_keywords: List[str] = field(default_factory=lambda: [
        "timeout",
        "timed out",
        "deadline exceeded",
        "connection timeout",
    ])


class IntelligentRateLimiter:
    """
    Intelligent Rate Limiter with Error Aggregation

    Features:
    - Automatic rate limit detection
    - Exponential backoff with jitter
    - Error pattern analysis
    - Self-healing recommendations
    - Persistent retry until success
    - Error aggregation and reporting
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize intelligent rate limiter

        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()
        self.error_history: List[ErrorRecord] = []
        self.retry_counts: Dict[str, int] = {}  # task_id -> retry_count
        self.success_after_retry: Dict[str, int] = {}  # task_id -> successful_retry_number

        # Statistics
        self.total_retries = 0
        self.total_successes = 0
        self.total_failures = 0

        # Error patterns for self-improvement
        self.error_patterns: Dict[str, int] = {}

        # Load historical errors
        self._load_error_history()

    def execute_with_retry(
        self,
        func: Callable,
        task_id: str,
        *args,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Execute a function with intelligent retry logic

        Args:
            func: Function to execute
            task_id: Unique task identifier
            *args: Function arguments
            max_retries: Override max retries (None = use config, -1 = infinite)
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If max retries exceeded and still failing
        """
        max_retries = max_retries if max_retries is not None else self.config.max_retries
        retry_count = 0
        last_error = None

        # Initialize retry tracking
        self.retry_counts[task_id] = 0

        logger.info(f"🎯 Starting task: {task_id}")

        while True:
            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Success!
                if retry_count > 0:
                    logger.info(f"✅ Task succeeded after {retry_count} retries: {task_id}")
                    self.success_after_retry[task_id] = retry_count
                    self.total_successes += 1

                    # Record successful recovery
                    if last_error:
                        self._record_success_after_error(last_error, retry_count)
                else:
                    logger.info(f"✅ Task succeeded on first try: {task_id}")
                    self.total_successes += 1

                return result

            except Exception as e:
                retry_count += 1
                self.retry_counts[task_id] = retry_count
                self.total_retries += 1
                last_error = e

                # Categorize error
                category = self._categorize_error(e)
                error_msg = str(e)

                # Record error
                self._record_error(
                    category=category,
                    error_message=error_msg,
                    provider=kwargs.get('provider', 'unknown'),
                    model=kwargs.get('model', 'unknown'),
                    retry_count=retry_count
                )

                # Check if should retry
                if max_retries != -1 and retry_count >= max_retries:
                    logger.error(f"❌ Task failed after {retry_count} retries: {task_id}")
                    logger.error(f"   Last error: {error_msg}")
                    self.total_failures += 1
                    raise Exception(f"Max retries ({max_retries}) exceeded for task: {task_id}") from e

                # Calculate wait time
                wait_time = self._calculate_wait_time(retry_count, category)

                # Log retry attempt
                retry_msg = f"infinite" if max_retries == -1 else max_retries
                logger.warning(f"⚠️ Error on attempt {retry_count}/{retry_msg}: {task_id}")
                logger.warning(f"   Category: {category.value}")
                logger.warning(f"   Error: {error_msg[:100]}...")
                logger.info(f"⏳ Waiting {wait_time:.1f}s before retry {retry_count + 1}...")

                # Wait before retry
                time.sleep(wait_time)

                # Log retry start
                logger.info(f"🔄 Retrying attempt {retry_count + 1}: {task_id}")

    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on message patterns"""
        error_msg = str(error).lower()

        # Check rate limit
        for keyword in self.config.rate_limit_keywords:
            if keyword.lower() in error_msg:
                return ErrorCategory.RATE_LIMIT

        # Check timeout
        for keyword in self.config.timeout_keywords:
            if keyword.lower() in error_msg:
                return ErrorCategory.TIMEOUT

        # Check API errors
        if "api" in error_msg or "server" in error_msg or "500" in error_msg or "502" in error_msg:
            return ErrorCategory.API_ERROR

        # Check network
        if "network" in error_msg or "connection" in error_msg or "dns" in error_msg:
            return ErrorCategory.NETWORK

        # Check authentication
        if "auth" in error_msg or "unauthorized" in error_msg or "401" in error_msg or "403" in error_msg:
            return ErrorCategory.AUTHENTICATION

        # Check context size
        if "context" in error_msg or "token" in error_msg or "too large" in error_msg:
            return ErrorCategory.CONTEXT_SIZE

        return ErrorCategory.UNKNOWN

    def _calculate_wait_time(self, retry_count: int, category: ErrorCategory) -> float:
        """Calculate wait time with exponential backoff and jitter"""
        # Base wait time from config
        wait_time = self.config.initial_wait * (self.config.exponential_base ** (retry_count - 1))

        # Category-specific adjustments
        if category == ErrorCategory.RATE_LIMIT:
            # Rate limits need longer waits
            wait_time *= 2.0
        elif category == ErrorCategory.TIMEOUT:
            # Timeouts might need less aggressive backoff
            wait_time *= 0.8
        elif category == ErrorCategory.CONTEXT_SIZE:
            # Context size errors don't need exponential backoff
            wait_time = self.config.initial_wait

        # Cap at max wait time
        wait_time = min(wait_time, self.config.max_wait)

        # Add jitter to prevent thundering herd
        if self.config.jitter:
            import random
            jitter_amount = wait_time * 0.1  # 10% jitter
            wait_time += random.uniform(-jitter_amount, jitter_amount)

        return max(wait_time, 0.5)  # Minimum 0.5 seconds

    def _record_error(
        self,
        category: ErrorCategory,
        error_message: str,
        provider: str,
        model: str,
        retry_count: int
    ):
        """Record an error occurrence"""
        record = ErrorRecord(
            timestamp=datetime.now(),
            category=category,
            error_message=error_message,
            provider=provider,
            model=model,
            retry_count=retry_count
        )
        self.error_history.append(record)

        # Update error patterns
        pattern_key = f"{category.value}:{provider}"
        self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1

    def _record_success_after_error(self, error: Exception, retry_count: int):
        """Record successful recovery after error"""
        if self.error_history:
            # Update last error record
            last_record = self.error_history[-1]
            last_record.success_after_retry = True
            last_record.recovery_action = f"Succeeded after {retry_count} retries"

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        if not self.error_history:
            return {
                "total_errors": 0,
                "total_retries": self.total_retries,
                "total_successes": self.total_successes,
                "total_failures": self.total_failures,
            }

        # Category breakdown
        category_counts = Counter(record.category.value for record in self.error_history)

        # Provider breakdown
        provider_counts = Counter(record.provider for record in self.error_history)

        # Success rate after retry
        retry_successes = sum(1 for record in self.error_history if record.success_after_retry)
        retry_attempts = len(self.error_history)
        success_rate = (retry_successes / retry_attempts * 100) if retry_attempts > 0 else 0

        # Average retries for successful recoveries
        successful_retries = [record.retry_count for record in self.error_history if record.success_after_retry]
        avg_retries = sum(successful_retries) / len(successful_retries) if successful_retries else 0

        return {
            "total_errors": len(self.error_history),
            "total_retries": self.total_retries,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "success_rate_after_retry": round(success_rate, 2),
            "average_retries_to_success": round(avg_retries, 2),
            "by_category": dict(category_counts),
            "by_provider": dict(provider_counts),
            "error_patterns": self.error_patterns,
        }

    def get_self_improvement_recommendations(self) -> List[str]:
        """
        Analyze error patterns and generate self-improvement recommendations
        """
        recommendations = []
        stats = self.get_error_statistics()

        if stats["total_errors"] == 0:
            return ["✅ No errors detected - system running smoothly!"]

        # Analyze by category
        categories = stats.get("by_category", {})

        # Rate limit recommendations
        if categories.get("rate_limit", 0) > 5:
            recommendations.append(
                "🔴 HIGH: Frequent rate limit errors detected. "
                "Consider: 1) Implementing request batching, "
                "2) Increasing initial wait time, "
                "3) Using multiple API keys with round-robin"
            )

        # Timeout recommendations
        if categories.get("timeout", 0) > 3:
            recommendations.append(
                "🟡 MEDIUM: Multiple timeout errors. "
                "Consider: 1) Increasing timeout values, "
                "2) Breaking large requests into smaller chunks, "
                "3) Using streaming responses"
            )

        # Context size recommendations
        if categories.get("context_size", 0) > 2:
            recommendations.append(
                "🟡 MEDIUM: Context size errors detected. "
                "Consider: 1) Implementing smart truncation, "
                "2) Using summarization before sending, "
                "3) Switching to models with larger context windows"
            )

        # API error recommendations
        if categories.get("api_error", 0) > 5:
            recommendations.append(
                "🔴 HIGH: Frequent API errors. "
                "Consider: 1) Using AI failover to alternative providers, "
                "2) Implementing circuit breaker pattern, "
                "3) Adding health check before requests"
            )

        # Success rate analysis
        if stats["success_rate_after_retry"] < 50:
            recommendations.append(
                "🔴 CRITICAL: Low success rate after retry (<50%). "
                "Consider: 1) Reviewing error handling logic, "
                "2) Increasing max retries, "
                "3) Investigating root cause of failures"
            )
        elif stats["success_rate_after_retry"] > 90:
            recommendations.append(
                "✅ EXCELLENT: High success rate after retry (>90%). "
                "Current retry strategy is working well!"
            )

        # Retry optimization
        if stats["average_retries_to_success"] > 5:
            recommendations.append(
                "🟡 MEDIUM: High average retries needed. "
                "Consider: 1) Adjusting exponential backoff parameters, "
                "2) Implementing smarter wait time calculation, "
                "3) Using provider-specific retry strategies"
            )

        return recommendations if recommendations else ["✅ System performance is acceptable"]

    def _load_error_history(self):
        """Load historical error data from disk"""
        try:
            history_file = Path(__file__).parent.parent / "logs" / "error_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    # TODO: Deserialize error records
                    logger.info(f"📂 Loaded {len(data)} historical error records")
        except Exception as e:
            logger.debug(f"Could not load error history: {e}")

    def save_error_history(self):
        """Save error history to disk for persistence"""
        try:
            history_file = Path(__file__).parent.parent / "logs" / "error_history.json"
            history_file.parent.mkdir(parents=True, exist_ok=True)

            data = []
            for record in self.error_history:
                data.append({
                    "timestamp": record.timestamp.isoformat(),
                    "category": record.category.value,
                    "error_message": record.error_message,
                    "provider": record.provider,
                    "model": record.model,
                    "retry_count": record.retry_count,
                    "recovery_action": record.recovery_action,
                    "success_after_retry": record.success_after_retry,
                })

            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"💾 Saved {len(data)} error records to {history_file}")

        except Exception as e:
            logger.error(f"Failed to save error history: {e}")

    def generate_error_report(self, output_file: Optional[Path] = None) -> str:
        """Generate comprehensive error report"""
        stats = self.get_error_statistics()
        recommendations = self.get_self_improvement_recommendations()

        report = []
        report.append("=" * 80)
        report.append("🔍 YAGO ERROR ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\n📅 Generated: {datetime.now().isoformat()}")
        report.append(f"\n📊 STATISTICS")
        report.append("-" * 80)
        report.append(f"Total Errors: {stats['total_errors']}")
        report.append(f"Total Retries: {stats['total_retries']}")
        report.append(f"Total Successes: {stats['total_successes']}")
        report.append(f"Total Failures: {stats['total_failures']}")
        report.append(f"Success Rate After Retry: {stats['success_rate_after_retry']}%")
        report.append(f"Average Retries to Success: {stats['average_retries_to_success']}")

        report.append(f"\n📈 ERROR BREAKDOWN BY CATEGORY")
        report.append("-" * 80)
        for category, count in stats.get('by_category', {}).items():
            report.append(f"  {category}: {count}")

        report.append(f"\n🤖 ERROR BREAKDOWN BY PROVIDER")
        report.append("-" * 80)
        for provider, count in stats.get('by_provider', {}).items():
            report.append(f"  {provider}: {count}")

        report.append(f"\n💡 SELF-IMPROVEMENT RECOMMENDATIONS")
        report.append("-" * 80)
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")

        report.append("\n" + "=" * 80)

        report_text = "\n".join(report)

        # Save to file if requested
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"📄 Error report saved to: {output_file}")

        return report_text


# Singleton instance
_rate_limiter_instance = None


def get_rate_limiter() -> IntelligentRateLimiter:
    """Get IntelligentRateLimiter singleton"""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = IntelligentRateLimiter()
    return _rate_limiter_instance


def reset_rate_limiter():
    """Reset singleton (for testing)"""
    global _rate_limiter_instance
    _rate_limiter_instance = None


if __name__ == "__main__":
    # Test rate limiter
    limiter = get_rate_limiter()

    # Simulate some errors and retries
    def flaky_function(fail_count=3):
        """Function that fails first N times then succeeds"""
        if not hasattr(flaky_function, 'attempt'):
            flaky_function.attempt = 0

        flaky_function.attempt += 1

        if flaky_function.attempt <= fail_count:
            if flaky_function.attempt == 1:
                raise Exception("rate limit exceeded - 429")
            elif flaky_function.attempt == 2:
                raise Exception("timeout after 30s")
            else:
                raise Exception("Internal server error - 500")

        return "Success!"

    # Test with retry
    try:
        result = limiter.execute_with_retry(
            flaky_function,
            task_id="test_task",
            max_retries=5
        )
        print(f"\n✅ Result: {result}")
    except Exception as e:
        print(f"\n❌ Failed: {e}")

    # Generate report
    print("\n" + limiter.generate_error_report())

    # Get recommendations
    print("\n🎯 Recommendations:")
    for rec in limiter.get_self_improvement_recommendations():
        print(f"  - {rec}")
