"""
YAGO v8.0 - Analytics Base Classes
Core abstractions for the analytics system
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class MetricType(str, Enum):
    """Types of metrics that can be collected"""
    COST = "cost"                      # Cost metrics
    LATENCY = "latency"                # Response time metrics
    THROUGHPUT = "throughput"          # Requests per second
    ERROR_RATE = "error_rate"          # Error percentage
    TOKEN_USAGE = "token_usage"        # Token consumption
    MODEL_USAGE = "model_usage"        # Model usage counts
    SUCCESS_RATE = "success_rate"      # Success percentage
    RESOURCE_USAGE = "resource_usage"  # CPU/Memory usage
    QUEUE_SIZE = "queue_size"          # Queue depth
    CUSTOM = "custom"                  # Custom metrics


class TimeRange(str, Enum):
    """Time range options for analytics"""
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"
    QUARTER = "3m"
    YEAR = "1y"
    CUSTOM = "custom"


class AggregationType(str, Enum):
    """Aggregation methods for metrics"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    P95 = "p95"  # 95th percentile
    P99 = "p99"  # 99th percentile


class Metric(BaseModel):
    """
    A single metric data point
    """
    metric_id: str = Field(description="Unique metric identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metric_type: MetricType = Field(description="Type of metric")

    # Metric data
    value: float = Field(description="Metric value")
    unit: str = Field(description="Unit of measurement")

    # Context
    component: Optional[str] = None
    operation: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "metric_id": "metric_abc123",
                "metric_type": "cost",
                "value": 0.0025,
                "unit": "USD",
                "component": "openai_adapter",
                "operation": "generate",
                "labels": {"model": "gpt-4-turbo"}
            }
        }


class Prediction(BaseModel):
    """
    A prediction result
    """
    prediction_id: str = Field(description="Unique prediction identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metric_type: MetricType = Field(description="Type of metric being predicted")

    # Prediction
    predicted_value: float = Field(description="Predicted value")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0-1)")
    prediction_time: datetime = Field(description="Time of prediction")

    # Range
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

    # Context
    model_used: str = Field(description="Prediction model used")
    features_used: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": "pred_abc123",
                "metric_type": "cost",
                "predicted_value": 15.5,
                "confidence": 0.85,
                "prediction_time": "2026-01-15T12:00:00Z",
                "model_used": "linear_regression"
            }
        }


class Anomaly(BaseModel):
    """
    An detected anomaly
    """
    anomaly_id: str = Field(description="Unique anomaly identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metric_type: MetricType = Field(description="Type of metric")

    # Anomaly details
    expected_value: float = Field(description="Expected value")
    actual_value: float = Field(description="Actual value")
    deviation: float = Field(description="Deviation from expected")
    severity: float = Field(ge=0.0, le=1.0, description="Severity score (0-1)")

    # Detection
    detection_method: str = Field(description="Method used to detect")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence")

    # Context
    component: Optional[str] = None
    description: str = Field(description="Human-readable description")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "anomaly_id": "anom_abc123",
                "metric_type": "cost",
                "expected_value": 10.0,
                "actual_value": 50.0,
                "deviation": 40.0,
                "severity": 0.9,
                "detection_method": "statistical",
                "confidence": 0.95,
                "description": "Cost spike detected: 5x higher than expected"
            }
        }


class Forecast(BaseModel):
    """
    A forecast for future values
    """
    forecast_id: str = Field(description="Unique forecast identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metric_type: MetricType = Field(description="Type of metric")

    # Forecast period
    forecast_start: datetime = Field(description="Start of forecast period")
    forecast_end: datetime = Field(description="End of forecast period")

    # Forecast data
    forecasted_values: List[Dict[str, Any]] = Field(
        description="List of forecasted values with timestamps"
    )
    total_forecasted: float = Field(description="Total forecasted value")

    # Confidence
    confidence: float = Field(ge=0.0, le=1.0, description="Forecast confidence")
    confidence_interval: Dict[str, List[float]] = Field(
        default_factory=dict,
        description="Confidence intervals (e.g., 95%)"
    )

    # Model
    model_used: str = Field(description="Forecasting model used")
    accuracy_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "forecast_id": "fcst_abc123",
                "metric_type": "cost",
                "forecast_start": "2026-02-01T00:00:00Z",
                "forecast_end": "2026-02-28T23:59:59Z",
                "total_forecasted": 450.75,
                "confidence": 0.88,
                "model_used": "prophet"
            }
        }


