"""
YAGO v7.2 - Plugin Manager
High-level plugin lifecycle management
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base import Plugin, PluginMetadata, PluginStatus, PluginType
from .registry import PluginRegistry, get_registry
from .loader import PluginLoader

logger = logging.getLogger(__name__)


class PluginManager:
    """
    High-level manager for plugin lifecycle

    Responsibilities:
    - Initialize plugins
    - Enable/disable plugins
    - Execute plugin operations
    - Monitor plugin health
    - Handle plugin errors
    """

    def __init__(self, registry: Optional[PluginRegistry] = None):
        """
        Initialize plugin manager

        Args:
            registry: Plugin registry instance (uses global if not provided)
        """
        self.registry = registry or get_registry()
        self.loader = PluginLoader(self.registry)
        self._execution_stats: Dict[str, Dict[str, Any]] = {}  # plugin_id -> stats

        logger.info("PluginManager initialized")

    async def initialize_plugin(self, plugin_id: str) -> bool:
        """
        Initialize a plugin

        Args:
            plugin_id: ID of plugin to initialize

        Returns:
            True if initialization successful
        """
        try:
            plugin = self.registry.get(plugin_id)
            if not plugin:
                logger.error(f"Plugin {plugin_id} not found")
                return False

            if plugin.status != PluginStatus.LOADED:
                logger.warning(f"Plugin {plugin_id} not in LOADED state")

            plugin.status = PluginStatus.LOADING

            # Validate before initializing
            if not await plugin.validate():
                logger.error(f"Plugin {plugin_id} validation failed")
                plugin.status = PluginStatus.ERROR
                return False

            # Initialize
            success = await plugin.initialize()

            if success:
                plugin.status = PluginStatus.LOADED
                plugin._initialized = True
                logger.info(f"Plugin {plugin_id} initialized successfully")
            else:
                plugin.status = PluginStatus.ERROR
                logger.error(f"Plugin {plugin_id} initialization failed")

            return success

        except Exception as e:
            logger.error(f"Error initializing plugin {plugin_id}: {e}")
            plugin.status = PluginStatus.ERROR
            return False

    async def initialize_all(self) -> Dict[str, bool]:
        """
        Initialize all registered plugins

        Returns:
            Dict mapping plugin_id to initialization success
        """
        results = {}

        # Get plugins in dependency order
        plugin_order = self.registry.get_dependency_order()

        for plugin_id in plugin_order:
            success = await self.initialize_plugin(plugin_id)
            results[plugin_id] = success

        successful = sum(1 for v in results.values() if v)
        logger.info(f"Initialized {successful}/{len(results)} plugins")

        return results

    async def enable_plugin(self, plugin_id: str, auto_initialize: bool = True) -> bool:
        """
        Enable a plugin

        Args:
            plugin_id: ID of plugin to enable
            auto_initialize: Automatically initialize if not already initialized

        Returns:
            True if enabled successfully
        """
        try:
            plugin = self.registry.get(plugin_id)
            if not plugin:
                logger.error(f"Plugin {plugin_id} not found")
                return False

            # Initialize if needed
            if not plugin._initialized and auto_initialize:
                if not await self.initialize_plugin(plugin_id):
                    return False

            # Enable
            success = await plugin.enable()

            if success:
                logger.info(f"Plugin {plugin_id} enabled successfully")
                self._init_stats(plugin_id)
            else:
                logger.error(f"Plugin {plugin_id} enable failed")

            return success

        except Exception as e:
            logger.error(f"Error enabling plugin {plugin_id}: {e}")
            return False

    async def disable_plugin(self, plugin_id: str) -> bool:
        """
        Disable a plugin

        Args:
            plugin_id: ID of plugin to disable

        Returns:
            True if disabled successfully
        """
        try:
            plugin = self.registry.get(plugin_id)
            if not plugin:
                logger.error(f"Plugin {plugin_id} not found")
                return False

            success = await plugin.disable()

            if success:
                logger.info(f"Plugin {plugin_id} disabled successfully")
            else:
                logger.error(f"Plugin {plugin_id} disable failed")

            return success

        except Exception as e:
            logger.error(f"Error disabling plugin {plugin_id}: {e}")
            return False

    async def execute_plugin(self,
                            plugin_id: str,
                            input_data: Any = None,
                            **kwargs) -> Optional[Any]:
        """
        Execute a plugin

        Args:
            plugin_id: ID of plugin to execute
            input_data: Input data for the plugin
            **kwargs: Additional keyword arguments

        Returns:
            Plugin execution result or None if failed
        """
        try:
            plugin = self.registry.get(plugin_id)
            if not plugin:
                logger.error(f"Plugin {plugin_id} not found")
                return None

            if plugin.status != PluginStatus.ACTIVE:
                logger.error(f"Plugin {plugin_id} not active (status: {plugin.status})")
                return None

            # Execute
            import time
            start_time = time.time()

            result = await plugin.execute(input_data, **kwargs)

            execution_time = time.time() - start_time

            # Update stats
            self._update_stats(plugin_id, success=True, execution_time=execution_time)

            logger.info(f"Plugin {plugin_id} executed successfully in {execution_time:.3f}s")
            return result

        except Exception as e:
            logger.error(f"Error executing plugin {plugin_id}: {e}")
            self._update_stats(plugin_id, success=False)
            return None

    async def configure_plugin(self, plugin_id: str, config: Dict[str, Any]) -> bool:
        """
        Configure a plugin

        Args:
            plugin_id: ID of plugin to configure
            config: Configuration dictionary

        Returns:
            True if configuration successful
        """
        try:
            plugin = self.registry.get(plugin_id)
            if not plugin:
                logger.error(f"Plugin {plugin_id} not found")
                return False

            success = await plugin.configure(config)

            if success:
                logger.info(f"Plugin {plugin_id} configured successfully")
            else:
                logger.error(f"Plugin {plugin_id} configuration failed")

            return success

        except Exception as e:
            logger.error(f"Error configuring plugin {plugin_id}: {e}")
            return False

    async def health_check_plugin(self, plugin_id: str) -> Dict[str, Any]:
        """
        Check health of a plugin

        Args:
            plugin_id: ID of plugin to check

        Returns:
            Health status dictionary
        """
        try:
            plugin = self.registry.get(plugin_id)
            if not plugin:
                return {
                    "plugin_id": plugin_id,
                    "error": "Plugin not found"
                }

            health = await plugin.health_check()
            health["plugin_id"] = plugin_id

            return health

        except Exception as e:
            logger.error(f"Error checking plugin health {plugin_id}: {e}")
            return {
                "plugin_id": plugin_id,
                "error": str(e)
            }

    async def health_check_all(self) -> List[Dict[str, Any]]:
        """
        Check health of all plugins

        Returns:
            List of health status dictionaries
        """
        health_checks = []

        for plugin_id in self.registry._plugins.keys():
            health = await self.health_check_plugin(plugin_id)
            health_checks.append(health)

        return health_checks

    async def cleanup_plugin(self, plugin_id: str) -> bool:
        """
        Cleanup a plugin

        Args:
            plugin_id: ID of plugin to cleanup

        Returns:
            True if cleanup successful
        """
        try:
            plugin = self.registry.get(plugin_id)
            if not plugin:
                logger.error(f"Plugin {plugin_id} not found")
                return False

            # Disable if active
            if plugin.status == PluginStatus.ACTIVE:
                await self.disable_plugin(plugin_id)

            # Cleanup
            success = await plugin.cleanup()

            if success:
                plugin._initialized = False
                logger.info(f"Plugin {plugin_id} cleaned up successfully")
            else:
                logger.error(f"Plugin {plugin_id} cleanup failed")

            return success

        except Exception as e:
            logger.error(f"Error cleaning up plugin {plugin_id}: {e}")
            return False

    async def cleanup_all(self) -> Dict[str, bool]:
        """
        Cleanup all plugins

        Returns:
            Dict mapping plugin_id to cleanup success
        """
        results = {}

        # Cleanup in reverse dependency order
        plugin_order = self.registry.get_dependency_order()
        plugin_order.reverse()

        for plugin_id in plugin_order:
            success = await self.cleanup_plugin(plugin_id)
            results[plugin_id] = success

        return results

    def get_plugin_stats(self, plugin_id: str) -> Dict[str, Any]:
        """Get execution statistics for a plugin"""
        return self._execution_stats.get(plugin_id, {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "total_time": 0.0,
            "avg_time": 0.0
        })

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get execution statistics for all plugins"""
        return self._execution_stats.copy()

    def list_plugins(self,
                     plugin_type: Optional[PluginType] = None,
                     status: Optional[PluginStatus] = None) -> List[Dict[str, Any]]:
        """
        List plugins with optional filters

        Args:
            plugin_type: Filter by plugin type
            status: Filter by plugin status

        Returns:
            List of plugin information dictionaries
        """
        plugins = self.registry.get_all()

        # Apply filters
        if plugin_type:
            plugins = [p for p in plugins if p.metadata.type == plugin_type]

        if status:
            plugins = [p for p in plugins if p.status == status]

        # Return info
        return [p.get_info() for p in plugins]

    async def discover_and_load(self, plugin_dir: Path) -> List[Plugin]:
        """
        Discover and load plugins from a directory

        Args:
            plugin_dir: Directory to search

        Returns:
            List of loaded plugins
        """
        return self.loader.discover_and_load(plugin_dir, auto_register=True)

    async def reload_plugin(self, plugin_id: str) -> bool:
        """
        Reload a plugin

        Args:
            plugin_id: ID of plugin to reload

        Returns:
            True if reload successful
        """
        try:
            # Cleanup first
            await self.cleanup_plugin(plugin_id)

            # Reload
            plugin = self.loader.reload(plugin_id)

            if not plugin:
                return False

            # Re-initialize
            return await self.initialize_plugin(plugin_id)

        except Exception as e:
            logger.error(f"Error reloading plugin {plugin_id}: {e}")
            return False

    def _init_stats(self, plugin_id: str):
        """Initialize stats for a plugin"""
        if plugin_id not in self._execution_stats:
            self._execution_stats[plugin_id] = {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "total_time": 0.0,
                "avg_time": 0.0
            }

    def _update_stats(self, plugin_id: str, success: bool, execution_time: float = 0.0):
        """Update execution stats for a plugin"""
        if plugin_id not in self._execution_stats:
            self._init_stats(plugin_id)

        stats = self._execution_stats[plugin_id]
        stats["executions"] += 1

        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1

        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["executions"]


# Global manager instance
_manager: Optional[PluginManager] = None


def get_manager() -> PluginManager:
    """Get the global plugin manager instance"""
    global _manager
    if _manager is None:
        _manager = PluginManager()
    return _manager
