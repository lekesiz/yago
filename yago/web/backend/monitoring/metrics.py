"""
YAGO v7.2 - Prometheus Metrics
Collect and expose application metrics for monitoring
"""

from fastapi import APIRouter, Response
from typing import Dict, Any
import time
import psutil
import os
from datetime import datetime

router = APIRouter(prefix="/api/v1/metrics", tags=["Monitoring"])

# Global metrics storage
_metrics: Dict[str, Any] = {
    "requests_total": 0,
    "requests_success": 0,
    "requests_error": 0,
    "response_time_sum": 0.0,
    "response_time_count": 0,
    "active_sessions": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "db_queries_total": 0,
    "db_queries_slow": 0,
    "websocket_connections": 0,
    "agents_active": 0,
    "projects_total": 0,
    "cost_total": 0.0,
    "api_calls_total": 0,
    "errors_by_type": {},
    "requests_by_endpoint": {},
    "requests_by_method": {},
    "start_time": time.time(),
}


def increment_metric(name: str, value: float = 1.0):
    """Increment a metric by value"""
    if name in _metrics:
        _metrics[name] += value


def set_metric(name: str, value: Any):
    """Set a metric to a specific value"""
    _metrics[name] = value


def record_request(endpoint: str, method: str, duration: float, success: bool):
    """Record API request metrics"""
    _metrics["requests_total"] += 1

    if success:
        _metrics["requests_success"] += 1
    else:
        _metrics["requests_error"] += 1

    _metrics["response_time_sum"] += duration
    _metrics["response_time_count"] += 1

    # Track by endpoint
    if endpoint not in _metrics["requests_by_endpoint"]:
        _metrics["requests_by_endpoint"][endpoint] = 0
    _metrics["requests_by_endpoint"][endpoint] += 1

    # Track by method
    if method not in _metrics["requests_by_method"]:
        _metrics["requests_by_method"][method] = 0
    _metrics["requests_by_method"][method] += 1


def record_error(error_type: str):
    """Record error metrics"""
    if error_type not in _metrics["errors_by_type"]:
        _metrics["errors_by_type"][error_type] = 0
    _metrics["errors_by_type"][error_type] += 1


def get_system_metrics() -> Dict[str, Any]:
    """Get system resource metrics"""
    try:
        process = psutil.Process(os.getpid())

        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(),
            "memory_used_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
            "memory_total_mb": psutil.virtual_memory().total / 1024 / 1024,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "disk_free_gb": psutil.disk_usage('/').free / 1024 / 1024 / 1024,
            "network_sent_mb": psutil.net_io_counters().bytes_sent / 1024 / 1024,
            "network_recv_mb": psutil.net_io_counters().bytes_recv / 1024 / 1024,
            "open_files": len(process.open_files()),
            "threads": process.num_threads(),
        }
    except Exception as e:
        return {"error": str(e)}


def get_application_metrics() -> Dict[str, Any]:
    """Get application-specific metrics"""
    uptime = time.time() - _metrics["start_time"]
    avg_response_time = (
        _metrics["response_time_sum"] / _metrics["response_time_count"]
        if _metrics["response_time_count"] > 0
        else 0
    )

    return {
        "uptime_seconds": uptime,
        "requests_total": _metrics["requests_total"],
        "requests_success": _metrics["requests_success"],
        "requests_error": _metrics["requests_error"],
        "error_rate": (
            _metrics["requests_error"] / _metrics["requests_total"]
            if _metrics["requests_total"] > 0
            else 0
        ),
        "avg_response_time_ms": avg_response_time * 1000,
        "requests_per_second": (
            _metrics["requests_total"] / uptime
            if uptime > 0
            else 0
        ),
        "active_sessions": _metrics["active_sessions"],
        "cache_hit_rate": (
            _metrics["cache_hits"] / (_metrics["cache_hits"] + _metrics["cache_misses"])
            if (_metrics["cache_hits"] + _metrics["cache_misses"]) > 0
            else 0
        ),
        "db_queries_total": _metrics["db_queries_total"],
        "db_queries_slow": _metrics["db_queries_slow"],
        "websocket_connections": _metrics["websocket_connections"],
        "agents_active": _metrics["agents_active"],
        "projects_total": _metrics["projects_total"],
        "cost_total": _metrics["cost_total"],
        "api_calls_total": _metrics["api_calls_total"],
    }


