"""
YAGO v7.2 - Plugin Registry
Central registry for plugin discovery, registration, and management
"""

from typing import Dict, List, Optional, Set, Any
from pathlib import Path
import json
import logging
from datetime import datetime

from .base import (
    Plugin,
    PluginMetadata,
    PluginType,
    PluginStatus
)

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Central registry for all plugins in the YAGO system

    Responsibilities:
    - Register and unregister plugins
    - Discover plugins from filesystem
    - Manage plugin metadata
    - Handle plugin dependencies
    - Validate plugin compatibility
    """

    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        """
        Initialize plugin registry

        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self._plugins: Dict[str, Plugin] = {}  # plugin_id -> Plugin instance
        self._metadata: Dict[str, PluginMetadata] = {}  # plugin_id -> metadata
        self._plugin_dirs = plugin_dirs or []
        self._dependency_graph: Dict[str, Set[str]] = {}  # plugin_id -> set of dependencies

        logger.info(f"PluginRegistry initialized with {len(self._plugin_dirs)} plugin directories")

    def register(self, plugin: Plugin) -> bool:
        """
        Register a plugin in the registry

        Args:
            plugin: Plugin instance to register

        Returns:
            bool: True if registration successful
        """
        try:
            plugin_id = plugin.metadata.id

            # Check if already registered
            if plugin_id in self._plugins:
                logger.warning(f"Plugin {plugin_id} already registered")
                return False

            # Validate plugin
            if not self._validate_plugin(plugin):
                logger.error(f"Plugin {plugin_id} validation failed")
                return False

            # Check dependencies
            if not self._check_dependencies(plugin.metadata):
                logger.error(f"Plugin {plugin_id} has unmet dependencies")
                return False

            # Register plugin
            self._plugins[plugin_id] = plugin
            self._metadata[plugin_id] = plugin.metadata

            # Update dependency graph
            self._dependency_graph[plugin_id] = set(plugin.metadata.plugin_dependencies)

            logger.info(f"Plugin {plugin_id} registered successfully")
            return True

        except Exception as e:
            logger.error(f"Error registering plugin: {e}")
            return False

    def unregister(self, plugin_id: str) -> bool:
        """
        Unregister a plugin from the registry

        Args:
            plugin_id: ID of plugin to unregister

        Returns:
            bool: True if unregistration successful
        """
        try:
            if plugin_id not in self._plugins:
                logger.warning(f"Plugin {plugin_id} not found in registry")
                return False

            # Check if other plugins depend on this one
            dependents = self._get_dependents(plugin_id)
            if dependents:
                logger.error(f"Cannot unregister {plugin_id}: required by {dependents}")
                return False

            # Remove from registry
            plugin = self._plugins.pop(plugin_id)
            self._metadata.pop(plugin_id)
            self._dependency_graph.pop(plugin_id, None)

            logger.info(f"Plugin {plugin_id} unregistered successfully")
            return True

        except Exception as e:
            logger.error(f"Error unregistering plugin: {e}")
            return False

    def get(self, plugin_id: str) -> Optional[Plugin]:
        """Get plugin by ID"""
        return self._plugins.get(plugin_id)

    def get_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get plugin metadata by ID"""
        return self._metadata.get(plugin_id)

    def get_all(self) -> List[Plugin]:
        """Get all registered plugins"""
        return list(self._plugins.values())

    def get_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """Get all plugins of a specific type"""
        return [
            plugin for plugin in self._plugins.values()
            if plugin.metadata.type == plugin_type
        ]

    def get_by_status(self, status: PluginStatus) -> List[Plugin]:
        """Get all plugins with a specific status"""
        return [
            plugin for plugin in self._plugins.values()
            if plugin.status == status
        ]

    def search(self,
               query: str = "",
               plugin_type: Optional[PluginType] = None,
               tags: Optional[List[str]] = None,
               author: Optional[str] = None) -> List[Plugin]:
        """
        Search for plugins

        Args:
            query: Search term for name/description
            plugin_type: Filter by plugin type
            tags: Filter by tags
            author: Filter by author

        Returns:
            List of matching plugins
        """
        results = list(self._plugins.values())

        # Filter by type
        if plugin_type:
            results = [p for p in results if p.metadata.type == plugin_type]

        # Filter by author
        if author:
            results = [p for p in results if author.lower() in p.metadata.author.lower()]

        # Filter by tags
        if tags:
            results = [
                p for p in results
                if any(tag in p.metadata.tags for tag in tags)
            ]

        # Search in name and description
        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if (query_lower in p.metadata.name.lower() or
                    query_lower in p.metadata.description.lower())
            ]

        return results

    def discover(self, plugin_dir: Path) -> List[PluginMetadata]:
        """
        Discover plugins in a directory

        Args:
            plugin_dir: Directory to search

        Returns:
            List of discovered plugin metadata
        """
        discovered = []

        try:
            if not plugin_dir.exists() or not plugin_dir.is_dir():
                logger.warning(f"Plugin directory not found: {plugin_dir}")
                return discovered

            # Look for plugin.json files
            for plugin_file in plugin_dir.rglob("plugin.json"):
                try:
                    with open(plugin_file, 'r') as f:
                        data = json.load(f)

                    metadata = PluginMetadata(**data)
                    discovered.append(metadata)
                    logger.info(f"Discovered plugin: {metadata.id}")

                except Exception as e:
                    logger.error(f"Error loading plugin metadata from {plugin_file}: {e}")

            logger.info(f"Discovered {len(discovered)} plugins in {plugin_dir}")
            return discovered

        except Exception as e:
            logger.error(f"Error discovering plugins: {e}")
            return discovered

    def discover_all(self) -> List[PluginMetadata]:
        """Discover plugins in all configured directories"""
        all_discovered = []
        for plugin_dir in self._plugin_dirs:
            all_discovered.extend(self.discover(plugin_dir))
        return all_discovered

    def get_dependency_order(self) -> List[str]:
        """
        Get plugin IDs in dependency order (topological sort)

        Returns:
            List of plugin IDs in order they should be loaded
        """
        # Kahn's algorithm for topological sort
        in_degree = {plugin_id: 0 for plugin_id in self._plugins}

        # Calculate in-degrees
        for plugin_id, deps in self._dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1

        # Queue of plugins with no dependencies
        queue = [pid for pid, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            plugin_id = queue.pop(0)
            result.append(plugin_id)

            # Reduce in-degree for dependent plugins
            for other_id, deps in self._dependency_graph.items():
                if plugin_id in deps:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)

        # Check for circular dependencies
        if len(result) != len(self._plugins):
            logger.error("Circular dependency detected in plugins")
            return []

        return result

    def _validate_plugin(self, plugin: Plugin) -> bool:
        """Validate plugin meets requirements"""
        try:
            # Check required metadata
            if not plugin.metadata.id or not plugin.metadata.name:
                return False

            # Check version format (basic semver check)
            version_parts = plugin.metadata.version.split('.')
            if len(version_parts) != 3:
                return False

            # Validate YAGO version compatibility
            # TODO: Implement proper version checking

            return True

        except Exception as e:
            logger.error(f"Plugin validation error: {e}")
            return False

    def _check_dependencies(self, metadata: PluginMetadata) -> bool:
        """Check if plugin dependencies are met"""
        for dep_id in metadata.plugin_dependencies:
            if dep_id not in self._plugins:
                logger.error(f"Missing dependency: {dep_id}")
                return False
        return True

    def _get_dependents(self, plugin_id: str) -> List[str]:
        """Get list of plugins that depend on this plugin"""
        dependents = []
        for other_id, deps in self._dependency_graph.items():
            if plugin_id in deps:
                dependents.append(other_id)
        return dependents

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_plugins": len(self._plugins),
            "by_type": {
                plugin_type.value: len(self.get_by_type(plugin_type))
                for plugin_type in PluginType
            },
            "by_status": {
                status.value: len(self.get_by_status(status))
                for status in PluginStatus
            },
            "plugin_directories": len(self._plugin_dirs),
        }

    def export_metadata(self, output_file: Path) -> bool:
        """Export all plugin metadata to JSON file"""
        try:
            data = {
                plugin_id: metadata.model_dump()
                for plugin_id, metadata in self._metadata.items()
            }

            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Exported metadata for {len(data)} plugins to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting metadata: {e}")
            return False

    def clear(self):
        """Clear all registered plugins (for testing)"""
        self._plugins.clear()
        self._metadata.clear()
        self._dependency_graph.clear()
        logger.info("Plugin registry cleared")


# Singleton instance
_registry: Optional[PluginRegistry] = None


def get_registry() -> PluginRegistry:
    """Get the global plugin registry instance"""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry
