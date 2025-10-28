"""
YAGO v7.2 - Plugin Core Module
Core plugin system components
"""

from .base import (
    Plugin,
    PluginType,
    PluginStatus,
    PluginMetadata,
    PluginContext,
    AgentPlugin,
    DashboardPlugin,
    IntegrationPlugin,
    WorkflowPlugin,
    ToolPlugin,
)
from .registry import PluginRegistry, get_registry
from .loader import PluginLoader
from .manager import PluginManager, get_manager

__all__ = [
    # Base classes
    'Plugin',
    'AgentPlugin',
    'DashboardPlugin',
    'IntegrationPlugin',
    'WorkflowPlugin',
    'ToolPlugin',

    # Enums
    'PluginType',
    'PluginStatus',

    # Models
    'PluginMetadata',
    'PluginContext',

    # Core components
    'PluginRegistry',
    'PluginLoader',
    'PluginManager',

    # Factory functions
    'get_registry',
    'get_manager',
]
