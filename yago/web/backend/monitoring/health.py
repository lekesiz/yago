"""
YAGO v7.2 - Health Check Endpoints
Comprehensive health monitoring for all system components
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Any, List
from enum import Enum
import time
import sqlite3
import os
from datetime import datetime

router = APIRouter(prefix="/api/v1/health", tags=["Health"])


class HealthStatus(str, Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Health status of a single component"""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float
    details: Dict[str, Any] = {}


class SystemHealth(BaseModel):
    """Overall system health"""
    status: HealthStatus
    timestamp: str
    uptime_seconds: float
    components: List[ComponentHealth]
    summary: Dict[str, int]


# Track service start time
SERVICE_START_TIME = time.time()


async def check_database() -> ComponentHealth:
    """Check database connectivity and health"""
    start = time.time()

    try:
        # Try to connect to database
        db_path = os.getenv("DATABASE_PATH", "data/yago.db")

        if not os.path.exists(db_path):
            return ComponentHealth(
                name="database",
                status=HealthStatus.DEGRADED,
                message="Database file not found",
                response_time_ms=(time.time() - start) * 1000,
                details={"path": db_path}
            )

        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        # Get database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]

        conn.close()

        if result[0] == 1:
            return ComponentHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database is accessible",
                response_time_ms=(time.time() - start) * 1000,
                details={
                    "path": db_path,
                    "size_mb": db_size / 1024 / 1024,
                    "writable": os.access(db_path, os.W_OK)
                }
            )
        else:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message="Database query failed",
                response_time_ms=(time.time() - start) * 1000
            )

    except Exception as e:
        return ComponentHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=f"Database error: {str(e)}",
            response_time_ms=(time.time() - start) * 1000
        )


async def check_filesystem() -> ComponentHealth:
    """Check filesystem health"""
    start = time.time()

    try:
        import psutil

        # Check disk space
        disk = psutil.disk_usage('/')

        if disk.percent > 90:
            status_level = HealthStatus.UNHEALTHY
            message = "Disk space critically low"
        elif disk.percent > 75:
            status_level = HealthStatus.DEGRADED
            message = "Disk space running low"
        else:
            status_level = HealthStatus.HEALTHY
            message = "Filesystem is healthy"

        return ComponentHealth(
            name="filesystem",
            status=status_level,
            message=message,
            response_time_ms=(time.time() - start) * 1000,
            details={
                "disk_total_gb": disk.total / 1024 / 1024 / 1024,
                "disk_used_gb": disk.used / 1024 / 1024 / 1024,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "disk_percent": disk.percent
            }
        )

    except Exception as e:
        return ComponentHealth(
            name="filesystem",
            status=HealthStatus.UNHEALTHY,
            message=f"Filesystem check failed: {str(e)}",
            response_time_ms=(time.time() - start) * 1000
        )


async def check_memory() -> ComponentHealth:
    """Check memory health"""
    start = time.time()

    try:
        import psutil

        memory = psutil.virtual_memory()

        if memory.percent > 90:
            status_level = HealthStatus.UNHEALTHY
            message = "Memory usage critically high"
        elif memory.percent > 75:
            status_level = HealthStatus.DEGRADED
            message = "Memory usage high"
        else:
            status_level = HealthStatus.HEALTHY
            message = "Memory is healthy"

        return ComponentHealth(
            name="memory",
            status=status_level,
            message=message,
            response_time_ms=(time.time() - start) * 1000,
            details={
                "total_mb": memory.total / 1024 / 1024,
                "available_mb": memory.available / 1024 / 1024,
                "used_mb": memory.used / 1024 / 1024,
                "percent": memory.percent
            }
        )

    except Exception as e:
        return ComponentHealth(
            name="memory",
            status=HealthStatus.UNHEALTHY,
            message=f"Memory check failed: {str(e)}",
            response_time_ms=(time.time() - start) * 1000
        )