def format_prometheus_metrics() -> str:
    """Format metrics in Prometheus exposition format"""
    lines = []

    # Get all metrics
    system = get_system_metrics()
    app = get_application_metrics()

    # System metrics
    lines.append("# HELP yago_cpu_percent CPU usage percentage")
    lines.append("# TYPE yago_cpu_percent gauge")
    lines.append(f"yago_cpu_percent {system.get('cpu_percent', 0)}")

    lines.append("# HELP yago_memory_used_mb Memory used in MB")
    lines.append("# TYPE yago_memory_used_mb gauge")
    lines.append(f"yago_memory_used_mb {system.get('memory_used_mb', 0)}")

    lines.append("# HELP yago_memory_percent Memory usage percentage")
    lines.append("# TYPE yago_memory_percent gauge")
    lines.append(f"yago_memory_percent {system.get('memory_percent', 0)}")

    # Application metrics
    lines.append("# HELP yago_uptime_seconds Application uptime in seconds")
    lines.append("# TYPE yago_uptime_seconds counter")
    lines.append(f"yago_uptime_seconds {app['uptime_seconds']}")

    lines.append("# HELP yago_requests_total Total number of requests")
    lines.append("# TYPE yago_requests_total counter")
    lines.append(f"yago_requests_total {app['requests_total']}")

    lines.append("# HELP yago_requests_success Successful requests")
    lines.append("# TYPE yago_requests_success counter")
    lines.append(f"yago_requests_success {app['requests_success']}")

    lines.append("# HELP yago_requests_error Failed requests")
    lines.append("# TYPE yago_requests_error counter")
    lines.append(f"yago_requests_error {app['requests_error']}")

    lines.append("# HELP yago_error_rate Error rate (0-1)")
    lines.append("# TYPE yago_error_rate gauge")
    lines.append(f"yago_error_rate {app['error_rate']}")

    lines.append("# HELP yago_avg_response_time_ms Average response time in milliseconds")
    lines.append("# TYPE yago_avg_response_time_ms gauge")
    lines.append(f"yago_avg_response_time_ms {app['avg_response_time_ms']}")

    lines.append("# HELP yago_requests_per_second Requests per second")
    lines.append("# TYPE yago_requests_per_second gauge")
    lines.append(f"yago_requests_per_second {app['requests_per_second']}")

    lines.append("# HELP yago_active_sessions Active user sessions")
    lines.append("# TYPE yago_active_sessions gauge")
    lines.append(f"yago_active_sessions {app['active_sessions']}")

    lines.append("# HELP yago_websocket_connections Active WebSocket connections")
    lines.append("# TYPE yago_websocket_connections gauge")
    lines.append(f"yago_websocket_connections {app['websocket_connections']}")

    lines.append("# HELP yago_cost_total Total cost in USD")
    lines.append("# TYPE yago_cost_total counter")
    lines.append(f"yago_cost_total {app['cost_total']}")

    # Requests by endpoint
    for endpoint, count in _metrics["requests_by_endpoint"].items():
        safe_endpoint = endpoint.replace('/', '_').replace('{', '').replace('}', '')
        lines.append(f'yago_requests_by_endpoint{{endpoint="{endpoint}"}} {count}')

    # Errors by type
    for error_type, count in _metrics["errors_by_type"].items():
        lines.append(f'yago_errors_by_type{{type="{error_type}"}} {count}')

    return "\n".join(lines) + "\n"


@router.get("/prometheus")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    metrics_text = format_prometheus_metrics()
    return Response(content=metrics_text, media_type="text/plain")


@router.get("")
async def get_metrics():
    """Get all metrics in JSON format"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": get_system_metrics(),
        "application": get_application_metrics(),
        "requests_by_endpoint": _metrics["requests_by_endpoint"],
        "requests_by_method": _metrics["requests_by_method"],
        "errors_by_type": _metrics["errors_by_type"],
    }


@router.post("/reset")
async def reset_metrics():
    """Reset all metrics (for testing)"""
    global _metrics
    _metrics = {
        "requests_total": 0,
        "requests_success": 0,
        "requests_error": 0,
        "response_time_sum": 0.0,
        "response_time_count": 0,
        "active_sessions": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "db_queries_total": 0,
        "db_queries_slow": 0,
        "websocket_connections": 0,
        "agents_active": 0,
        "projects_total": 0,
        "cost_total": 0.0,
        "api_calls_total": 0,
        "errors_by_type": {},
        "requests_by_endpoint": {},
        "requests_by_method": {},
        "start_time": time.time(),
    }
    return {"message": "Metrics reset successfully"}


# Export for use in other modules
metrics_router = router
