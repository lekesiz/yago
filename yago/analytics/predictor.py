"""
YAGO v8.0 - Performance Predictor
Predict future performance metrics
"""

import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from .base import (
    Metric,
    MetricType,
    TimeRange,
    Prediction,
)
from .collector import MetricsCollector

logger = logging.getLogger(__name__)


class PerformancePredictor:
    """
    Predict future performance based on historical data
    """

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def predict_latency(
        self,
        hours_ahead: int = 1,
        component: Optional[str] = None
    ) -> Optional[Prediction]:
        """
        Predict latency N hours ahead

        Args:
            hours_ahead: Number of hours to predict ahead
            component: Optional component filter

        Returns:
            Prediction or None
        """
        return self._predict_metric(
            metric_type=MetricType.LATENCY,
            hours_ahead=hours_ahead,
            component=component,
            model_name="moving_average"
        )

    def predict_throughput(
        self,
        hours_ahead: int = 1,
        component: Optional[str] = None
    ) -> Optional[Prediction]:
        """
        Predict throughput N hours ahead

        Args:
            hours_ahead: Number of hours to predict ahead
            component: Optional component filter

        Returns:
            Prediction or None
        """
        return self._predict_metric(
            metric_type=MetricType.THROUGHPUT,
            hours_ahead=hours_ahead,
            component=component,
            model_name="linear_trend"
        )

    def predict_error_rate(
        self,
        hours_ahead: int = 1,
        component: Optional[str] = None
    ) -> Optional[Prediction]:
        """
        Predict error rate N hours ahead

        Args:
            hours_ahead: Number of hours to predict ahead
            component: Optional component filter

        Returns:
            Prediction or None
        """
        return self._predict_metric(
            metric_type=MetricType.ERROR_RATE,
            hours_ahead=hours_ahead,
            component=component,
            model_name="exponential_smoothing"
        )

    def predict_resource_usage(
        self,
        hours_ahead: int = 1,
        component: Optional[str] = None
    ) -> Optional[Prediction]:
        """
        Predict resource usage N hours ahead

        Args:
            hours_ahead: Number of hours to predict ahead
            component: Optional component filter

        Returns:
            Prediction or None
        """
        return self._predict_metric(
            metric_type=MetricType.RESOURCE_USAGE,
            hours_ahead=hours_ahead,
            component=component,
            model_name="linear_trend"
        )

    def detect_performance_issues(
        self,
        time_range: TimeRange = TimeRange.HOUR,
        component: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect potential performance issues

        Args:
            time_range: Time range to analyze
            component: Optional component filter

        Returns:
            List of detected issues
        """
        issues = []

        # Check latency
        latency_metrics = self.collector.get_metrics(
            metric_type=MetricType.LATENCY,
            time_range=time_range,
            component=component
        )

        if latency_metrics:
            values = [m.value for m in latency_metrics]
            avg_latency = sum(values) / len(values)
            p95_latency = sorted(values)[int(len(values) * 0.95)]

            if p95_latency > 5000:  # 5 seconds
                issues.append({
                    "type": "high_latency",
                    "severity": "high",
                    "metric": "latency",
                    "value": p95_latency,
                    "threshold": 5000,
                    "message": f"P95 latency is {p95_latency:.0f}ms (threshold: 5000ms)",
                    "component": component
                })
            elif avg_latency > 2000:  # 2 seconds
                issues.append({
                    "type": "elevated_latency",
                    "severity": "medium",
                    "metric": "latency",
                    "value": avg_latency,
                    "threshold": 2000,
                    "message": f"Average latency is {avg_latency:.0f}ms (threshold: 2000ms)",
                    "component": component
                })

        # Check error rate
        error_metrics = self.collector.get_metrics(
            metric_type=MetricType.ERROR_RATE,
            time_range=time_range,
            component=component
        )

        if error_metrics:
            values = [m.value for m in error_metrics]
            avg_error_rate = sum(values) / len(values)

            if avg_error_rate > 0.1:  # 10%
                issues.append({
                    "type": "high_error_rate",
                    "severity": "critical",
                    "metric": "error_rate",
                    "value": avg_error_rate,
                    "threshold": 0.1,
                    "message": f"Error rate is {avg_error_rate*100:.1f}% (threshold: 10%)",
                    "component": component
                })
            elif avg_error_rate > 0.05:  # 5%
                issues.append({
                    "type": "elevated_error_rate",
                    "severity": "high",
                    "metric": "error_rate",
                    "value": avg_error_rate,
                    "threshold": 0.05,
                    "message": f"Error rate is {avg_error_rate*100:.1f}% (threshold: 5%)",
                    "component": component
                })

        return issues

    def _predict_metric(
        self,
        metric_type: MetricType,
        hours_ahead: int,
        component: Optional[str],
        model_name: str
    ) -> Optional[Prediction]:
        """
        Generic prediction method

        Args:
            metric_type: Type of metric to predict
            hours_ahead: Hours ahead to predict
            component: Optional component filter
            model_name: Name of prediction model

        Returns:
            Prediction or None
        """
        # Get historical data (last 24 hours)
        metrics = self.collector.get_metrics(
            metric_type=metric_type,
            time_range=TimeRange.DAY,
            component=component
        )

        if len(metrics) < 10:
            logger.warning(
                f"Insufficient data for prediction: {len(metrics)} metrics "
                f"(need at least 10)"
            )
            return None

        # Sort by timestamp
        metrics.sort(key=lambda m: m.timestamp)
        values = [m.value for m in metrics]

        # Apply prediction model
        if model_name == "moving_average":
            predicted_value, confidence = self._moving_average(values)
        elif model_name == "linear_trend":
            predicted_value, confidence = self._linear_trend(values, hours_ahead)
        elif model_name == "exponential_smoothing":
            predicted_value, confidence = self._exponential_smoothing(values)
        else:
            predicted_value, confidence = self._moving_average(values)

        # Calculate bounds (±20% for simplicity)
        margin = predicted_value * 0.2
        lower_bound = max(0, predicted_value - margin)
        upper_bound = predicted_value + margin

        prediction_time = datetime.utcnow() + timedelta(hours=hours_ahead)

        return Prediction(
            prediction_id=f"pred_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            metric_type=metric_type,
            predicted_value=predicted_value,
            confidence=confidence,
            prediction_time=prediction_time,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            model_used=model_name,
            features_used=["historical_values", "time_of_day"],
            metadata={
                "hours_ahead": hours_ahead,
                "data_points": len(metrics),
                "component": component
            }
        )

    def _moving_average(
        self,
        values: List[float],
        window: int = 10
    ) -> tuple[float, float]:
        """
        Simple moving average prediction

        Args:
            values: Historical values
            window: Window size

        Returns:
            (predicted_value, confidence)
        """
        recent = values[-window:]
        predicted = sum(recent) / len(recent)

        # Calculate confidence based on variance
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5

        if mean > 0:
            cv = std_dev / mean  # Coefficient of variation
            confidence = max(0.5, 1.0 - min(cv, 0.5))
        else:
            confidence = 0.5

        return predicted, confidence

    def _linear_trend(
        self,
        values: List[float],
        steps_ahead: int = 1
    ) -> tuple[float, float]:
        """
        Linear trend prediction

        Args:
            values: Historical values
            steps_ahead: Steps ahead to predict

        Returns:
            (predicted_value, confidence)
        """
        n = len(values)
        x = list(range(n))

        # Linear regression
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(i * v for i, v in enumerate(values))
        sum_x2 = sum(i * i for i in x)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return self._moving_average(values)

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # Predict
        predicted = slope * (n + steps_ahead - 1) + intercept
        predicted = max(0, predicted)  # Can't be negative

        # Calculate R-squared for confidence
        mean_y = sum_y / n
        ss_tot = sum((v - mean_y) ** 2 for v in values)
        ss_res = sum((values[i] - (slope * i + intercept)) ** 2 for i in range(n))

        if ss_tot > 0:
            r_squared = 1 - (ss_res / ss_tot)
            confidence = max(0.5, min(abs(r_squared), 1.0))
        else:
            confidence = 0.5

        return predicted, confidence

    def _exponential_smoothing(
        self,
        values: List[float],
        alpha: float = 0.3
    ) -> tuple[float, float]:
        """
        Exponential smoothing prediction

        Args:
            values: Historical values
            alpha: Smoothing factor (0-1)

        Returns:
            (predicted_value, confidence)
        """
        if not values:
            return 0.0, 0.0

        # Apply exponential smoothing
        smoothed = values[0]
        for value in values[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed

        predicted = smoothed

        # Calculate confidence based on recent volatility
        recent = values[-10:]
        if len(recent) > 1:
            mean_recent = sum(recent) / len(recent)
            variance = sum((v - mean_recent) ** 2 for v in recent) / len(recent)
            std_dev = variance ** 0.5

            if mean_recent > 0:
                cv = std_dev / mean_recent
                confidence = max(0.5, 1.0 - min(cv, 0.5))
            else:
                confidence = 0.5
        else:
            confidence = 0.5

        return predicted, confidence
