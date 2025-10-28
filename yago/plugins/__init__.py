"""
YAGO v7.2 - Plugin System
Extensible plugin architecture for custom functionality
"""

from .core.base import Plugin, PluginMetadata, PluginType, PluginStatus
from .core.registry import PluginRegistry
from .core.loader import PluginLoader
from .core.manager import PluginManager

__version__ = "7.2.0"

__all__ = [
    'Plugin',
    'PluginMetadata',
    'PluginType',
    'PluginStatus',
    'PluginRegistry',
    'PluginLoader',
    'PluginManager',
]
