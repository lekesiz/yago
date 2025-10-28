"""
YAGO v8.0 - Analytics API
RESTful API for advanced analytics
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from yago.analytics import (
    MetricsCollector,
    MetricsAnalyzer,
    PerformancePredictor,
    CostForecaster,
    AnomalyDetector,
    MetricType,
    TimeRange,
    AggregationType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

# Initialize components
collector = MetricsCollector()
analyzer = MetricsAnalyzer(collector)
predictor = PerformancePredictor(collector)
forecaster = CostForecaster(collector)
detector = AnomalyDetector(collector)


# Request Models

class MetricRecordRequest(BaseModel):
    """Request to record a metric"""
    metric_type: str
    value: float
    unit: str
    component: Optional[str] = None
    operation: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ForecastRequest(BaseModel):
    """Request for forecast"""
    days_ahead: int = 30
    component: Optional[str] = None


class BudgetRequest(BaseModel):
    """Request for budget impact analysis"""
    monthly_budget: float
    component: Optional[str] = None


# Endpoints

@router.post("/metrics/record")
async def record_metric(request: MetricRecordRequest):
    """
    Record a metric

    Args:
        request: Metric recording request

    Returns:
        Recorded metric
    """
    try:
        metric_type = MetricType(request.metric_type)

        metric = collector.record_metric(
            metric_type=metric_type,
            value=request.value,
            unit=request.unit,
            component=request.component,
            operation=request.operation,
            labels=request.labels,
            **(request.metadata or {})
        )

        return {
            "metric_id": metric.metric_id,
            "metric_type": metric.metric_type.value,
            "value": metric.value,
            "unit": metric.unit,
            "timestamp": metric.timestamp.isoformat(),
            "message": "Metric recorded successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metric type: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error recording metric: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record metric"
        )


@router.get("/metrics/{metric_type}")
async def get_metrics(
    metric_type: str,
    time_range: Optional[str] = "1d",
    component: Optional[str] = None,
    limit: Optional[int] = 100
):
    """
    Get metrics

    Args:
        metric_type: Type of metric
        time_range: Time range (1h, 1d, 1w, 1m)
        component: Optional component filter
        limit: Maximum number of metrics

    Returns:
        List of metrics
    """
    try:
        mt = MetricType(metric_type)
        tr = TimeRange(time_range) if time_range else None

        metrics = collector.get_metrics(
            metric_type=mt,
            time_range=tr,
            component=component,
            limit=limit
        )

        return {
            "metric_type": metric_type,
            "time_range": time_range,
            "component": component,
            "count": len(metrics),
            "metrics": [
                {
                    "metric_id": m.metric_id,
                    "timestamp": m.timestamp.isoformat(),
                    "value": m.value,
                    "unit": m.unit,
                    "component": m.component,
                    "operation": m.operation,
                    "labels": m.labels
                }
                for m in metrics
            ]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics"
        )


@router.get("/metrics/{metric_type}/aggregate")
async def aggregate_metrics(
    metric_type: str,
    aggregation: str = "avg",
    time_range: Optional[str] = "1d",
    component: Optional[str] = None
):
    """
    Aggregate metrics

    Args:
        metric_type: Type of metric
        aggregation: Aggregation method (sum, avg, min, max, count, median, p95, p99)
        time_range: Time range
        component: Optional component filter

    Returns:
        Aggregated value
    """
    try:
        mt = MetricType(metric_type)
        agg = AggregationType(aggregation)
        tr = TimeRange(time_range) if time_range else None

        value = collector.aggregate_metrics(
            metric_type=mt,
            aggregation=agg,
            time_range=tr,
            component=component
        )

        return {
            "metric_type": metric_type,
            "aggregation": aggregation,
            "time_range": time_range,
            "component": component,
            "value": value
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error aggregating metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to aggregate metrics"
        )


@router.get("/metrics/{metric_type}/timeseries")
async def get_time_series(
    metric_type: str,
    time_range: str = "1d",
    interval_minutes: int = 60,
    aggregation: str = "avg",
    component: Optional[str] = None
):
    """
    Get time series data

    Args:
        metric_type: Type of metric
        time_range: Time range
        interval_minutes: Interval for bucketing
        aggregation: Aggregation method
        component: Optional component filter

    Returns:
        Time series data
    """
    try:
        mt = MetricType(metric_type)
        tr = TimeRange(time_range)
        agg = AggregationType(aggregation)

        time_series = collector.get_time_series(
            metric_type=mt,
            time_range=tr,
            interval_minutes=interval_minutes,
            aggregation=agg,
            component=component
        )

        return {
            "metric_type": metric_type,
            "time_range": time_range,
            "interval_minutes": interval_minutes,
            "aggregation": aggregation,
            "component": component,
            "data_points": len(time_series),
            "time_series": time_series
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting time series: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get time series"
        )


@router.get("/metrics/{metric_type}/statistics")
async def get_statistics(
    metric_type: str,
    time_range: Optional[str] = "1d",
    component: Optional[str] = None
):
    """
    Get statistics for a metric

    Args:
        metric_type: Type of metric
        time_range: Time range
        component: Optional component filter

    Returns:
        Statistics
    """
    try:
        mt = MetricType(metric_type)
        tr = TimeRange(time_range) if time_range else None

        stats = collector.get_statistics(
            metric_type=mt,
            time_range=tr,
            component=component
        )

        return {
            "metric_type": metric_type,
            "time_range": time_range,
            "component": component,
            "statistics": stats
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )


@router.get("/trends/{metric_type}")
async def detect_trend(
    metric_type: str,
    time_range: str = "1w",
    component: Optional[str] = None
):
    """
    Detect trend in metric

    Args:
        metric_type: Type of metric
        time_range: Time range to analyze
        component: Optional component filter

    Returns:
        Detected trend
    """
    try:
        mt = MetricType(metric_type)
        tr = TimeRange(time_range)

        trend = analyzer.detect_trend(
            metric_type=mt,
            time_range=tr,
            component=component
        )

        if not trend:
            return {
                "message": "Insufficient data for trend detection"
            }

        return {
            "trend_id": trend.trend_id,
            "metric_type": trend.metric_type.value,
            "direction": trend.direction,
            "magnitude": trend.magnitude,
            "velocity": trend.velocity,
            "slope": trend.slope,
            "correlation": trend.correlation,
            "confidence": trend.confidence,
            "description": trend.description,
            "period_start": trend.period_start.isoformat(),
            "period_end": trend.period_end.isoformat()
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error detecting trend: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect trend"
        )


@router.get("/patterns/{metric_type}")
async def detect_pattern(
    metric_type: str,
    time_range: str = "1w",
    component: Optional[str] = None
):
    """
    Detect usage pattern

    Args:
        metric_type: Type of metric
        time_range: Time range to analyze
        component: Optional component filter

    Returns:
        Detected pattern
    """
    try:
        mt = MetricType(metric_type)
        tr = TimeRange(time_range)

        pattern = analyzer.detect_pattern(
            metric_type=mt,
            time_range=tr,
            component=component
        )

        if not pattern:
            return {
                "message": "Insufficient data for pattern detection"
            }

        return {
            "pattern_id": pattern.pattern_id,
            "pattern_type": pattern.pattern_type,
            "frequency": pattern.frequency,
            "strength": pattern.strength,
            "peak_times": pattern.peak_times,
            "valley_times": pattern.valley_times,
            "peak_value": pattern.peak_value,
            "valley_value": pattern.valley_value,
            "description": pattern.description,
            "recommendations": pattern.recommendations
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error detecting pattern: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect pattern"
        )


@router.get("/insights")
async def get_insights(
    time_range: str = "1w",
    component: Optional[str] = None
):
    """
    Get comprehensive insights

    Args:
        time_range: Time range to analyze
        component: Optional component filter

    Returns:
        Insights
    """
    try:
        tr = TimeRange(time_range)

        insights = analyzer.get_insights(
            time_range=tr,
            component=component
        )

        return insights

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get insights"
        )


@router.post("/predictions/latency")
async def predict_latency(hours_ahead: int = 1, component: Optional[str] = None):
    """Predict latency"""
    try:
        prediction = predictor.predict_latency(hours_ahead, component)

        if not prediction:
            return {"message": "Insufficient data for prediction"}

        return {
            "prediction_id": prediction.prediction_id,
            "metric_type": prediction.metric_type.value,
            "predicted_value": prediction.predicted_value,
            "confidence": prediction.confidence,
            "prediction_time": prediction.prediction_time.isoformat(),
            "lower_bound": prediction.lower_bound,
            "upper_bound": prediction.upper_bound,
            "model_used": prediction.model_used
        }

    except Exception as e:
        logger.error(f"Error predicting latency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to predict latency"
        )


@router.post("/predictions/error-rate")
async def predict_error_rate(hours_ahead: int = 1, component: Optional[str] = None):
    """Predict error rate"""
    try:
        prediction = predictor.predict_error_rate(hours_ahead, component)

        if not prediction:
            return {"message": "Insufficient data for prediction"}

        return {
            "prediction_id": prediction.prediction_id,
            "predicted_value": prediction.predicted_value,
            "confidence": prediction.confidence,
            "prediction_time": prediction.prediction_time.isoformat()
        }

    except Exception as e:
        logger.error(f"Error predicting error rate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to predict error rate"
        )


@router.get("/predictions/performance-issues")
async def detect_performance_issues(
    time_range: str = "1h",
    component: Optional[str] = None
):
    """Detect performance issues"""
    try:
        tr = TimeRange(time_range)
        issues = predictor.detect_performance_issues(tr, component)

        return {
            "time_range": time_range,
            "component": component,
            "issues_count": len(issues),
            "issues": issues
        }

    except Exception as e:
        logger.error(f"Error detecting performance issues: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect performance issues"
        )


@router.post("/forecast/cost")
async def forecast_cost(request: ForecastRequest):
    """Forecast cost"""
    try:
        forecast = forecaster.forecast_daily_cost(
            days_ahead=request.days_ahead,
            component=request.component
        )

        if not forecast:
            return {"message": "Insufficient data for forecast"}

        return {
            "forecast_id": forecast.forecast_id,
            "metric_type": forecast.metric_type.value,
            "total_forecasted": forecast.total_forecasted,
            "confidence": forecast.confidence,
            "forecast_start": forecast.forecast_start.isoformat(),
            "forecast_end": forecast.forecast_end.isoformat(),
            "forecasted_values": forecast.forecasted_values[:30],  # Limit to 30 days
            "model_used": forecast.model_used
        }

    except Exception as e:
        logger.error(f"Error forecasting cost: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to forecast cost"
        )


@router.post("/forecast/tokens")
async def forecast_tokens(request: ForecastRequest):
    """Forecast token usage"""
    try:
        forecast = forecaster.forecast_token_usage(
            days_ahead=request.days_ahead,
            component=request.component
        )

        if not forecast:
            return {"message": "Insufficient data for forecast"}

        return {
            "forecast_id": forecast.forecast_id,
            "total_forecasted": forecast.total_forecasted,
            "confidence": forecast.confidence,
            "forecasted_values": forecast.forecasted_values[:30]
        }

    except Exception as e:
        logger.error(f"Error forecasting tokens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to forecast tokens"
        )


@router.post("/budget/impact")
async def estimate_budget_impact(request: BudgetRequest):
    """Estimate budget impact"""
    try:
        impact = forecaster.estimate_budget_impact(
            monthly_budget=request.monthly_budget,
            component=request.component
        )

        return impact

    except Exception as e:
        logger.error(f"Error estimating budget impact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to estimate budget impact"
        )


@router.get("/cost/breakdown")
async def get_cost_breakdown(
    time_range: str = "1m",
    group_by: str = "component"
):
    """Get cost breakdown"""
    try:
        tr = TimeRange(time_range)
        breakdown = forecaster.get_cost_breakdown(tr, group_by)

        return breakdown

    except Exception as e:
        logger.error(f"Error getting cost breakdown: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get cost breakdown"
        )


@router.get("/anomalies/{metric_type}")
async def detect_anomalies(
    metric_type: str,
    time_range: str = "1d",
    component: Optional[str] = None,
    method: str = "statistical"
):
    """Detect anomalies"""
    try:
        mt = MetricType(metric_type)
        tr = TimeRange(time_range)

        anomalies = detector.detect_anomalies(mt, tr, component, method)

        return {
            "metric_type": metric_type,
            "time_range": time_range,
            "detection_method": method,
            "anomalies_count": len(anomalies),
            "anomalies": [
                {
                    "anomaly_id": a.anomaly_id,
                    "timestamp": a.timestamp.isoformat(),
                    "expected_value": a.expected_value,
                    "actual_value": a.actual_value,
                    "deviation": a.deviation,
                    "severity": a.severity,
                    "confidence": a.confidence,
                    "description": a.description
                }
                for a in anomalies
            ]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect anomalies"
        )


@router.get("/anomalies/summary")
async def get_anomaly_summary(
    time_range: str = "1d",
    component: Optional[str] = None
):
    """Get anomaly summary"""
    try:
        tr = TimeRange(time_range)
        summary = detector.get_anomaly_summary(tr, component)

        return summary

    except Exception as e:
        logger.error(f"Error getting anomaly summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get anomaly summary"
        )


@router.get("/collector/summary")
async def get_collector_summary():
    """Get collector summary"""
    try:
        summary = collector.get_summary()
        return summary

    except Exception as e:
        logger.error(f"Error getting collector summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get collector summary"
        )


@router.get("/collector/components")
async def get_components():
    """Get list of components"""
    try:
        components = collector.get_components()
        return {
            "count": len(components),
            "components": components
        }

    except Exception as e:
        logger.error(f"Error getting components: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get components"
        )


# Export router
analytics_router = router
