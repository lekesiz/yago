"""
YAGO v8.0 - Metrics Analyzer
Analyze metrics and detect trends
"""

import logging
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import Counter

from .base import (
    Metric,
    MetricType,
    TimeRange,
    Trend,
    UsagePattern,
)
from .collector import MetricsCollector

logger = logging.getLogger(__name__)


class MetricsAnalyzer:
    """
    Analyze metrics and detect patterns
    """

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def detect_trend(
        self,
        metric_type: MetricType,
        time_range: TimeRange = TimeRange.WEEK,
        component: Optional[str] = None
    ) -> Optional[Trend]:
        """
        Detect trend in metrics

        Args:
            metric_type: Type of metric to analyze
            time_range: Time range to analyze
            component: Optional component filter

        Returns:
            Detected trend or None
        """
        metrics = self.collector.get_metrics(
            metric_type=metric_type,
            time_range=time_range,
            component=component
        )

        if len(metrics) < 10:  # Need minimum data points
            return None

        # Sort by timestamp
        metrics.sort(key=lambda m: m.timestamp)

        # Calculate trend
        values = [m.value for m in metrics]
        timestamps = [(m.timestamp - metrics[0].timestamp).total_seconds() for m in metrics]

        # Linear regression
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)

        # Calculate slope (trend)
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return None

        slope = (n * sum_xy - sum_x * sum_y) / denominator

        # Calculate correlation
        mean_x = sum_x / n
        mean_y = sum_y / n
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(timestamps, values))
        denominator_x = sum((x - mean_x) ** 2 for x in timestamps) ** 0.5
        denominator_y = sum((y - mean_y) ** 2 for y in values) ** 0.5

        if denominator_x == 0 or denominator_y == 0:
            correlation = 0.0
        else:
            correlation = numerator / (denominator_x * denominator_y)

        # Determine direction and magnitude
        if abs(slope) < 0.01:  # Threshold for stability
            direction = "stable"
            magnitude = 0.0
        elif slope > 0:
            direction = "up"
            magnitude = slope * (timestamps[-1] - timestamps[0])
        else:
            direction = "down"
            magnitude = abs(slope * (timestamps[-1] - timestamps[0]))

        # Calculate velocity (change per day)
        time_span_days = (metrics[-1].timestamp - metrics[0].timestamp).total_seconds() / 86400
        if time_span_days > 0:
            velocity = (values[-1] - values[0]) / time_span_days
        else:
            velocity = 0.0

        # Generate description
        unit = metrics[0].unit if metrics else "units"
        description = self._generate_trend_description(
            direction,
            magnitude,
            velocity,
            unit,
            metric_type
        )

        return Trend(
            trend_id=f"trend_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            metric_type=metric_type,
            direction=direction,
            magnitude=magnitude,
            velocity=velocity,
            period_start=metrics[0].timestamp,
            period_end=metrics[-1].timestamp,
            slope=slope,
            correlation=correlation,
            confidence=abs(correlation),
            description=description
        )

    def detect_pattern(
        self,
        metric_type: MetricType,
        time_range: TimeRange = TimeRange.WEEK,
        component: Optional[str] = None
    ) -> Optional[UsagePattern]:
        """
        Detect usage patterns

        Args:
            metric_type: Type of metric
            time_range: Time range to analyze
            component: Optional component filter

        Returns:
            Detected pattern or None
        """
        metrics = self.collector.get_metrics(
            metric_type=metric_type,
            time_range=time_range,
            component=component
        )

        if len(metrics) < 24:  # Need at least 24 hours of data
            return None

        # Group by hour of day
        hourly_values: Dict[int, List[float]] = {h: [] for h in range(24)}

        for metric in metrics:
            hour = metric.timestamp.hour
            hourly_values[hour].append(metric.value)

        # Calculate average per hour
        hourly_avg = {
            hour: sum(values) / len(values) if values else 0.0
            for hour, values in hourly_values.items()
        }

        if not any(hourly_avg.values()):
            return None

        # Find peaks and valleys
        max_hour = max(hourly_avg.items(), key=lambda x: x[1])
        min_hour = min(hourly_avg.items(), key=lambda x: x[1])

        peak_value = max_hour[1]
        valley_value = min_hour[1]

        # Find all peak hours (within 80% of max)
        peak_threshold = peak_value * 0.8
        peak_times = [
            f"{hour:02d}:00"
            for hour, avg in hourly_avg.items()
            if avg >= peak_threshold
        ]

        # Find all valley hours (within 120% of min)
        valley_threshold = valley_value * 1.2
        valley_times = [
            f"{hour:02d}:00"
            for hour, avg in hourly_avg.items()
            if avg <= valley_threshold
        ]

        # Calculate pattern strength (coefficient of variation)
        values = list(hourly_avg.values())
        mean_val = sum(values) / len(values)
        if mean_val > 0:
            std_dev = (sum((v - mean_val) ** 2 for v in values) / len(values)) ** 0.5
            cv = std_dev / mean_val
            strength = min(cv, 1.0)  # Cap at 1.0
        else:
            strength = 0.0

        # Determine pattern type
        if time_range in [TimeRange.DAY, TimeRange.HOUR]:
            pattern_type = "hourly"
            frequency = "1h"
        else:
            pattern_type = "daily"
            frequency = "24h"

        # Generate description and recommendations
        description = self._generate_pattern_description(
            pattern_type,
            peak_times,
            valley_times,
            peak_value,
            valley_value,
            metrics[0].unit if metrics else "units"
        )

        recommendations = self._generate_pattern_recommendations(
            pattern_type,
            peak_times,
            valley_times,
            strength
        )

        return UsagePattern(
            pattern_id=f"patt_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            pattern_type=pattern_type,
            frequency=frequency,
            strength=strength,
            peak_times=peak_times,
            valley_times=valley_times,
            peak_value=peak_value,
            valley_value=valley_value,
            component=component,
            description=description,
            recommendations=recommendations
        )

    def compare_periods(
        self,
        metric_type: MetricType,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime,
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare two time periods

        Args:
            metric_type: Type of metric
            period1_start: Period 1 start
            period1_end: Period 1 end
            period2_start: Period 2 start
            period2_end: Period 2 end
            component: Optional component filter

        Returns:
            Comparison results
        """
        # Get metrics for both periods
        metrics1 = self.collector.get_metrics(
            metric_type=metric_type,
            start_time=period1_start,
            end_time=period1_end,
            component=component
        )

        metrics2 = self.collector.get_metrics(
            metric_type=metric_type,
            start_time=period2_start,
            end_time=period2_end,
            component=component
        )

        if not metrics1 or not metrics2:
            return {
                "error": "Insufficient data for comparison"
            }

        values1 = [m.value for m in metrics1]
        values2 = [m.value for m in metrics2]

        avg1 = sum(values1) / len(values1)
        avg2 = sum(values2) / len(values2)

        # Calculate change
        if avg1 > 0:
            percent_change = ((avg2 - avg1) / avg1) * 100
        else:
            percent_change = 0.0

        return {
            "period1": {
                "start": period1_start.isoformat(),
                "end": period1_end.isoformat(),
                "count": len(metrics1),
                "avg": avg1,
                "min": min(values1),
                "max": max(values1),
                "total": sum(values1)
            },
            "period2": {
                "start": period2_start.isoformat(),
                "end": period2_end.isoformat(),
                "count": len(metrics2),
                "avg": avg2,
                "min": min(values2),
                "max": max(values2),
                "total": sum(values2)
            },
            "comparison": {
                "absolute_change": avg2 - avg1,
                "percent_change": percent_change,
                "trend": "up" if avg2 > avg1 else "down" if avg2 < avg1 else "stable"
            }
        }

    def get_insights(
        self,
        time_range: TimeRange = TimeRange.WEEK,
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive insights

        Args:
            time_range: Time range to analyze
            component: Optional component filter

        Returns:
            Insights dictionary
        """
        insights = {
            "timestamp": datetime.utcnow().isoformat(),
            "time_range": time_range.value,
            "component": component,
            "trends": {},
            "patterns": {},
            "recommendations": []
        }

        # Detect trends for key metrics
        for metric_type in [MetricType.COST, MetricType.LATENCY, MetricType.ERROR_RATE]:
            trend = self.detect_trend(metric_type, time_range, component)
            if trend:
                insights["trends"][metric_type.value] = {
                    "direction": trend.direction,
                    "magnitude": trend.magnitude,
                    "velocity": trend.velocity,
                    "confidence": trend.confidence,
                    "description": trend.description
                }

        # Detect patterns
        for metric_type in [MetricType.COST, MetricType.TOKEN_USAGE]:
            pattern = self.detect_pattern(metric_type, time_range, component)
            if pattern:
                insights["patterns"][metric_type.value] = {
                    "pattern_type": pattern.pattern_type,
                    "strength": pattern.strength,
                    "peak_times": pattern.peak_times,
                    "valley_times": pattern.valley_times,
                    "description": pattern.description
                }
                insights["recommendations"].extend(pattern.recommendations)

        return insights

    def _generate_trend_description(
        self,
        direction: str,
        magnitude: float,
        velocity: float,
        unit: str,
        metric_type: MetricType
    ) -> str:
        """Generate human-readable trend description"""
        metric_name = metric_type.value.replace("_", " ").title()

        if direction == "stable":
            return f"{metric_name} is stable with no significant trend"
        elif direction == "up":
            return (
                f"{metric_name} is increasing by {abs(velocity):.2f} {unit}/day "
                f"(total change: {magnitude:.2f} {unit})"
            )
        else:
            return (
                f"{metric_name} is decreasing by {abs(velocity):.2f} {unit}/day "
                f"(total change: {magnitude:.2f} {unit})"
            )

    def _generate_pattern_description(
        self,
        pattern_type: str,
        peak_times: List[str],
        valley_times: List[str],
        peak_value: float,
        valley_value: float,
        unit: str
    ) -> str:
        """Generate human-readable pattern description"""
        peak_str = ", ".join(peak_times[:3])
        valley_str = ", ".join(valley_times[:3])

        return (
            f"{pattern_type.title()} usage pattern detected. "
            f"Peak usage at {peak_str} ({peak_value:.2f} {unit}), "
            f"low usage at {valley_str} ({valley_value:.2f} {unit})"
        )

    def _generate_pattern_recommendations(
        self,
        pattern_type: str,
        peak_times: List[str],
        valley_times: List[str],
        strength: float
    ) -> List[str]:
        """Generate recommendations based on pattern"""
        recommendations = []

        if strength > 0.5:
            recommendations.append(
                f"Strong {pattern_type} pattern detected. "
                "Consider optimizing resource allocation based on usage peaks."
            )

        if peak_times:
            recommendations.append(
                f"Peak usage occurs at {', '.join(peak_times[:3])}. "
                "Ensure adequate resources during these times."
            )

        if valley_times:
            recommendations.append(
                f"Low usage at {', '.join(valley_times[:3])}. "
                "Consider scheduling maintenance or batch jobs during these periods."
            )

        return recommendations
