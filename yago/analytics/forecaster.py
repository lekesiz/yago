"""
YAGO v8.0 - Cost Forecaster
Forecast future costs based on usage patterns
"""

import logging
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from .base import (
    MetricType,
    TimeRange,
    Forecast,
)
from .collector import MetricsCollector

logger = logging.getLogger(__name__)


class CostForecaster:
    """
    Forecast future costs based on historical usage
    """

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def forecast_daily_cost(
        self,
        days_ahead: int = 30,
        component: Optional[str] = None
    ) -> Optional[Forecast]:
        """
        Forecast daily costs

        Args:
            days_ahead: Number of days to forecast
            component: Optional component filter

        Returns:
            Cost forecast or None
        """
        return self._forecast_metric(
            metric_type=MetricType.COST,
            days_ahead=days_ahead,
            component=component,
            aggregation_unit="day"
        )

    def forecast_monthly_cost(
        self,
        months_ahead: int = 3,
        component: Optional[str] = None
    ) -> Optional[Forecast]:
        """
        Forecast monthly costs

        Args:
            months_ahead: Number of months to forecast
            component: Optional component filter

        Returns:
            Cost forecast or None
        """
        days = months_ahead * 30
        return self._forecast_metric(
            metric_type=MetricType.COST,
            days_ahead=days,
            component=component,
            aggregation_unit="month"
        )

    def forecast_token_usage(
        self,
        days_ahead: int = 30,
        component: Optional[str] = None
    ) -> Optional[Forecast]:
        """
        Forecast token usage

        Args:
            days_ahead: Number of days to forecast
            component: Optional component filter

        Returns:
            Token usage forecast or None
        """
        return self._forecast_metric(
            metric_type=MetricType.TOKEN_USAGE,
            days_ahead=days_ahead,
            component=component,
            aggregation_unit="day"
        )

    def estimate_budget_impact(
        self,
        monthly_budget: float,
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate budget impact based on current usage

        Args:
            monthly_budget: Monthly budget in USD
            component: Optional component filter

        Returns:
            Budget impact analysis
        """
        # Get cost metrics for last 7 days
        metrics = self.collector.get_metrics(
            metric_type=MetricType.COST,
            time_range=TimeRange.WEEK,
            component=component
        )

        if not metrics:
            return {
                "error": "No cost data available"
            }

        # Calculate daily average
        total_cost = sum(m.value for m in metrics)
        days = 7
        daily_avg = total_cost / days

        # Project monthly cost
        projected_monthly = daily_avg * 30

        # Calculate budget utilization
        utilization = (projected_monthly / monthly_budget) * 100 if monthly_budget > 0 else 0
        remaining_budget = monthly_budget - projected_monthly

        # Determine status
        if utilization >= 100:
            status = "over_budget"
            severity = "critical"
        elif utilization >= 90:
            status = "approaching_limit"
            severity = "high"
        elif utilization >= 75:
            status = "high_usage"
            severity = "medium"
        else:
            status = "on_track"
            severity = "low"

        # Days until budget exhausted
        if daily_avg > 0 and remaining_budget > 0:
            days_remaining = remaining_budget / daily_avg
        else:
            days_remaining = 0

        return {
            "monthly_budget": monthly_budget,
            "current_usage": {
                "daily_average": daily_avg,
                "weekly_total": total_cost,
                "projected_monthly": projected_monthly
            },
            "budget_status": {
                "utilization_percent": utilization,
                "remaining_budget": remaining_budget,
                "days_until_exhausted": days_remaining,
                "status": status,
                "severity": severity
            },
            "recommendations": self._generate_budget_recommendations(
                utilization,
                status,
                daily_avg,
                monthly_budget
            )
        }

    def get_cost_breakdown(
        self,
        time_range: TimeRange = TimeRange.MONTH,
        group_by: str = "component"
    ) -> Dict[str, Any]:
        """
        Get cost breakdown by component or model

        Args:
            time_range: Time range to analyze
            group_by: Group by 'component' or 'model'

        Returns:
            Cost breakdown
        """
        metrics = self.collector.get_metrics(
            metric_type=MetricType.COST,
            time_range=time_range
        )

        if not metrics:
            return {
                "total_cost": 0.0,
                "breakdown": {},
                "top_costs": []
            }

        # Group costs
        breakdown: Dict[str, float] = {}

        for metric in metrics:
            if group_by == "component":
                key = metric.component or "unknown"
            elif group_by == "model":
                key = metric.labels.get("model", "unknown")
            else:
                key = "total"

            breakdown[key] = breakdown.get(key, 0.0) + metric.value

        # Calculate total
        total_cost = sum(breakdown.values())

        # Get top costs
        top_costs = sorted(
            [
                {
                    "name": name,
                    "cost": cost,
                    "percentage": (cost / total_cost * 100) if total_cost > 0 else 0
                }
                for name, cost in breakdown.items()
            ],
            key=lambda x: x["cost"],
            reverse=True
        )

        return {
            "total_cost": total_cost,
            "time_range": time_range.value,
            "group_by": group_by,
            "breakdown": breakdown,
            "top_costs": top_costs[:10]  # Top 10
        }

    def _forecast_metric(
        self,
        metric_type: MetricType,
        days_ahead: int,
        component: Optional[str],
        aggregation_unit: str
    ) -> Optional[Forecast]:
        """
        Generic forecasting method

        Args:
            metric_type: Type of metric to forecast
            days_ahead: Days ahead to forecast
            component: Optional component filter
            aggregation_unit: 'day' or 'month'

        Returns:
            Forecast or None
        """
        # Get historical data (last 30 days)
        metrics = self.collector.get_metrics(
            metric_type=metric_type,
            time_range=TimeRange.MONTH,
            component=component
        )

        if len(metrics) < 7:  # Need at least a week of data
            logger.warning(
                f"Insufficient data for forecast: {len(metrics)} metrics "
                f"(need at least 7)"
            )
            return None

        # Calculate daily averages
        daily_values = self._aggregate_by_day(metrics)

        if not daily_values:
            return None

        # Apply forecasting model (simple linear trend for now)
        forecasted_values = self._forecast_linear_trend(
            list(daily_values.values()),
            days_ahead
        )

        # Calculate total
        total_forecasted = sum(forecasted_values)

        # Calculate confidence (decreases with forecast horizon)
        base_confidence = 0.85
        horizon_penalty = min(days_ahead / 90, 0.3)  # Max 30% penalty
        confidence = base_confidence - horizon_penalty

        # Create forecast data points
        forecast_start = datetime.utcnow() + timedelta(days=1)
        forecast_data = []

        for i, value in enumerate(forecasted_values):
            timestamp = forecast_start + timedelta(days=i)
            forecast_data.append({
                "timestamp": timestamp.isoformat(),
                "value": value,
                "day": i + 1
            })

        # Calculate confidence intervals (±15%)
        confidence_interval = {
            "95%": [
                [data["timestamp"], data["value"] * 0.85, data["value"] * 1.15]
                for data in forecast_data
            ]
        }

        forecast_end = forecast_start + timedelta(days=days_ahead)

        return Forecast(
            forecast_id=f"fcst_{uuid.uuid4().hex[:12]}",
            created_at=datetime.utcnow(),
            metric_type=metric_type,
            forecast_start=forecast_start,
            forecast_end=forecast_end,
            forecasted_values=forecast_data,
            total_forecasted=total_forecasted,
            confidence=confidence,
            confidence_interval=confidence_interval,
            model_used="linear_trend",
            metadata={
                "days_ahead": days_ahead,
                "aggregation_unit": aggregation_unit,
                "component": component,
                "historical_days": len(daily_values)
            }
        )

    def _aggregate_by_day(
        self,
        metrics: List
    ) -> Dict[str, float]:
        """Aggregate metrics by day"""
        daily_values: Dict[str, float] = {}

        for metric in metrics:
            date_key = metric.timestamp.strftime("%Y-%m-%d")
            daily_values[date_key] = daily_values.get(date_key, 0.0) + metric.value

        return daily_values

    def _forecast_linear_trend(
        self,
        historical_values: List[float],
        days_ahead: int
    ) -> List[float]:
        """
        Forecast using linear trend

        Args:
            historical_values: Historical daily values
            days_ahead: Days to forecast

        Returns:
            List of forecasted values
        """
        n = len(historical_values)
        x = list(range(n))

        # Linear regression
        sum_x = sum(x)
        sum_y = sum(historical_values)
        sum_xy = sum(i * v for i, v in enumerate(historical_values))
        sum_x2 = sum(i * i for i in x)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            # Use average if no trend
            avg = sum_y / n
            return [avg] * days_ahead

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # Forecast
        forecasted = []
        for i in range(days_ahead):
            value = slope * (n + i) + intercept
            value = max(0, value)  # Can't be negative
            forecasted.append(value)

        return forecasted

    def _generate_budget_recommendations(
        self,
        utilization: float,
        status: str,
        daily_avg: float,
        monthly_budget: float
    ) -> List[str]:
        """Generate budget recommendations"""
        recommendations = []

        if status == "over_budget":
            recommendations.append(
                f"⚠️  CRITICAL: Projected to exceed budget by "
                f"${daily_avg * 30 - monthly_budget:.2f}. "
                "Immediate cost optimization required."
            )
            recommendations.append(
                "Consider switching to cheaper models for non-critical tasks."
            )
            recommendations.append(
                "Implement rate limiting or usage caps."
            )

        elif status == "approaching_limit":
            recommendations.append(
                f"⚠️  WARNING: At {utilization:.0f}% of monthly budget. "
                "Monitor usage closely."
            )
            recommendations.append(
                "Review cost breakdown to identify optimization opportunities."
            )

        elif status == "high_usage":
            recommendations.append(
                f"Using {utilization:.0f}% of budget. Within limits but monitor trends."
            )

        else:
            recommendations.append(
                f"✓ On track: Using {utilization:.0f}% of monthly budget."
            )

        # Add general recommendations
        recommendations.append(
            "Set up alerts for cost anomalies to catch unexpected spikes."
        )

        return recommendations
