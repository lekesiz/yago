"""
YAGO v8.0 - Health Monitor
Continuous health monitoring and status tracking
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from collections import deque

from .base import (
    HealthStatus,
    HealthCheckResult,
    ErrorContext,
    ErrorSeverity,
)

logger = logging.getLogger(__name__)


class ComponentHealth:
    """Track health metrics for a component"""

    def __init__(self, component: str, window_size: int = 100):
        self.component = component
        self.window_size = window_size

        # Metrics
        self.total_requests = 0
        self.failed_requests = 0
        self.response_times = deque(maxlen=window_size)
        self.errors = deque(maxlen=window_size)
        self.last_check: Optional[datetime] = None
        self.status = HealthStatus.HEALTHY

    def record_success(self, response_time_ms: float):
        """Record a successful operation"""
        self.total_requests += 1
        self.response_times.append(response_time_ms)

    def record_failure(self, error: ErrorContext):
        """Record a failed operation"""
        self.total_requests += 1
        self.failed_requests += 1
        self.errors.append(error)

    def get_error_rate(self) -> float:
        """Calculate error rate"""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests

    def get_success_rate(self) -> float:
        """Calculate success rate"""
        return 1.0 - self.get_error_rate()

    def get_avg_response_time(self) -> Optional[float]:
        """Calculate average response time"""
        if not self.response_times:
            return None
        return sum(self.response_times) / len(self.response_times)

    def get_recent_errors(self, count: int = 10) -> List[ErrorContext]:
        """Get recent errors"""
        return list(self.errors)[-count:]

    def evaluate_health(self) -> HealthStatus:
        """Evaluate current health status"""
        error_rate = self.get_error_rate()
        avg_response_time = self.get_avg_response_time()

        # Check for critical errors
        recent_errors = self.get_recent_errors(5)
        critical_errors = [
            e for e in recent_errors
            if e.severity == ErrorSeverity.CRITICAL
        ]

        if critical_errors:
            return HealthStatus.CRITICAL

        # Check error rate
        if error_rate >= 0.5:
            return HealthStatus.CRITICAL
        elif error_rate >= 0.2:
            return HealthStatus.UNHEALTHY
        elif error_rate >= 0.05:
            return HealthStatus.DEGRADED

        # Check response time
        if avg_response_time and avg_response_time > 5000:  # 5 seconds
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def reset(self):
        """Reset metrics"""
        self.total_requests = 0
        self.failed_requests = 0
        self.response_times.clear()
        self.errors.clear()


class HealthMonitor:
    """
    Continuous health monitoring system
    """

    def __init__(
        self,
        check_interval_seconds: float = 30.0,
        alert_threshold: HealthStatus = HealthStatus.UNHEALTHY
    ):
        self.check_interval = check_interval_seconds
        self.alert_threshold = alert_threshold

        # Component tracking
        self.components: Dict[str, ComponentHealth] = {}

        # Health checks
        self.health_checks: Dict[str, Callable] = {}

        # Alerting
        self.alert_callbacks: List[Callable] = []

        # Monitoring
        self.monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

    def register_component(self, component: str):
        """Register a component for monitoring"""
        if component not in self.components:
            self.components[component] = ComponentHealth(component)
            logger.info(f"Registered component for monitoring: {component}")

    def register_health_check(
        self,
        component: str,
        check_fn: Callable[[], HealthCheckResult]
    ):
        """Register a health check function"""
        self.health_checks[component] = check_fn
        self.register_component(component)
        logger.info(f"Registered health check for: {component}")

    def register_alert_callback(self, callback: Callable):
        """Register callback for health alerts"""
        self.alert_callbacks.append(callback)

    def record_success(self, component: str, response_time_ms: float):
        """Record successful operation"""
        if component not in self.components:
            self.register_component(component)

        self.components[component].record_success(response_time_ms)

    def record_failure(self, component: str, error: ErrorContext):
        """Record failed operation"""
        if component not in self.components:
            self.register_component(component)

        self.components[component].record_failure(error)

        # Check if alert needed
        self._check_alert(component)

    async def check_component_health(
        self,
        component: str
    ) -> HealthCheckResult:
        """Check health of a specific component"""
        if component not in self.components:
            raise ValueError(f"Component not registered: {component}")

        health = self.components[component]

        # Run custom health check if available
        if component in self.health_checks:
            try:
                result = await self.health_checks[component]()
                health.status = result.status
                health.last_check = datetime.utcnow()
                return result
            except Exception as e:
                logger.error(f"Health check failed for {component}: {e}")

        # Default health evaluation
        status = health.evaluate_health()
        health.status = status
        health.last_check = datetime.utcnow()

        # Build issues list
        issues = []
        error_rate = health.get_error_rate()
        if error_rate > 0.05:
            issues.append(f"High error rate: {error_rate*100:.1f}%")

        avg_time = health.get_avg_response_time()
        if avg_time and avg_time > 5000:
            issues.append(f"Slow response time: {avg_time:.0f}ms")

        return HealthCheckResult(
            component=component,
            status=status,
            response_time_ms=avg_time,
            error_rate=error_rate,
            success_rate=health.get_success_rate(),
            message=self._get_status_message(status),
            issues=issues,
            details={
                "total_requests": health.total_requests,
                "failed_requests": health.failed_requests
            }
        )

    async def check_all_health(self) -> Dict[str, HealthCheckResult]:
        """Check health of all components"""
        results = {}

        for component in self.components.keys():
            try:
                result = await self.check_component_health(component)
                results[component] = result
            except Exception as e:
                logger.error(f"Failed to check health of {component}: {e}")
                results[component] = HealthCheckResult(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check failed: {str(e)}"
                )

        return results

    async def get_system_health(self) -> HealthCheckResult:
        """Get overall system health"""
        component_results = await self.check_all_health()

        if not component_results:
            return HealthCheckResult(
                component="system",
                status=HealthStatus.HEALTHY,
                message="No components registered"
            )

        # Aggregate status
        statuses = [r.status for r in component_results.values()]

        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in statuses:
            overall_status = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        # Aggregate metrics
        error_rates = [r.error_rate for r in component_results.values()]
        avg_error_rate = sum(error_rates) / len(error_rates)

        response_times = [
            r.response_time_ms
            for r in component_results.values()
            if r.response_time_ms is not None
        ]
        avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times else None
        )

        # Build issues
        issues = []
        for component, result in component_results.items():
            if result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                issues.append(f"{component}: {result.status.value}")

        return HealthCheckResult(
            component="system",
            status=overall_status,
            response_time_ms=avg_response_time,
            error_rate=avg_error_rate,
            success_rate=1.0 - avg_error_rate,
            message=self._get_status_message(overall_status),
            issues=issues,
            details={
                "components": len(component_results),
                "healthy": sum(
                    1 for r in component_results.values()
                    if r.status == HealthStatus.HEALTHY
                ),
                "degraded": sum(
                    1 for r in component_results.values()
                    if r.status == HealthStatus.DEGRADED
                ),
                "unhealthy": sum(
                    1 for r in component_results.values()
                    if r.status == HealthStatus.UNHEALTHY
                ),
                "critical": sum(
                    1 for r in component_results.values()
                    if r.status == HealthStatus.CRITICAL
                )
            }
        )

    async def start_monitoring(self):
        """Start continuous monitoring"""
        if self.monitoring:
            logger.warning("Monitoring already running")
            return

        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(
            f"Started health monitoring "
            f"(interval: {self.check_interval}s)"
        )

    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.monitoring:
            return

        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped health monitoring")

    async def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring:
            try:
                # Check system health
                system_health = await self.get_system_health()

                # Alert if needed
                if self._should_alert(system_health.status):
                    await self._send_alerts(system_health)

                # Sleep until next check
                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    def _check_alert(self, component: str):
        """Check if alert should be sent for component"""
        health = self.components[component]

        if self._should_alert(health.status):
            asyncio.create_task(self._send_component_alert(component))

    def _should_alert(self, status: HealthStatus) -> bool:
        """Check if status warrants an alert"""
        severity_order = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 1,
            HealthStatus.UNHEALTHY: 2,
            HealthStatus.CRITICAL: 3
        }

        return (
            severity_order.get(status, 0) >=
            severity_order.get(self.alert_threshold, 2)
        )

    async def _send_alerts(self, system_health: HealthCheckResult):
        """Send alerts about system health"""
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(system_health)
                else:
                    callback(system_health)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    async def _send_component_alert(self, component: str):
        """Send alert about component health"""
        try:
            result = await self.check_component_health(component)
            await self._send_alerts(result)
        except Exception as e:
            logger.error(f"Failed to send component alert: {e}")

    def _get_status_message(self, status: HealthStatus) -> str:
        """Get human-readable status message"""
        messages = {
            HealthStatus.HEALTHY: "All systems operational",
            HealthStatus.DEGRADED: "Some issues detected, monitoring",
            HealthStatus.UNHEALTHY: "Significant issues, requires attention",
            HealthStatus.CRITICAL: "Critical issues, immediate action required"
        }
        return messages.get(status, "Unknown status")

    def get_component_stats(self, component: str) -> Dict:
        """Get statistics for a component"""
        if component not in self.components:
            raise ValueError(f"Component not registered: {component}")

        health = self.components[component]

        return {
            "component": component,
            "status": health.status.value,
            "total_requests": health.total_requests,
            "failed_requests": health.failed_requests,
            "error_rate": health.get_error_rate(),
            "success_rate": health.get_success_rate(),
            "avg_response_time_ms": health.get_avg_response_time(),
            "last_check": health.last_check.isoformat() if health.last_check else None,
            "recent_errors": [
                {
                    "error_id": e.error_id,
                    "severity": e.severity.value,
                    "category": e.category.value,
                    "message": e.error_message
                }
                for e in health.get_recent_errors(5)
            ]
        }

    def reset_component(self, component: str):
        """Reset component metrics"""
        if component in self.components:
            self.components[component].reset()
            logger.info(f"Reset metrics for component: {component}")