async def check_cpu() -> ComponentHealth:
    """Check CPU health"""
    start = time.time()

    try:
        import psutil

        cpu_percent = psutil.cpu_percent(interval=0.1)

        if cpu_percent > 90:
            status_level = HealthStatus.DEGRADED
            message = "CPU usage very high"
        elif cpu_percent > 75:
            status_level = HealthStatus.DEGRADED
            message = "CPU usage high"
        else:
            status_level = HealthStatus.HEALTHY
            message = "CPU is healthy"

        return ComponentHealth(
            name="cpu",
            status=status_level,
            message=message,
            response_time_ms=(time.time() - start) * 1000,
            details={
                "cpu_percent": cpu_percent,
                "cpu_count": psutil.cpu_count(),
                "cpu_freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None
            }
        )

    except Exception as e:
        return ComponentHealth(
            name="cpu",
            status=HealthStatus.UNHEALTHY,
            message=f"CPU check failed: {str(e)}",
            response_time_ms=(time.time() - start) * 1000
        )


async def check_api_keys() -> ComponentHealth:
    """Check if required API keys are configured"""
    start = time.time()

    try:
        required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]
        configured = []
        missing = []

        for key in required_keys:
            value = os.getenv(key)
            if value and len(value) > 10:  # Basic validation
                configured.append(key)
            else:
                missing.append(key)

        if len(configured) == len(required_keys):
            status_level = HealthStatus.HEALTHY
            message = "All API keys configured"
        elif len(configured) > 0:
            status_level = HealthStatus.DEGRADED
            message = f"Some API keys missing: {', '.join(missing)}"
        else:
            status_level = HealthStatus.UNHEALTHY
            message = "No API keys configured"

        return ComponentHealth(
            name="api_keys",
            status=status_level,
            message=message,
            response_time_ms=(time.time() - start) * 1000,
            details={
                "configured": configured,
                "missing": missing,
                "total_required": len(required_keys)
            }
        )

    except Exception as e:
        return ComponentHealth(
            name="api_keys",
            status=HealthStatus.UNHEALTHY,
            message=f"API key check failed: {str(e)}",
            response_time_ms=(time.time() - start) * 1000
        )


@router.get("", response_model=SystemHealth)
async def health_check():
    """
    Comprehensive health check of all system components
    Returns detailed health status for monitoring
    """
    components = await check_all_components()

    # Determine overall status
    statuses = [c.status for c in components]

    if all(s == HealthStatus.HEALTHY for s in statuses):
        overall_status = HealthStatus.HEALTHY
    elif any(s == HealthStatus.UNHEALTHY for s in statuses):
        overall_status = HealthStatus.UNHEALTHY
    else:
        overall_status = HealthStatus.DEGRADED

    # Count by status
    summary = {
        "healthy": sum(1 for s in statuses if s == HealthStatus.HEALTHY),
        "degraded": sum(1 for s in statuses if s == HealthStatus.DEGRADED),
        "unhealthy": sum(1 for s in statuses if s == HealthStatus.UNHEALTHY),
        "total": len(statuses)
    }

    return SystemHealth(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        uptime_seconds=time.time() - SERVICE_START_TIME,
        components=components,
        summary=summary
    )


@router.get("/liveness")
async def liveness_check():
    """
    Simple liveness check for Kubernetes/Docker
    Returns 200 if service is running
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/readiness")
async def readiness_check():
    """
    Readiness check for Kubernetes/Docker
    Returns 200 only if service is ready to handle requests
    """
    components = await check_all_components()

    # Check critical components
    db = next((c for c in components if c.name == "database"), None)

    if db and db.status == HealthStatus.UNHEALTHY:
        return {
            "status": "not_ready",
            "reason": "Database unavailable",
            "timestamp": datetime.utcnow().isoformat()
        }, status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


async def check_all_components() -> List[ComponentHealth]:
    """Check all system components"""
    return [
        await check_database(),
        await check_filesystem(),
        await check_memory(),
        await check_cpu(),
        await check_api_keys(),
    ]


# Export for use in other modules
health_router = router
