"""
YAGO v7.2 - Plugin Base Classes
Base classes and interfaces for plugin development
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class PluginType(str, Enum):
    """Types of plugins supported by YAGO"""
    AGENT = "agent"              # Custom agent implementations
    DASHBOARD = "dashboard"      # Dashboard widgets/panels
    INTEGRATION = "integration"  # External service integrations
    WORKFLOW = "workflow"        # Custom workflow steps
    TOOL = "tool"               # Agent tools
    PREPROCESSOR = "preprocessor" # Data preprocessors
    POSTPROCESSOR = "postprocessor" # Data postprocessors
    MIDDLEWARE = "middleware"    # Request/response middleware
    EXTENSION = "extension"      # General extensions


class PluginStatus(str, Enum):
    """Plugin lifecycle status"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class PluginMetadata(BaseModel):
    """Plugin metadata and configuration"""

    # Identity
    id: str = Field(..., description="Unique plugin identifier")
    name: str = Field(..., description="Human-readable plugin name")
    version: str = Field(..., description="Plugin version (semver)")

    # Classification
    type: PluginType = Field(..., description="Plugin type")
    category: str = Field(default="general", description="Plugin category")

    # Description
    description: str = Field(..., description="Short description")
    long_description: Optional[str] = Field(None, description="Detailed description")

    # Author & Links
    author: str = Field(..., description="Plugin author")
    author_email: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    documentation: Optional[str] = None

    # Requirements
    min_yago_version: str = Field(default="7.2.0", description="Minimum YAGO version")
    max_yago_version: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list, description="Python package dependencies")
    plugin_dependencies: List[str] = Field(default_factory=list, description="Other required plugins")

    # Features
    tags: List[str] = Field(default_factory=list, description="Plugin tags for discovery")
    capabilities: List[str] = Field(default_factory=list, description="Plugin capabilities")

    # Configuration
    configurable: bool = Field(default=True, description="Can be configured")
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Dict[str, Any] = Field(default_factory=dict)

    # Lifecycle
    auto_enable: bool = Field(default=False, description="Enable on load")
    singleton: bool = Field(default=True, description="Single instance only")

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PluginContext:
    """Context provided to plugins"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.data: Dict[str, Any] = {}
        self.shared_state: Dict[str, Any] = {}

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set_data(self, key: str, value: Any):
        """Set context data"""
        self.data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get context data"""
        return self.data.get(key, default)


class Plugin(ABC):
    """
    Base class for all YAGO plugins

    All plugins must inherit from this class and implement required methods.
    """

    def __init__(self, metadata: PluginMetadata, context: Optional[PluginContext] = None):
        self.metadata = metadata
        self.context = context or PluginContext()
        self.status = PluginStatus.UNLOADED
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the plugin

        Called when plugin is loaded. Perform setup here.

        Returns:
            bool: True if initialization successful
        """
        pass

    @abstractmethod
    async def execute(self, input_data: Any = None, **kwargs) -> Any:
        """
        Execute plugin functionality

        Main entry point for plugin execution.

        Args:
            input_data: Input data for the plugin
            **kwargs: Additional keyword arguments

        Returns:
            Any: Plugin execution result
        """
        pass

    async def validate(self) -> bool:
        """
        Validate plugin configuration and dependencies

        Returns:
            bool: True if validation successful
        """
        return True

    async def configure(self, config: Dict[str, Any]) -> bool:
        """
        Configure the plugin

        Args:
            config: Configuration dictionary

        Returns:
            bool: True if configuration successful
        """
        self.context.config.update(config)
        return True

    async def enable(self) -> bool:
        """
        Enable the plugin

        Called when plugin is activated.

        Returns:
            bool: True if enabled successfully
        """
        self.status = PluginStatus.ACTIVE
        return True

    async def disable(self) -> bool:
        """
        Disable the plugin

        Called when plugin is deactivated.

        Returns:
            bool: True if disabled successfully
        """
        self.status = PluginStatus.DISABLED
        return True

    async def cleanup(self) -> bool:
        """
        Cleanup plugin resources

        Called when plugin is unloaded. Clean up resources here.

        Returns:
            bool: True if cleanup successful
        """
        return True

    async def health_check(self) -> Dict[str, Any]:
        """
        Check plugin health

        Returns:
            Dict with health status information
        """
        return {
            "status": self.status.value,
            "initialized": self._initialized,
            "healthy": self.status == PluginStatus.ACTIVE
        }

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "version": self.metadata.version,
            "type": self.metadata.type.value,
            "status": self.status.value,
            "author": self.metadata.author,
            "description": self.metadata.description,
        }


class AgentPlugin(Plugin):
    """Base class for agent plugins"""

    @abstractmethod
    async def process(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent task"""
        pass


class DashboardPlugin(Plugin):
    """Base class for dashboard plugins"""

    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """Render dashboard component"""
        pass

    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        pass


class IntegrationPlugin(Plugin):
    """Base class for integration plugins"""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to external service"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from external service"""
        pass

    @abstractmethod
    async def sync(self, data: Any) -> bool:
        """Sync data with external service"""
        pass


class WorkflowPlugin(Plugin):
    """Base class for workflow plugins"""

    @abstractmethod
    async def run_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow step"""
        pass


class ToolPlugin(Plugin):
    """Base class for tool plugins"""

    @abstractmethod
    async def invoke(self, *args, **kwargs) -> Any:
        """Invoke tool functionality"""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for LLM"""
        pass
