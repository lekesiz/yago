"""
YAGO v7.2 - Plugin Management API
RESTful API for plugin operations
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from yago.plugins.core import (
    get_manager,
    get_registry,
    PluginType,
    PluginStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/plugins", tags=["Plugins"])


# Request/Response Models

class PluginConfigRequest(BaseModel):
    """Request model for plugin configuration"""
    config: Dict[str, Any]


class PluginExecuteRequest(BaseModel):
    """Request model for plugin execution"""
    input_data: Optional[Any] = None
    kwargs: Dict[str, Any] = {}


class PluginLoadRequest(BaseModel):
    """Request model for loading plugins"""
    plugin_path: str


class PluginResponse(BaseModel):
    """Response model for plugin info"""
    id: str
    name: str
    version: str
    type: str
    status: str
    author: str
    description: str


class PluginDetailResponse(PluginResponse):
    """Detailed plugin response"""
    long_description: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    documentation: Optional[str] = None
    tags: List[str] = []
    capabilities: List[str] = []
    dependencies: List[str] = []
    plugin_dependencies: List[str] = []
    configurable: bool = True
    auto_enable: bool = False


# Endpoints

@router.get("", response_model=List[PluginResponse])
async def list_plugins(
    plugin_type: Optional[str] = None,
    status: Optional[str] = None
):
    """
    List all plugins with optional filters

    Args:
        plugin_type: Filter by plugin type (agent, dashboard, integration, etc.)
        status: Filter by status (loaded, active, error, etc.)

    Returns:
        List of plugins
    """
    try:
        manager = get_manager()

        # Parse filters
        type_filter = PluginType(plugin_type) if plugin_type else None
        status_filter = PluginStatus(status) if status else None

        plugins = manager.list_plugins(
            plugin_type=type_filter,
            status=status_filter
        )

        return plugins

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filter value: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error listing plugins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list plugins"
        )


@router.get("/{plugin_id}", response_model=PluginDetailResponse)
async def get_plugin(plugin_id: str):
    """
    Get detailed information about a specific plugin

    Args:
        plugin_id: ID of the plugin

    Returns:
        Detailed plugin information
    """
    try:
        registry = get_registry()
        plugin = registry.get(plugin_id)

        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin {plugin_id} not found"
            )

        metadata = plugin.metadata

        return PluginDetailResponse(
            id=metadata.id,
            name=metadata.name,
            version=metadata.version,
            type=metadata.type.value,
            status=plugin.status.value,
            author=metadata.author,
            description=metadata.description,
            long_description=metadata.long_description,
            homepage=metadata.homepage,
            repository=metadata.repository,
            documentation=metadata.documentation,
            tags=metadata.tags,
            capabilities=metadata.capabilities,
            dependencies=metadata.dependencies,
            plugin_dependencies=metadata.plugin_dependencies,
            configurable=metadata.configurable,
            auto_enable=metadata.auto_enable
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get plugin"
        )


@router.post("/{plugin_id}/initialize")
async def initialize_plugin(plugin_id: str):
    """
    Initialize a plugin

    Args:
        plugin_id: ID of the plugin

    Returns:
        Success status
    """
    try:
        manager = get_manager()
        success = await manager.initialize_plugin(plugin_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize plugin {plugin_id}"
            )

        return {"success": True, "message": f"Plugin {plugin_id} initialized"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{plugin_id}/enable")
async def enable_plugin(plugin_id: str):
    """
    Enable a plugin

    Args:
        plugin_id: ID of the plugin

    Returns:
        Success status
    """
    try:
        manager = get_manager()
        success = await manager.enable_plugin(plugin_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to enable plugin {plugin_id}"
            )

        return {"success": True, "message": f"Plugin {plugin_id} enabled"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{plugin_id}/disable")
async def disable_plugin(plugin_id: str):
    """
    Disable a plugin

    Args:
        plugin_id: ID of the plugin

    Returns:
        Success status
    """
    try:
        manager = get_manager()
        success = await manager.disable_plugin(plugin_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to disable plugin {plugin_id}"
            )

        return {"success": True, "message": f"Plugin {plugin_id} disabled"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{plugin_id}/configure")
async def configure_plugin(plugin_id: str, request: PluginConfigRequest):
    """
    Configure a plugin

    Args:
        plugin_id: ID of the plugin
        request: Configuration data

    Returns:
        Success status
    """
    try:
        manager = get_manager()
        success = await manager.configure_plugin(plugin_id, request.config)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to configure plugin {plugin_id}"
            )

        return {"success": True, "message": f"Plugin {plugin_id} configured"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{plugin_id}/execute")
async def execute_plugin(plugin_id: str, request: PluginExecuteRequest):
    """
    Execute a plugin

    Args:
        plugin_id: ID of the plugin
        request: Execution request with input data

    Returns:
        Plugin execution result
    """
    try:
        manager = get_manager()
        result = await manager.execute_plugin(
            plugin_id,
            request.input_data,
            **request.kwargs
        )

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Plugin {plugin_id} execution failed"
            )

        return {
            "success": True,
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing plugin {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{plugin_id}/health")
async def health_check_plugin(plugin_id: str):
    """
    Check health of a plugin

    Args:
        plugin_id: ID of the plugin

    Returns:
        Health status
    """
    try:
        manager = get_manager()
        health = await manager.health_check_plugin(plugin_id)

        return health

    except Exception as e:
        logger.error(f"Error checking plugin health {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{plugin_id}/stats")
async def get_plugin_stats(plugin_id: str):
    """
    Get execution statistics for a plugin

    Args:
        plugin_id: ID of the plugin

    Returns:
        Execution statistics
    """
    try:
        manager = get_manager()
        stats = manager.get_plugin_stats(plugin_id)

        return {
            "plugin_id": plugin_id,
            "stats": stats
        }

    except Exception as e:
        logger.error(f"Error getting plugin stats {plugin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/load")
async def load_plugin(request: PluginLoadRequest):
    """
    Load a plugin from filesystem

    Args:
        request: Load request with plugin path

    Returns:
        Loaded plugin info
    """
    try:
        manager = get_manager()
        plugin_path = Path(request.plugin_path)

        if not plugin_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin path not found: {request.plugin_path}"
            )

        plugins = await manager.discover_and_load(plugin_path)

        if not plugins:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to load plugin"
            )

        return {
            "success": True,
            "message": f"Loaded {len(plugins)} plugin(s)",
            "plugins": [p.get_info() for p in plugins]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading plugin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats/all")
async def get_all_stats():
    """
    Get execution statistics for all plugins

    Returns:
        All plugin statistics
    """
    try:
        manager = get_manager()
        stats = manager.get_all_stats()

        return {
            "stats": stats,
            "total_plugins": len(stats)
        }

    except Exception as e:
        logger.error(f"Error getting all stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/health/all")
async def health_check_all():
    """
    Check health of all plugins

    Returns:
        Health status for all plugins
    """
    try:
        manager = get_manager()
        health_checks = await manager.health_check_all()

        return {
            "health_checks": health_checks,
            "total_plugins": len(health_checks),
            "healthy_count": sum(1 for h in health_checks if h.get("healthy", False))
        }

    except Exception as e:
        logger.error(f"Error checking all plugin health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/types")
async def get_plugin_types():
    """Get all available plugin types"""
    return {
        "types": [pt.value for pt in PluginType]
    }


@router.get("/statuses")
async def get_plugin_statuses():
    """Get all available plugin statuses"""
    return {
        "statuses": [ps.value for ps in PluginStatus]
    }


# Export for main app
plugins_router = router
