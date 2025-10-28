"""
YAGO v8.0 - Anomaly Detector
Detect anomalies in metrics
"""

import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import (
    MetricType,
    TimeRange,
    Anomaly,
)
from .collector import MetricsCollector

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detect anomalies in metrics using statistical methods
    """

    def __init__(
        self,
        collector: MetricsCollector,
        threshold_std_dev: float = 2.0
    ):
        self.collector = collector
        self.threshold_std_dev = threshold_std_dev

    def detect_anomalies(
        self,
        metric_type: MetricType,
        time_range: TimeRange = TimeRange.DAY,
        component: Optional[str] = None,
        method: str = "statistical"
    ) -> List[Anomaly]:
        """
        Detect anomalies in metrics

        Args:
            metric_type: Type of metric to analyze
            time_range: Time range to check
            component: Optional component filter
            method: Detection method ('statistical', 'iqr', 'moving_average')

        Returns:
            List of detected anomalies
        """
        if method == "statistical":
            return self._detect_statistical(metric_type, time_range, component)
        elif method == "iqr":
            return self._detect_iqr(metric_type, time_range, component)
        elif method == "moving_average":
            return self._detect_moving_average(metric_type, time_range, component)
        else:
            return self._detect_statistical(metric_type, time_range, component)

    def detect_cost_anomalies(
        self,
        time_range: TimeRange = TimeRange.DAY,
        component: Optional[str] = None
    ) -> List[Anomaly]:
        """Detect cost anomalies"""
        return self.detect_anomalies(
            metric_type=MetricType.COST,
            time_range=time_range,
            component=component,
            method="statistical"
        )

    def detect_latency_anomalies(
        self,
        time_range: TimeRange = TimeRange.DAY,
        component: Optional[str] = None
    ) -> List[Anomaly]:
        """Detect latency anomalies"""
        return self.detect_anomalies(
            metric_type=MetricType.LATENCY,
            time_range=time_range,
            component=component,
            method="statistical"
        )

    def detect_error_anomalies(
        self,
        time_range: TimeRange = TimeRange.DAY,
        component: Optional[str] = None
    ) -> List[Anomaly]:
        """Detect error rate anomalies"""
        return self.detect_anomalies(
            metric_type=MetricType.ERROR_RATE,
            time_range=time_range,
            component=component,
            method="statistical"
        )

    def get_anomaly_summary(
        self,
        time_range: TimeRange = TimeRange.DAY,
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summary of all anomalies

        Args:
            time_range: Time range to analyze
            component: Optional component filter

        Returns:
            Anomaly summary
        """
        all_anomalies = []

        # Check key metrics
        for metric_type in [MetricType.COST, MetricType.LATENCY, MetricType.ERROR_RATE]:
            anomalies = self.detect_anomalies(
                metric_type=metric_type,
                time_range=time_range,
                component=component
            )
            all_anomalies.extend(anomalies)

        # Group by severity
        critical = [a for a in all_anomalies if a.severity >= 0.8]
        high = [a for a in all_anomalies if 0.6 <= a.severity < 0.8]
        medium = [a for a in all_anomalies if 0.4 <= a.severity < 0.6]
        low = [a for a in all_anomalies if a.severity < 0.4]

        return {
            "total_anomalies": len(all_anomalies),
            "by_severity": {
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low)
            },
            "by_metric": {
                metric_type.value: len([
                    a for a in all_anomalies
                    if a.metric_type == metric_type
                ])
                for metric_type in [MetricType.COST, MetricType.LATENCY, MetricType.ERROR_RATE]
            },
            "anomalies": [
                {
                    "anomaly_id": a.anomaly_id,
                    "metric_type": a.metric_type.value,
                    "severity": a.severity,
                    "expected": a.expected_value,
                    "actual": a.actual_value,
                    "deviation": a.deviation,
                    "description": a.description,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in sorted(all_anomalies, key=lambda x: x.severity, reverse=True)
            ]
        }

    def _detect_statistical(
        self,
        metric_type: MetricType,
        time_range: TimeRange,
        component: Optional[str]
    ) -> List[Anomaly]:
        """
        Detect anomalies using statistical method (Z-score)

        Args:
            metric_type: Type of metric
            time_range: Time range
            component: Optional component filter

        Returns:
            List of anomalies
        """
        metrics = self.collector.get_metrics(
            metric_type=metric_type,
            time_range=time_range,
            component=component
        )

        if len(metrics) < 10:
            return []

        values = [m.value for m in metrics]

        # Calculate statistics
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return []

        # Find anomalies
        anomalies = []

        for metric in metrics:
            z_score = abs((metric.value - mean) / std_dev)

            if z_score > self.threshold_std_dev:
                deviation = metric.value - mean
                severity = min(z_score / 5.0, 1.0)  # Normalize to 0-1

                description = self._generate_anomaly_description(
                    metric_type,
                    mean,
                    metric.value,
                    deviation,
                    metric.unit
                )

                anomaly = Anomaly(
                    anomaly_id=f"anom_{uuid.uuid4().hex[:12]}",
                    timestamp=metric.timestamp,
                    metric_type=metric_type,
                    expected_value=mean,
                    actual_value=metric.value,
                    deviation=deviation,
                    severity=severity,
                    detection_method="statistical",
                    confidence=min(z_score / 3.0, 0.99),
                    component=component,
                    description=description,
                    metadata={
                        "z_score": z_score,
                        "std_dev": std_dev,
                        "threshold": self.threshold_std_dev
                    }
                )

                anomalies.append(anomaly)

        return anomalies

    def _detect_iqr(
        self,
        metric_type: MetricType,
        time_range: TimeRange,
        component: Optional[str]
    ) -> List[Anomaly]:
        """
        Detect anomalies using IQR (Interquartile Range) method

        Args:
            metric_type: Type of metric
            time_range: Time range
            component: Optional component filter

        Returns:
            List of anomalies
        """
        metrics = self.collector.get_metrics(
            metric_type=metric_type,
            time_range=time_range,
            component=component
        )

        if len(metrics) < 10:
            return []

        values = sorted([m.value for m in metrics])
        n = len(values)

        # Calculate quartiles
        q1 = values[n // 4]
        q3 = values[(3 * n) // 4]
        iqr = q3 - q1

        # Calculate bounds
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Find anomalies
        anomalies = []
        median = values[n // 2]

        for metric in metrics:
            if metric.value < lower_bound or metric.value > upper_bound:
                deviation = metric.value - median
                severity = min(abs(deviation) / (upper_bound - lower_bound), 1.0)

                description = self._generate_anomaly_description(
                    metric_type,
                    median,
                    metric.value,
                    deviation,
                    metric.unit
                )

                anomaly = Anomaly(
                    anomaly_id=f"anom_{uuid.uuid4().hex[:12]}",
                    timestamp=metric.timestamp,
                    metric_type=metric_type,
                    expected_value=median,
                    actual_value=metric.value,
                    deviation=deviation,
                    severity=severity,
                    detection_method="iqr",
                    confidence=0.85,
                    component=component,
                    description=description,
                    metadata={
                        "q1": q1,
                        "q3": q3,
                        "iqr": iqr,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound
                    }
                )

                anomalies.append(anomaly)

        return anomalies

    def _detect_moving_average(
        self,
        metric_type: MetricType,
        time_range: TimeRange,
        component: Optional[str]
    ) -> List[Anomaly]:
        """
        Detect anomalies using moving average method

        Args:
            metric_type: Type of metric
            time_range: Time range
            component: Optional component filter

        Returns:
            List of anomalies
        """
        metrics = self.collector.get_metrics(
            metric_type=metric_type,
            time_range=time_range,
            component=component
        )

        if len(metrics) < 20:
            return []

        # Sort by timestamp
        metrics.sort(key=lambda m: m.timestamp)

        window_size = 10
        threshold_factor = 2.0
        anomalies = []

        for i in range(window_size, len(metrics)):
            # Calculate moving average from previous window
            window = metrics[i-window_size:i]
            window_values = [m.value for m in window]
            moving_avg = sum(window_values) / len(window_values)

            # Calculate moving std dev
            variance = sum((v - moving_avg) ** 2 for v in window_values) / len(window_values)
            std_dev = variance ** 0.5

            current_metric = metrics[i]
            deviation = current_metric.value - moving_avg

            # Check if anomaly
            if std_dev > 0 and abs(deviation) > threshold_factor * std_dev:
                severity = min(abs(deviation) / (threshold_factor * std_dev * 2), 1.0)

                description = self._generate_anomaly_description(
                    metric_type,
                    moving_avg,
                    current_metric.value,
                    deviation,
                    current_metric.unit
                )

                anomaly = Anomaly(
                    anomaly_id=f"anom_{uuid.uuid4().hex[:12]}",
                    timestamp=current_metric.timestamp,
                    metric_type=metric_type,
                    expected_value=moving_avg,
                    actual_value=current_metric.value,
                    deviation=deviation,
                    severity=severity,
                    detection_method="moving_average",
                    confidence=0.80,
                    component=component,
                    description=description,
                    metadata={
                        "window_size": window_size,
                        "moving_avg": moving_avg,
                        "std_dev": std_dev
                    }
                )

                anomalies.append(anomaly)

        return anomalies

    def _generate_anomaly_description(
        self,
        metric_type: MetricType,
        expected: float,
        actual: float,
        deviation: float,
        unit: str
    ) -> str:
        """Generate human-readable anomaly description"""
        metric_name = metric_type.value.replace("_", " ").title()

        if deviation > 0:
            direction = "spike"
            factor = actual / expected if expected > 0 else 0
            return (
                f"{metric_name} {direction} detected: "
                f"{actual:.2f} {unit} (expected: {expected:.2f} {unit}). "
                f"{factor:.1f}x higher than expected."
            )
        else:
            direction = "drop"
            factor = expected / actual if actual > 0 else 0
            return (
                f"{metric_name} {direction} detected: "
                f"{actual:.2f} {unit} (expected: {expected:.2f} {unit}). "
                f"{factor:.1f}x lower than expected."
            )
