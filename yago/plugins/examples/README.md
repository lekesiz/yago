# YAGO Plugin Examples

This directory contains example plugins demonstrating various YAGO plugin capabilities.

## Available Examples

### 1. Hello World Plugin (`hello_world/`)

**Type:** Tool Plugin
**Purpose:** Demonstrates basic plugin structure and functionality

**Features:**
- Simple initialization and cleanup
- Configuration handling
- Context usage
- Multi-language support
- Health monitoring
- Tool schema for LLM integration

**Usage:**
```python
from yago.plugins.core import get_manager

# Get plugin manager
manager = get_manager()

# Load plugin
await manager.discover_and_load("yago/plugins/examples/hello_world")

# Initialize and enable
await manager.initialize_plugin("hello_world")
await manager.enable_plugin("hello_world")

# Execute
result = await manager.execute_plugin("hello_world", {"name": "Alice"})
print(result["greeting"])  # "Hello Alice! Nice to see you!"

# Configure
await manager.configure_plugin("hello_world", {
    "greeting_style": "formal",
    "language": "fr"
})

# Execute again
result = await manager.execute_plugin("hello_world", {"name": "Bob"})
print(result["greeting"])  # "Bonjour, Bob. Comment puis-je vous aider aujourd'hui?"
```

## Plugin Structure

Each plugin directory should contain:

```
plugin_name/
├── plugin.json          # Plugin metadata and configuration
├── plugin.py            # Plugin implementation
├── README.md            # Plugin documentation (optional)
├── requirements.txt     # Python dependencies (optional)
└── tests/              # Plugin tests (optional)
    └── test_plugin.py
```

### plugin.json

Required metadata file:

```json
{
  "id": "unique_plugin_id",
  "name": "Human Readable Name",
  "version": "1.0.0",
  "type": "tool",
  "description": "Short description",
  "author": "Your Name",
  "min_yago_version": "7.2.0",
  "dependencies": [],
  "plugin_dependencies": [],
  "default_config": {}
}
```

### plugin.py

Must contain a class inheriting from one of:
- `Plugin` - Base class
- `AgentPlugin` - For custom agents
- `DashboardPlugin` - For dashboard widgets
- `IntegrationPlugin` - For external service integrations
- `WorkflowPlugin` - For custom workflow steps
- `ToolPlugin` - For agent tools

Required methods:
```python
async def initialize(self) -> bool:
    """Initialize the plugin"""
    pass

async def execute(self, input_data: Any = None, **kwargs) -> Any:
    """Execute plugin functionality"""
    pass
```

Optional lifecycle methods:
```python
async def validate(self) -> bool:
    """Validate configuration"""
    pass

async def configure(self, config: Dict[str, Any]) -> bool:
    """Configure the plugin"""
    pass

async def enable(self) -> bool:
    """Enable the plugin"""
    pass

async def disable(self) -> bool:
    """Disable the plugin"""
    pass

async def cleanup(self) -> bool:
    """Cleanup resources"""
    pass

async def health_check(self) -> Dict[str, Any]:
    """Check plugin health"""
    pass
```

## Creating Your Own Plugin

1. **Create Plugin Directory:**
   ```bash
   mkdir -p yago/plugins/examples/my_plugin
   cd yago/plugins/examples/my_plugin
   ```

2. **Create plugin.json:**
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

3. **Create plugin.py:**
   ```python
   from yago.plugins.core import ToolPlugin

   class MyPlugin(ToolPlugin):
       async def initialize(self) -> bool:
           return True

       async def execute(self, input_data=None, **kwargs):
           return {"result": "success"}

       async def invoke(self, *args, **kwargs):
           result = await self.execute(*args, **kwargs)
           return result["result"]

       def get_schema(self):
           return {
               "name": "my_tool",
               "description": "My awesome tool",
               "parameters": {"type": "object"}
           }
   ```

4. **Test Your Plugin:**
   ```python
   from pathlib import Path
   from yago.plugins.core import get_manager

   manager = get_manager()

   # Load
   plugin_path = Path("yago/plugins/examples/my_plugin")
   await manager.discover_and_load(plugin_path)

   # Initialize and enable
   await manager.initialize_plugin("my_plugin")
   await manager.enable_plugin("my_plugin")

   # Execute
   result = await manager.execute_plugin("my_plugin")
   print(result)
   ```

## Plugin Types

### Tool Plugin
For agent tools and utilities:
```python
from yago.plugins.core import ToolPlugin

class MyToolPlugin(ToolPlugin):
    async def invoke(self, *args, **kwargs) -> Any:
        """Tool invocation"""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """LLM tool schema"""
        pass
```

### Agent Plugin
For custom AI agents:
```python
from yago.plugins.core import AgentPlugin

class MyAgentPlugin(AgentPlugin):
    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent task"""
        pass
```

### Dashboard Plugin
For dashboard widgets:
```python
from yago.plugins.core import DashboardPlugin

class MyDashboardPlugin(DashboardPlugin):
    def render(self) -> Dict[str, Any]:
        """Render dashboard component"""
        pass

    def get_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        pass
```

### Integration Plugin
For external service integrations:
```python
from yago.plugins.core import IntegrationPlugin

class MyIntegrationPlugin(IntegrationPlugin):
    async def connect(self) -> bool:
        """Connect to service"""
        pass

    async def disconnect(self) -> bool:
        """Disconnect from service"""
        pass

    async def sync(self, data: Any) -> bool:
        """Sync data"""
        pass
```

### Workflow Plugin
For custom workflow steps:
```python
from yago.plugins.core import WorkflowPlugin

class MyWorkflowPlugin(WorkflowPlugin):
    async def run_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow step"""
        pass
```

## Best Practices

1. **Error Handling:** Always use try-except blocks and log errors
2. **Logging:** Use Python's logging module for debugging
3. **Configuration:** Validate configuration in `validate()` method
4. **Resources:** Clean up resources in `cleanup()` method
5. **Testing:** Write unit tests for your plugin
6. **Documentation:** Include docstrings and README
7. **Versioning:** Follow semantic versioning (semver)
8. **Dependencies:** Minimize external dependencies

## Testing Plugins

```python
import pytest
from yago.plugins.core import get_manager, PluginMetadata

@pytest.mark.asyncio
async def test_my_plugin():
    # Load plugin
    manager = get_manager()
    plugins = await manager.discover_and_load("path/to/plugin")

    assert len(plugins) == 1

    # Initialize
    success = await manager.initialize_plugin("my_plugin")
    assert success

    # Enable
    success = await manager.enable_plugin("my_plugin")
    assert success

    # Execute
    result = await manager.execute_plugin("my_plugin", {"test": "data"})
    assert result is not None

    # Health check
    health = await manager.health_check_plugin("my_plugin")
    assert health["healthy"]

    # Cleanup
    success = await manager.cleanup_plugin("my_plugin")
    assert success
```

## Resources

- [YAGO Plugin Documentation](https://yago.dev/docs/plugins)
- [Plugin API Reference](https://yago.dev/docs/api/plugins)
- [Community Plugins](https://yago.dev/plugins)

## Contributing

Want to contribute an example plugin? Please:

1. Follow the plugin structure guidelines
2. Include comprehensive documentation
3. Add unit tests
4. Submit a pull request

## Support

- GitHub Issues: https://github.com/yourusername/yago/issues
- Discord: https://discord.gg/yago
- Email: team@yago.dev
