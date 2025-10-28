"""
YAGO v7.2 - Plugin Loader
Dynamic plugin loading and instantiation
"""

import importlib
import importlib.util
import sys
import logging
from pathlib import Path
from typing import Optional, Type, Dict, Any, List

from .base import Plugin, PluginMetadata, PluginContext, PluginStatus
from .registry import PluginRegistry

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Handles dynamic loading of plugins from filesystem

    Responsibilities:
    - Load plugin modules dynamically
    - Instantiate plugin classes
    - Validate plugin implementations
    - Handle loading errors gracefully
    """

    def __init__(self, registry: PluginRegistry):
        """
        Initialize plugin loader

        Args:
            registry: Plugin registry instance
        """
        self.registry = registry
        self._loaded_modules: Dict[str, Any] = {}  # plugin_id -> module

        logger.info("PluginLoader initialized")

    def load_from_file(self, plugin_path: Path, metadata: PluginMetadata) -> Optional[Plugin]:
        """
        Load a plugin from a Python file

        Args:
            plugin_path: Path to plugin Python file
            metadata: Plugin metadata

        Returns:
            Plugin instance or None if loading failed
        """
        try:
            if not plugin_path.exists():
                logger.error(f"Plugin file not found: {plugin_path}")
                return None

            # Load module
            module = self._load_module(plugin_path, metadata.id)
            if not module:
                return None

            # Find plugin class
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                logger.error(f"No Plugin class found in {plugin_path}")
                return None

            # Validate plugin class
            if not self._validate_plugin_class(plugin_class):
                logger.error(f"Invalid plugin class in {plugin_path}")
                return None

            # Create plugin instance
            context = PluginContext(config=metadata.default_config)
            plugin = plugin_class(metadata=metadata, context=context)

            # Store module reference
            self._loaded_modules[metadata.id] = module

            logger.info(f"Successfully loaded plugin: {metadata.id} from {plugin_path}")
            return plugin

        except Exception as e:
            logger.error(f"Error loading plugin from {plugin_path}: {e}")
            return None

    def load_from_directory(self, plugin_dir: Path) -> Optional[Plugin]:
        """
        Load a plugin from a directory containing plugin.json and plugin.py

        Args:
            plugin_dir: Directory containing plugin files

        Returns:
            Plugin instance or None if loading failed
        """
        try:
            if not plugin_dir.is_dir():
                logger.error(f"Plugin directory not found: {plugin_dir}")
                return None

            # Load metadata
            metadata_file = plugin_dir / "plugin.json"
            if not metadata_file.exists():
                logger.error(f"plugin.json not found in {plugin_dir}")
                return None

            import json
            with open(metadata_file, 'r') as f:
                metadata_dict = json.load(f)

            metadata = PluginMetadata(**metadata_dict)

            # Load plugin code
            plugin_file = plugin_dir / "plugin.py"
            if not plugin_file.exists():
                logger.error(f"plugin.py not found in {plugin_dir}")
                return None

            return self.load_from_file(plugin_file, metadata)

        except Exception as e:
            logger.error(f"Error loading plugin from directory {plugin_dir}: {e}")
            return None

    def load_and_register(self, plugin_path: Path) -> Optional[Plugin]:
        """
        Load a plugin and register it in the registry

        Args:
            plugin_path: Path to plugin file or directory

        Returns:
            Plugin instance or None if failed
        """
        try:
            # Determine if path is file or directory
            if plugin_path.is_dir():
                plugin = self.load_from_directory(plugin_path)
            else:
                # Need metadata - look for adjacent plugin.json
                metadata_file = plugin_path.parent / "plugin.json"
                if not metadata_file.exists():
                    logger.error(f"plugin.json not found for {plugin_path}")
                    return None

                import json
                with open(metadata_file, 'r') as f:
                    metadata_dict = json.load(f)

                metadata = PluginMetadata(**metadata_dict)
                plugin = self.load_from_file(plugin_path, metadata)

            if not plugin:
                return None

            # Register in registry
            if self.registry.register(plugin):
                return plugin
            else:
                logger.error(f"Failed to register plugin: {plugin.metadata.id}")
                return None

        except Exception as e:
            logger.error(f"Error loading and registering plugin: {e}")
            return None

    def load_multiple(self, plugin_paths: List[Path]) -> List[Plugin]:
        """
        Load multiple plugins

        Args:
            plugin_paths: List of paths to plugin files or directories

        Returns:
            List of successfully loaded plugins
        """
        loaded = []
        for path in plugin_paths:
            plugin = self.load_and_register(path)
            if plugin:
                loaded.append(plugin)

        logger.info(f"Loaded {len(loaded)}/{len(plugin_paths)} plugins")
        return loaded

    def reload(self, plugin_id: str) -> Optional[Plugin]:
        """
        Reload a plugin

        Args:
            plugin_id: ID of plugin to reload

        Returns:
            Reloaded plugin instance or None
        """
        try:
            # Get existing plugin
            existing = self.registry.get(plugin_id)
            if not existing:
                logger.error(f"Plugin {plugin_id} not found in registry")
                return None

            # Cleanup existing plugin
            await existing.cleanup()

            # Unregister
            self.registry.unregister(plugin_id)

            # Reload module
            if plugin_id in self._loaded_modules:
                module = self._loaded_modules[plugin_id]
                importlib.reload(module)

            # TODO: Re-load from original path
            # For now, just log that reload is not fully implemented
            logger.warning(f"Full reload not implemented for {plugin_id}")

            return existing

        except Exception as e:
            logger.error(f"Error reloading plugin {plugin_id}: {e}")
            return None

    def unload(self, plugin_id: str) -> bool:
        """
        Unload a plugin

        Args:
            plugin_id: ID of plugin to unload

        Returns:
            True if unloaded successfully
        """
        try:
            # Get plugin
            plugin = self.registry.get(plugin_id)
            if not plugin:
                logger.error(f"Plugin {plugin_id} not found")
                return False

            # Cleanup
            if plugin.status == PluginStatus.ACTIVE:
                await plugin.disable()

            await plugin.cleanup()

            # Unregister
            if not self.registry.unregister(plugin_id):
                return False

            # Remove module
            if plugin_id in self._loaded_modules:
                del self._loaded_modules[plugin_id]

            logger.info(f"Plugin {plugin_id} unloaded successfully")
            return True

        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False

    def _load_module(self, module_path: Path, module_name: str) -> Optional[Any]:
        """
        Dynamically load a Python module

        Args:
            module_path: Path to Python file
            module_name: Name for the module

        Returns:
            Loaded module or None
        """
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if not spec or not spec.loader:
                logger.error(f"Failed to create module spec for {module_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            return module

        except Exception as e:
            logger.error(f"Error loading module from {module_path}: {e}")
            return None

    def _find_plugin_class(self, module: Any) -> Optional[Type[Plugin]]:
        """
        Find the Plugin class in a module

        Args:
            module: Python module

        Returns:
            Plugin class or None
        """
        try:
            for name in dir(module):
                obj = getattr(module, name)

                # Check if it's a class
                if not isinstance(obj, type):
                    continue

                # Check if it inherits from Plugin (but is not Plugin itself)
                if issubclass(obj, Plugin) and obj is not Plugin:
                    return obj

            return None

        except Exception as e:
            logger.error(f"Error finding plugin class: {e}")
            return None

    def _validate_plugin_class(self, plugin_class: Type[Plugin]) -> bool:
        """
        Validate that a plugin class implements required methods

        Args:
            plugin_class: Plugin class to validate

        Returns:
            True if valid
        """
        try:
            # Check that required abstract methods are implemented
            required_methods = ['initialize', 'execute']

            for method_name in required_methods:
                if not hasattr(plugin_class, method_name):
                    logger.error(f"Plugin class missing required method: {method_name}")
                    return False

                method = getattr(plugin_class, method_name)
                if not callable(method):
                    logger.error(f"Plugin {method_name} is not callable")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating plugin class: {e}")
            return False

    def discover_and_load(self, plugin_dir: Path, auto_register: bool = True) -> List[Plugin]:
        """
        Discover and load all plugins in a directory

        Args:
            plugin_dir: Directory to search
            auto_register: Automatically register loaded plugins

        Returns:
            List of loaded plugins
        """
        loaded = []

        try:
            # Discover plugin metadata
            discovered = self.registry.discover(plugin_dir)

            logger.info(f"Discovered {len(discovered)} plugins in {plugin_dir}")

            # Load each plugin
            for metadata in discovered:
                # Find plugin directory
                plugin_path = plugin_dir / metadata.id

                if not plugin_path.exists():
                    logger.warning(f"Plugin directory not found: {plugin_path}")
                    continue

                # Load plugin
                if auto_register:
                    plugin = self.load_and_register(plugin_path)
                else:
                    plugin = self.load_from_directory(plugin_path)

                if plugin:
                    loaded.append(plugin)

            logger.info(f"Loaded {len(loaded)} plugins from {plugin_dir}")
            return loaded

        except Exception as e:
            logger.error(f"Error discovering and loading plugins: {e}")
            return loaded

    def get_load_errors(self) -> Dict[str, str]:
        """Get any loading errors that occurred"""
        # TODO: Implement error tracking
        return {}
