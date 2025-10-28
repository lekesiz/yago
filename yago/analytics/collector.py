"""
YAGO v8.0 - Metrics Collector
Collect and store metrics for analysis
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque

from .base import (
    Metric,
    MetricType,
    TimeRange,
    AggregationType,
    AnalyticsConfig,
)

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collect and store metrics for analytics
    """

    def __init__(self, config: Optional[AnalyticsConfig] = None):
        self.config = config or AnalyticsConfig()

        # Metrics storage (in-memory for now, can be extended to DB)
        self.metrics: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=100000)  # Keep last 100k metrics per type
            for metric_type in MetricType
        }

        # Collection state
        self.collecting = False
        self.collection_task: Optional[asyncio.Task] = None

        # Statistics
        self.total_metrics_collected = 0
        self.last_collection_time: Optional[datetime] = None

    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        unit: str,
        component: Optional[str] = None,
        operation: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        **metadata
    ) -> Metric:
        """
        Record a single metric

        Args:
            metric_type: Type of metric
            value: Metric value
            unit: Unit of measurement
            component: Optional component name
            operation: Optional operation name
            labels: Optional labels
            **metadata: Additional metadata

        Returns:
            Created metric
        """
        metric = Metric(
            metric_id=f"metric_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            metric_type=metric_type,
            value=value,
            unit=unit,
            component=component,
            operation=operation,
            labels=labels or {},
            metadata=metadata
        )

        self.metrics[metric_type].append(metric)
        self.total_metrics_collected += 1
        self.last_collection_time = datetime.utcnow()

        logger.debug(
            f"Recorded metric: {metric_type.value} = {value} {unit} "
            f"({component or 'system'})"
        )

        return metric

    def record_cost(
        self,
        cost: float,
        component: Optional[str] = None,
        **metadata
    ) -> Metric:
        """Record a cost metric"""
        return self.record_metric(
            metric_type=MetricType.COST,
            value=cost,
            unit="USD",
            component=component,
            **metadata
        )

    def record_latency(
        self,
        latency_ms: float,
        component: Optional[str] = None,
        operation: Optional[str] = None,
        **metadata
    ) -> Metric:
        """Record a latency metric"""
        return self.record_metric(
            metric_type=MetricType.LATENCY,
            value=latency_ms,
            unit="ms",
            component=component,
            operation=operation,
            **metadata
        )

    def record_error_rate(
        self,
        error_rate: float,
        component: Optional[str] = None,
        **metadata
    ) -> Metric:
        """Record an error rate metric"""
        return self.record_metric(
            metric_type=MetricType.ERROR_RATE,
            value=error_rate,
            unit="percentage",
            component=component,
            **metadata
        )

    def record_token_usage(
        self,
        tokens: int,
        component: Optional[str] = None,
        **metadata
    ) -> Metric:
        """Record token usage metric"""
        return self.record_metric(
            metric_type=MetricType.TOKEN_USAGE,
            value=float(tokens),
            unit="tokens",
            component=component,
            **metadata
        )

    def get_metrics(
        self,
        metric_type: MetricType,
        time_range: Optional[TimeRange] = None,
        component: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Metric]:
        """
        Get metrics with filtering

        Args:
            metric_type: Type of metric to retrieve
            time_range: Predefined time range
            component: Filter by component
            start_time: Custom start time
            end_time: Custom end time
            limit: Maximum number of metrics to return

        Returns:
            List of metrics matching filters
        """
        metrics = list(self.metrics[metric_type])

        # Apply time filtering
        if time_range or start_time or end_time:
            start, end = self._get_time_bounds(time_range, start_time, end_time)

            metrics = [
                m for m in metrics
                if start <= m.timestamp <= end
            ]

        # Apply component filtering
        if component:
            metrics = [m for m in metrics if m.component == component]

        # Sort by timestamp (newest first)
        metrics.sort(key=lambda m: m.timestamp, reverse=True)

        # Apply limit
        if limit:
            metrics = metrics[:limit]

        return metrics

    def aggregate_metrics(
        self,
        metric_type: MetricType,
        aggregation: AggregationType,
        time_range: Optional[TimeRange] = None,
        component: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[float]:
        """
        Aggregate metrics

        Args:
            metric_type: Type of metric
            aggregation: Aggregation method
            time_range: Time range filter
            component: Component filter
            start_time: Custom start time
            end_time: Custom end time

        Returns:
            Aggregated value or None if no metrics
        """
        metrics = self.get_metrics(
            metric_type=metric_type,
            time_range=time_range,
            component=component,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            return None

        values = [m.value for m in metrics]

        if aggregation == AggregationType.SUM:
            return sum(values)
        elif aggregation == AggregationType.AVG:
            return sum(values) / len(values)
        elif aggregation == AggregationType.MIN:
            return min(values)
        elif aggregation == AggregationType.MAX:
            return max(values)
        elif aggregation == AggregationType.COUNT:
            return float(len(values))
        elif aggregation == AggregationType.MEDIAN:
            sorted_values = sorted(values)
            n = len(sorted_values)
            if n % 2 == 0:
                return (sorted_values[n//2-1] + sorted_values[n//2]) / 2
            else:
                return sorted_values[n//2]
        elif aggregation == AggregationType.P95:
            sorted_values = sorted(values)
            index = int(len(sorted_values) * 0.95)
            return sorted_values[index]
        elif aggregation == AggregationType.P99:
            sorted_values = sorted(values)
            index = int(len(sorted_values) * 0.99)
            return sorted_values[index]

        return None

    def get_time_series(
        self,
        metric_type: MetricType,
        time_range: TimeRange,
        interval_minutes: int = 60,
        aggregation: AggregationType = AggregationType.AVG,
        component: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get time series data

        Args:
            metric_type: Type of metric
            time_range: Time range
            interval_minutes: Interval for bucketing
            aggregation: Aggregation method
            component: Optional component filter

        Returns:
            List of time series data points
        """
        start_time, end_time = self._get_time_bounds(time_range)
        metrics = self.get_metrics(
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time,
            component=component
        )

        if not metrics:
            return []

        # Create time buckets
        interval = timedelta(minutes=interval_minutes)
        buckets: Dict[datetime, List[float]] = {}

        current = start_time
        while current <= end_time:
            buckets[current] = []
            current += interval

        # Fill buckets
        for metric in metrics:
            bucket_time = self._get_bucket_time(
                metric.timestamp,
                start_time,
                interval
            )
            if bucket_time in buckets:
                buckets[bucket_time].append(metric.value)

        # Aggregate buckets
        time_series = []
        for timestamp, values in sorted(buckets.items()):
            if values:
                if aggregation == AggregationType.AVG:
                    value = sum(values) / len(values)
                elif aggregation == AggregationType.SUM:
                    value = sum(values)
                elif aggregation == AggregationType.MAX:
                    value = max(values)
                elif aggregation == AggregationType.MIN:
                    value = min(values)
                else:
                    value = sum(values) / len(values)

                time_series.append({
                    "timestamp": timestamp.isoformat(),
                    "value": value,
                    "count": len(values)
                })

        return time_series

    def get_statistics(
        self,
        metric_type: MetricType,
        time_range: Optional[TimeRange] = None,
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for a metric type

        Args:
            metric_type: Type of metric
            time_range: Time range filter
            component: Component filter

        Returns:
            Statistics dictionary
        """
        metrics = self.get_metrics(
            metric_type=metric_type,
            time_range=time_range,
            component=component
        )

        if not metrics:
            return {
                "count": 0,
                "sum": 0.0,
                "avg": 0.0,
                "min": 0.0,
                "max": 0.0,
                "median": 0.0,
                "p95": 0.0,
                "p99": 0.0
            }

        values = [m.value for m in metrics]
        sorted_values = sorted(values)

        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "median": self._calculate_median(sorted_values),
            "p95": sorted_values[int(len(sorted_values) * 0.95)],
            "p99": sorted_values[int(len(sorted_values) * 0.99)],
            "first_timestamp": metrics[-1].timestamp.isoformat(),
            "last_timestamp": metrics[0].timestamp.isoformat()
        }

    def get_components(self) -> List[str]:
        """Get list of all components with metrics"""
        components = set()

        for metric_deque in self.metrics.values():
            for metric in metric_deque:
                if metric.component:
                    components.add(metric.component)

        return sorted(list(components))

    def clear_metrics(
        self,
        metric_type: Optional[MetricType] = None,
        older_than: Optional[datetime] = None
    ):
        """
        Clear metrics

        Args:
            metric_type: Optional specific type to clear
            older_than: Optional datetime to clear metrics older than
        """
        if metric_type:
            if older_than:
                # Clear specific type older than date
                self.metrics[metric_type] = deque(
                    [m for m in self.metrics[metric_type] if m.timestamp >= older_than],
                    maxlen=100000
                )
            else:
                # Clear all of specific type
                self.metrics[metric_type].clear()
        else:
            if older_than:
                # Clear all metrics older than date
                for mt in MetricType:
                    self.metrics[mt] = deque(
                        [m for m in self.metrics[mt] if m.timestamp >= older_than],
                        maxlen=100000
                    )
            else:
                # Clear all metrics
                for mt in MetricType:
                    self.metrics[mt].clear()

        logger.info("Cleared metrics")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics"""
        return {
            "total_metrics_collected": self.total_metrics_collected,
            "last_collection_time": (
                self.last_collection_time.isoformat()
                if self.last_collection_time else None
            ),
            "metrics_by_type": {
                mt.value: len(self.metrics[mt])
                for mt in MetricType
            },
            "components": self.get_components(),
            "collecting": self.collecting
        }

    def _get_time_bounds(
        self,
        time_range: Optional[TimeRange] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> tuple[datetime, datetime]:
        """Get start and end times for filtering"""
        now = datetime.utcnow()

        if start_time and end_time:
            return start_time, end_time

        if time_range == TimeRange.HOUR:
            start = now - timedelta(hours=1)
        elif time_range == TimeRange.DAY:
            start = now - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            start = now - timedelta(weeks=1)
        elif time_range == TimeRange.MONTH:
            start = now - timedelta(days=30)
        elif time_range == TimeRange.QUARTER:
            start = now - timedelta(days=90)
        elif time_range == TimeRange.YEAR:
            start = now - timedelta(days=365)
        else:
            start = datetime.min

        end = end_time or now

        return start, end

    def _get_bucket_time(
        self,
        timestamp: datetime,
        start_time: datetime,
        interval: timedelta
    ) -> datetime:
        """Get the bucket time for a timestamp"""
        delta = timestamp - start_time
        bucket_index = int(delta.total_seconds() / interval.total_seconds())
        return start_time + (interval * bucket_index)

    def _calculate_median(self, sorted_values: List[float]) -> float:
        """Calculate median from sorted values"""
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2-1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]

    async def start_collection(self):
        """Start automatic metric collection (placeholder for future use)"""
        if self.collecting:
            logger.warning("Collection already running")
            return

        self.collecting = True
        logger.info("Started metrics collection")

    async def stop_collection(self):
        """Stop automatic metric collection"""
        if not self.collecting:
            return

        self.collecting = False
        logger.info("Stopped metrics collection")
