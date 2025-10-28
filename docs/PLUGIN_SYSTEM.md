# YAGO v7.2 - Plugin System Documentation

## Overview

The YAGO Plugin System provides a powerful and flexible framework for extending YAGO's functionality through custom plugins. Developers can create plugins to add new agents, tools, integrations, dashboard widgets, and more.

## Table of Contents

1. [Architecture](#architecture)
2. [Plugin Types](#plugin-types)
3. [Quick Start](#quick-start)
4. [Plugin Development](#plugin-development)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Architecture

### Core Components

The plugin system consists of four main components:

#### 1. Plugin Base Classes (`yago/plugins/core/base.py`)

Abstract base classes that all plugins must inherit from:

- `Plugin` - Base class for all plugins
- `AgentPlugin` - For custom AI agents
- `DashboardPlugin` - For dashboard widgets
- `IntegrationPlugin` - For external service integrations
- `WorkflowPlugin` - For custom workflow steps
- `ToolPlugin` - For agent tools

#### 2. Plugin Registry (`yago/plugins/core/registry.py`)

Manages plugin registration and discovery:

- Register/unregister plugins
- Search and filter plugins
- Handle plugin dependencies
- Validate plugin compatibility

#### 3. Plugin Loader (`yago/plugins/core/loader.py`)

Handles dynamic plugin loading:

- Load plugins from filesystem
- Validate plugin implementations
- Handle loading errors
- Support plugin reloading

#### 4. Plugin Manager (`yago/plugins/core/manager.py`)

High-level plugin lifecycle management:

- Initialize/cleanup plugins
- Enable/disable plugins
- Execute plugin operations
- Monitor plugin health
- Track execution statistics

### Plugin Lifecycle

```
UNLOADED → LOADING → LOADED → ACTIVE
                ↓         ↓       ↓
              ERROR  ← ERROR ← ERROR
                ↓         ↓       ↓
           DISABLED ← DISABLED ← DISABLED
```

States:
- **UNLOADED**: Plugin not yet loaded
- **LOADING**: Plugin being initialized
- **LOADED**: Plugin initialized but not active
- **ACTIVE**: Plugin enabled and ready for execution
- **ERROR**: Plugin encountered an error
- **DISABLED**: Plugin disabled by user

## Plugin Types

### 1. Agent Plugin

Custom AI agent implementations with specific behaviors and capabilities.

```python
from yago.plugins.core import AgentPlugin

class MyAgentPlugin(AgentPlugin):
    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent task"""
        # Implement agent logic
        return {"result": "processed"}
```

**Use Cases:**
- Specialized AI assistants
- Domain-specific agents
- Custom reasoning systems

### 2. Dashboard Plugin

Dashboard widgets and data visualization components.

```python
from yago.plugins.core import DashboardPlugin

class MyDashboardPlugin(DashboardPlugin):
    def render(self) -> Dict[str, Any]:
        """Render dashboard component"""
        return {"type": "chart", "data": []}

    def get_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        return {"metrics": {}}
```

**Use Cases:**
- Custom metrics dashboards
- Data visualization
- Real-time monitoring

### 3. Integration Plugin

Connect YAGO with external services and APIs.

```python
from yago.plugins.core import IntegrationPlugin

class MyIntegrationPlugin(IntegrationPlugin):
    async def connect(self) -> bool:
        """Connect to external service"""
        return True

    async def disconnect(self) -> bool:
        """Disconnect from service"""
        return True

    async def sync(self, data: Any) -> bool:
        """Sync data with service"""
        return True
```

**Use Cases:**
- External API integrations
- Database connections
- Third-party service connectors

### 4. Workflow Plugin

Custom workflow steps and automation.

```python
from yago.plugins.core import WorkflowPlugin

class MyWorkflowPlugin(WorkflowPlugin):
    async def run_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow step"""
        return {"success": True}
```

**Use Cases:**
- Custom automation steps
- Data transformations
- Business logic implementation

### 5. Tool Plugin

Tools that AI agents can use to perform specific tasks.

```python
from yago.plugins.core import ToolPlugin

class MyToolPlugin(ToolPlugin):
    async def invoke(self, *args, **kwargs) -> Any:
        """Invoke tool functionality"""
        return "result"

    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for LLM"""
        return {
            "name": "my_tool",
            "description": "Tool description",
            "parameters": {"type": "object"}
        }
```

**Use Cases:**
- Utility functions for agents
- External API calls
- Data processing tools

## Quick Start

### 1. Create Plugin Directory

```bash
mkdir -p yago/plugins/my_plugin
cd yago/plugins/my_plugin
```

### 2. Create `plugin.json`

```json
{
  "id": "my_plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "type": "tool",
  "description": "My awesome plugin",
  "author": "Your Name",
  "min_yago_version": "7.2.0"
}
```

### 3. Create `plugin.py`

```python
from yago.plugins.core import ToolPlugin

class MyPlugin(ToolPlugin):
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        return True

    async def execute(self, input_data=None, **kwargs):
        """Execute plugin logic"""
        return {"result": "success"}

    async def invoke(self, *args, **kwargs):
        """Tool invocation"""
        result = await self.execute(*args, **kwargs)
        return result["result"]

    def get_schema(self):
        """Tool schema"""
        return {
            "name": "my_tool",
            "description": "My tool",
            "parameters": {"type": "object"}
        }
```

### 4. Load and Use Plugin

```python
from pathlib import Path
from yago.plugins.core import get_manager

# Get manager
manager = get_manager()

# Load plugin
plugins = await manager.discover_and_load(Path("yago/plugins/my_plugin"))

# Initialize and enable
await manager.initialize_plugin("my_plugin")
await manager.enable_plugin("my_plugin")

# Execute
result = await manager.execute_plugin("my_plugin", {"input": "data"})
print(result)
```

## Plugin Development

### Plugin Metadata (plugin.json)

Required fields:
- `id` - Unique plugin identifier
- `name` - Human-readable name
- `version` - Semantic version (e.g., "1.0.0")
- `type` - Plugin type
- `description` - Short description
- `author` - Author name
- `min_yago_version` - Minimum YAGO version

Optional fields:
- `long_description` - Detailed description
- `homepage` - Plugin website
- `repository` - Source code repository
- `documentation` - Documentation URL
- `dependencies` - Python package dependencies
- `plugin_dependencies` - Required plugins
- `tags` - Search tags
- `capabilities` - Plugin capabilities
- `config_schema` - JSON schema for configuration
- `default_config` - Default configuration
- `auto_enable` - Enable on load
- `singleton` - Allow only one instance

### Plugin Implementation

Required methods:

```python
async def initialize(self) -> bool:
    """Initialize the plugin"""
    # Setup code here
    return True

async def execute(self, input_data: Any = None, **kwargs) -> Any:
    """Execute plugin functionality"""
    # Main logic here
    return result
```

Optional lifecycle methods:

```python
async def validate(self) -> bool:
    """Validate configuration"""
    return True

async def configure(self, config: Dict[str, Any]) -> bool:
    """Configure the plugin"""
    self.context.config.update(config)
    return True

async def enable(self) -> bool:
    """Enable the plugin"""
    await super().enable()
    return True

async def disable(self) -> bool:
    """Disable the plugin"""
    await super().disable()
    return True

async def cleanup(self) -> bool:
    """Cleanup resources"""
    return True

async def health_check(self) -> Dict[str, Any]:
    """Check plugin health"""
    health = await super().health_check()
    # Add custom health metrics
    return health
```

### Plugin Context

Access configuration and data:

```python
# Get configuration
api_key = self.context.get_config("api_key")
timeout = self.context.get_config("timeout", 30)

# Set/get context data
self.context.set_data("key", "value")
value = self.context.get_data("key")

# Access shared state
self.context.shared_state["key"] = "value"
```

### Dependencies

Python packages in `plugin.json`:

```json
{
  "dependencies": [
    "requests>=2.28.0",
    "pandas>=1.5.0"
  ]
}
```

Plugin dependencies:

```json
{
  "plugin_dependencies": [
    "required_plugin_id"
  ]
}
```

## API Reference

### REST API Endpoints

#### List Plugins
```
GET /api/v1/plugins
Query params: plugin_type, status
```

#### Get Plugin
```
GET /api/v1/plugins/{plugin_id}
```

#### Initialize Plugin
```
POST /api/v1/plugins/{plugin_id}/initialize
```

#### Enable Plugin
```
POST /api/v1/plugins/{plugin_id}/enable
```

#### Disable Plugin
```
POST /api/v1/plugins/{plugin_id}/disable
```

#### Configure Plugin
```
POST /api/v1/plugins/{plugin_id}/configure
Body: {"config": {...}}
```

#### Execute Plugin
```
POST /api/v1/plugins/{plugin_id}/execute
Body: {"input_data": {...}, "kwargs": {...}}
```

#### Health Check
```
GET /api/v1/plugins/{plugin_id}/health
```

#### Get Statistics
```
GET /api/v1/plugins/{plugin_id}/stats
```

#### Load Plugin
```
POST /api/v1/plugins/load
Body: {"plugin_path": "/path/to/plugin"}
```

### Python API

#### Plugin Manager

```python
from yago.plugins.core import get_manager

manager = get_manager()

# Load plugins
await manager.discover_and_load(plugin_dir)

# Initialize
await manager.initialize_plugin(plugin_id)
await manager.initialize_all()

# Enable/Disable
await manager.enable_plugin(plugin_id)
await manager.disable_plugin(plugin_id)

# Execute
result = await manager.execute_plugin(plugin_id, input_data, **kwargs)

# Configure
await manager.configure_plugin(plugin_id, config)

# Health
health = await manager.health_check_plugin(plugin_id)
all_health = await manager.health_check_all()

# Stats
stats = manager.get_plugin_stats(plugin_id)
all_stats = manager.get_all_stats()

# List
plugins = manager.list_plugins(plugin_type, status)

# Cleanup
await manager.cleanup_plugin(plugin_id)
await manager.cleanup_all()
```

#### Plugin Registry

```python
from yago.plugins.core import get_registry

registry = get_registry()

# Register
success = registry.register(plugin)

# Get
plugin = registry.get(plugin_id)
metadata = registry.get_metadata(plugin_id)

# Search
results = registry.search(query, plugin_type, tags, author)

# Filter
by_type = registry.get_by_type(PluginType.TOOL)
by_status = registry.get_by_status(PluginStatus.ACTIVE)

# Discover
discovered = registry.discover(plugin_dir)
all_discovered = registry.discover_all()

# Dependencies
order = registry.get_dependency_order()

# Stats
stats = registry.get_stats()
```

## Examples

See `/yago/plugins/examples/` for complete examples:

- **hello_world** - Basic tool plugin with configuration
- More examples coming soon!

## Best Practices

### 1. Error Handling

Always use try-except blocks:

```python
async def execute(self, input_data=None, **kwargs):
    try:
        # Logic here
        return {"success": True}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"success": False, "error": str(e)}
```

### 2. Logging

Use Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 3. Configuration Validation

Validate in `validate()` method:

```python
async def validate(self) -> bool:
    required_keys = ["api_key", "endpoint"]
    for key in required_keys:
        if not self.context.get_config(key):
            logger.error(f"Missing required config: {key}")
            return False
    return True
```

### 4. Resource Cleanup

Clean up in `cleanup()` method:

```python
async def cleanup(self) -> bool:
    # Close connections
    if hasattr(self, 'connection'):
        self.connection.close()

    # Save state
    self._save_state()

    return True
```

### 5. Testing

Write unit tests:

```python
import pytest
from yago.plugins.core import get_manager

@pytest.mark.asyncio
async def test_my_plugin():
    manager = get_manager()

    # Load
    plugins = await manager.discover_and_load("path/to/plugin")
    assert len(plugins) == 1

    # Initialize
    success = await manager.initialize_plugin("my_plugin")
    assert success

    # Execute
    result = await manager.execute_plugin("my_plugin", {"test": "data"})
    assert result["success"]
```

### 6. Documentation

Include docstrings:

```python
class MyPlugin(ToolPlugin):
    """
    Brief plugin description

    Features:
    - Feature 1
    - Feature 2

    Configuration:
    - api_key: API key for service
    - timeout: Request timeout in seconds
    """

    async def execute(self, input_data=None, **kwargs):
        """
        Execute the plugin

        Args:
            input_data: Input data dict
            **kwargs: Additional arguments

        Returns:
            Dict with result
        """
        pass
```

## Troubleshooting

### Plugin Not Loading

- Check `plugin.json` syntax
- Verify `plugin.py` contains valid Plugin class
- Check logs for error messages
- Ensure dependencies are installed

### Initialization Fails

- Check `initialize()` method
- Verify configuration is valid
- Check database connectivity
- Review error logs

### Execution Errors

- Check input data format
- Verify plugin is ACTIVE
- Check for missing dependencies
- Review execution logs

### Performance Issues

- Use async operations
- Implement caching
- Optimize database queries
- Monitor execution stats

## Support

- **Documentation**: https://yago.dev/docs
- **GitHub Issues**: https://github.com/yourusername/yago/issues
- **Discord**: https://discord.gg/yago
- **Email**: team@yago.dev

## Contributing

We welcome plugin contributions! Please:

1. Follow the plugin structure guidelines
2. Include comprehensive documentation
3. Add unit tests
4. Submit a pull request

## License

YAGO Plugin System is part of YAGO and follows the same license.
