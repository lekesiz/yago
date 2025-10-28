"""
YAGO v8.0 - Auto-Healing API
RESTful API for auto-healing system management
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

from yago.healing import (
    HealthMonitor,
    ErrorDetector,
    RecoveryEngine,
    HealthStatus,
    ErrorSeverity,
    ErrorCategory,
    CircuitBreakerConfig,
    RetryConfig,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/healing", tags=["Auto-Healing"])

# Initialize components
health_monitor = HealthMonitor()
error_detector = ErrorDetector()
recovery_engine = RecoveryEngine(health_monitor, error_detector)


# Request/Response Models

class ComponentRegisterRequest(BaseModel):
    """Request to register a component"""
    component: str
    enable_circuit_breaker: bool = False
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None


class HealthCheckRequest(BaseModel):
    """Request to check component health"""
    component: Optional[str] = None


class RecoveryStatsRequest(BaseModel):
    """Request for recovery statistics"""
    component: Optional[str] = None


class CircuitBreakerResetRequest(BaseModel):
    """Request to reset circuit breaker"""
    component: str


class MonitoringConfigRequest(BaseModel):
    """Request to update monitoring config"""
    check_interval_seconds: float = 30.0
    alert_threshold: str = "unhealthy"


# Endpoints

@router.get("/health")
async def check_health(component: Optional[str] = None):
    """
    Check system or component health

    Args:
        component: Optional component name to check

    Returns:
        Health check results
    """
    try:
        if component:
            # Check specific component
            result = await health_monitor.check_component_health(component)
            return {
                "component": result.component,
                "status": result.status.value,
                "response_time_ms": result.response_time_ms,
                "error_rate": result.error_rate,
                "success_rate": result.success_rate,
                "message": result.message,
                "issues": result.issues,
                "details": result.details,
                "timestamp": result.timestamp.isoformat()
            }
        else:
            # Check system health
            result = await health_monitor.get_system_health()
            return {
                "system_status": result.status.value,
                "error_rate": result.error_rate,
                "success_rate": result.success_rate,
                "message": result.message,
                "issues": result.issues,
                "details": result.details,
                "timestamp": result.timestamp.isoformat()
            }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error checking health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check health"
        )


@router.get("/health/components")
async def check_all_components():
    """
    Check health of all registered components

    Returns:
        Health status for all components
    """
    try:
        results = await health_monitor.check_all_health()

        return {
            "total_components": len(results),
            "components": {
                component: {
                    "status": result.status.value,
                    "error_rate": result.error_rate,
                    "success_rate": result.success_rate,
                    "response_time_ms": result.response_time_ms,
                    "message": result.message,
                    "issues": result.issues
                }
                for component, result in results.items()
            }
        }

    except Exception as e:
        logger.error(f"Error checking all components: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check component health"
        )


@router.post("/components/register")
async def register_component(request: ComponentRegisterRequest):
    """
    Register a component for monitoring

    Args:
        request: Component registration request

    Returns:
        Registration confirmation
    """
    try:
        # Register component
        health_monitor.register_component(request.component)

        # Enable circuit breaker if requested
        if request.enable_circuit_breaker:
            recovery_engine.register_circuit_breaker(
                request.component,
                request.circuit_breaker_config
            )

        return {
            "component": request.component,
            "registered": True,
            "circuit_breaker_enabled": request.enable_circuit_breaker,
            "message": f"Component {request.component} registered successfully"
        }

    except Exception as e:
        logger.error(f"Error registering component: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register component"
        )


@router.get("/components")
async def list_components():
    """
    List all registered components

    Returns:
        List of components with their status
    """
    try:
        components = {}

        for component in health_monitor.components.keys():
            stats = health_monitor.get_component_stats(component)
            components[component] = stats

        return {
            "total": len(components),
            "components": components
        }

    except Exception as e:
        logger.error(f"Error listing components: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list components"
        )


@router.get("/recovery/stats")
async def get_recovery_stats(component: Optional[str] = None):
    """
    Get recovery statistics

    Args:
        component: Optional component filter

    Returns:
        Recovery statistics
    """
    try:
        stats = recovery_engine.get_recovery_stats()

        if component:
            # Filter for specific component
            component_stats = stats.get("by_component", {}).get(component, {})
            return {
                "component": component,
                "statistics": component_stats
            }

        return {
            "overall": {
                "total_recoveries": stats["total_recoveries"],
                "successful_recoveries": stats["successful_recoveries"],
                "failed_recoveries": stats["failed_recoveries"],
                "success_rate": stats["success_rate"],
                "avg_duration_ms": stats["avg_duration_ms"]
            },
            "by_action": stats["by_action"],
            "by_component": stats["by_component"]
        }

    except Exception as e:
        logger.error(f"Error getting recovery stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recovery statistics"
        )


@router.get("/recovery/recent")
async def get_recent_recoveries(count: int = 10):
    """
    Get recent recovery attempts

    Args:
        count: Number of recent recoveries to return

    Returns:
        List of recent recoveries
    """
    try:
        recoveries = recovery_engine.get_recent_recoveries(count)

        return {
            "count": len(recoveries),
            "recoveries": recoveries
        }

    except Exception as e:
        logger.error(f"Error getting recent recoveries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recent recoveries"
        )


@router.get("/circuit-breakers")
async def get_circuit_breaker_status():
    """
    Get status of all circuit breakers

    Returns:
        Circuit breaker status for all components
    """
    try:
        status_dict = recovery_engine.get_circuit_breaker_status()

        return {
            "total": len(status_dict),
            "circuit_breakers": status_dict
        }

    except Exception as e:
        logger.error(f"Error getting circuit breaker status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get circuit breaker status"
        )


@router.post("/circuit-breakers/reset")
async def reset_circuit_breaker(request: CircuitBreakerResetRequest):
    """
    Reset a circuit breaker

    Args:
        request: Circuit breaker reset request

    Returns:
        Reset confirmation
    """
    try:
        recovery_engine.reset_circuit_breaker(request.component)

        return {
            "component": request.component,
            "reset": True,
            "message": f"Circuit breaker reset for {request.component}"
        }

    except Exception as e:
        logger.error(f"Error resetting circuit breaker: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset circuit breaker"
        )


@router.post("/monitoring/start")
async def start_monitoring():
    """
    Start continuous health monitoring

    Returns:
        Monitoring start confirmation
    """
    try:
        await health_monitor.start_monitoring()

        return {
            "monitoring": True,
            "message": "Health monitoring started",
            "check_interval_seconds": health_monitor.check_interval
        }

    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start monitoring"
        )


@router.post("/monitoring/stop")
async def stop_monitoring():
    """
    Stop continuous health monitoring

    Returns:
        Monitoring stop confirmation
    """
    try:
        await health_monitor.stop_monitoring()

        return {
            "monitoring": False,
            "message": "Health monitoring stopped"
        }

    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop monitoring"
        )


@router.get("/monitoring/status")
async def get_monitoring_status():
    """
    Get monitoring status

    Returns:
        Monitoring configuration and status
    """
    return {
        "monitoring_active": health_monitor.monitoring,
        "check_interval_seconds": health_monitor.check_interval,
        "alert_threshold": health_monitor.alert_threshold.value,
        "registered_components": len(health_monitor.components),
        "registered_health_checks": len(health_monitor.health_checks),
        "alert_callbacks": len(health_monitor.alert_callbacks)
    }


@router.get("/errors/categories")
async def list_error_categories():
    """List available error categories"""
    return {
        "categories": [
            {
                "id": c.value,
                "name": c.value.replace("_", " ").title()
            }
            for c in ErrorCategory
        ]
    }


@router.get("/errors/severities")
async def list_error_severities():
    """List available error severities"""
    return {
        "severities": [
            {
                "id": s.value,
                "name": s.value.title(),
                "description": {
                    "low": "Minor issues, can be ignored",
                    "medium": "Needs attention but not critical",
                    "high": "Requires immediate action",
                    "critical": "System-threatening, urgent recovery"
                }.get(s.value, "")
            }
            for s in ErrorSeverity
        ]
    }


@router.get("/health-statuses")
async def list_health_statuses():
    """List available health statuses"""
    return {
        "statuses": [
            {
                "id": s.value,
                "name": s.value.title(),
                "description": {
                    "healthy": "All systems operational",
                    "degraded": "Some issues but operational",
                    "unhealthy": "Major issues, limited functionality",
                    "critical": "System failure, needs recovery"
                }.get(s.value, "")
            }
            for s in HealthStatus
        ]
    }


@router.get("/component/{component}/stats")
async def get_component_stats(component: str):
    """
    Get detailed statistics for a component

    Args:
        component: Component name

    Returns:
        Component statistics
    """
    try:
        stats = health_monitor.get_component_stats(component)
        return stats

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error getting component stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get component statistics"
        )


@router.post("/component/{component}/reset")
async def reset_component_metrics(component: str):
    """
    Reset metrics for a component

    Args:
        component: Component name

    Returns:
        Reset confirmation
    """
    try:
        health_monitor.reset_component(component)

        return {
            "component": component,
            "reset": True,
            "message": f"Metrics reset for {component}"
        }

    except Exception as e:
        logger.error(f"Error resetting component: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset component metrics"
        )


# Export router
healing_router = router