class Trend(BaseModel):
    """
    A detected trend
    """
    trend_id: str = Field(description="Unique trend identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metric_type: MetricType = Field(description="Type of metric")

    # Trend details
    direction: str = Field(description="Trend direction: up, down, stable")
    magnitude: float = Field(description="Magnitude of change")
    velocity: float = Field(description="Rate of change")

    # Time period
    period_start: datetime = Field(description="Start of trend period")
    period_end: datetime = Field(description="End of trend period")

    # Statistics
    slope: float = Field(description="Trend slope")
    correlation: float = Field(ge=-1.0, le=1.0, description="Correlation coefficient")
    confidence: float = Field(ge=0.0, le=1.0, description="Trend confidence")

    # Context
    description: str = Field(description="Human-readable description")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "trend_id": "trend_abc123",
                "metric_type": "cost",
                "direction": "up",
                "magnitude": 25.5,
                "velocity": 2.5,
                "slope": 0.15,
                "correlation": 0.92,
                "confidence": 0.95,
                "description": "Cost increasing by 2.5 USD/day"
            }
        }


class UsagePattern(BaseModel):
    """
    A detected usage pattern
    """
    pattern_id: str = Field(description="Unique pattern identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Pattern details
    pattern_type: str = Field(description="Type of pattern: daily, weekly, monthly, seasonal")
    frequency: str = Field(description="Pattern frequency")
    strength: float = Field(ge=0.0, le=1.0, description="Pattern strength")

    # Peaks and valleys
    peak_times: List[str] = Field(default_factory=list)
    valley_times: List[str] = Field(default_factory=list)
    peak_value: float = Field(description="Peak usage value")
    valley_value: float = Field(description="Valley usage value")

    # Context
    component: Optional[str] = None
    description: str = Field(description="Human-readable description")
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "pattern_id": "patt_abc123",
                "pattern_type": "daily",
                "frequency": "24h",
                "strength": 0.87,
                "peak_times": ["14:00", "15:00", "16:00"],
                "valley_times": ["02:00", "03:00", "04:00"],
                "peak_value": 150.0,
                "valley_value": 10.0,
                "description": "Daily peak usage during business hours"
            }
        }


class AnalyticsConfig(BaseModel):
    """
    Configuration for analytics system
    """
    # Collection
    collection_interval_seconds: float = Field(default=60.0, gt=0)
    retention_days: int = Field(default=90, gt=0)

    # Analysis
    anomaly_detection_enabled: bool = Field(default=True)
    anomaly_threshold: float = Field(default=2.0, gt=0)  # Standard deviations
    trend_analysis_enabled: bool = Field(default=True)
    pattern_detection_enabled: bool = Field(default=True)

    # Forecasting
    forecast_horizon_days: int = Field(default=30, gt=0)
    forecast_update_interval_hours: int = Field(default=24, gt=0)

    # Alerts
    alert_on_anomalies: bool = Field(default=True)
    alert_threshold_severity: float = Field(default=0.7, ge=0.0, le=1.0)


class AnalyticsSummary(BaseModel):
    """
    Summary of analytics data
    """
    summary_id: str = Field(description="Unique summary identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Time period
    period_start: datetime
    period_end: datetime

    # Metrics summary
    total_metrics_collected: int = Field(default=0)
    metrics_by_type: Dict[str, int] = Field(default_factory=dict)

    # Key insights
    total_cost: float = Field(default=0.0)
    avg_latency_ms: float = Field(default=0.0)
    error_rate: float = Field(default=0.0)
    success_rate: float = Field(default=0.0)

    # Trends
    cost_trend: str = Field(default="stable")  # up, down, stable
    performance_trend: str = Field(default="stable")

    # Anomalies
    anomalies_detected: int = Field(default=0)
    critical_anomalies: int = Field(default=0)

    # Forecasts
    forecasted_cost_next_month: Optional[float] = None
    forecasted_usage_next_month: Optional[float] = None

    # Recommendations
    recommendations: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "summary_id": "sum_abc123",
                "total_cost": 1250.75,
                "avg_latency_ms": 285.5,
                "error_rate": 0.02,
                "success_rate": 0.98,
                "cost_trend": "up",
                "anomalies_detected": 5,
                "forecasted_cost_next_month": 1450.0
            }
        }
