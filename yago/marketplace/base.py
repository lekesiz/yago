"""
YAGO v8.0 - Marketplace Base Classes
Core abstractions for the marketplace system
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class ItemType(str, Enum):
    """Types of marketplace items"""
    PLUGIN = "plugin"
    TEMPLATE = "template"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"


class ItemCategory(str, Enum):
    """Categories for marketplace items"""
    DEVELOPMENT = "development"
    DATA_PROCESSING = "data_processing"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    AUTOMATION = "automation"
    MONITORING = "monitoring"
    SECURITY = "security"
    AI_ML = "ai_ml"
    UTILITIES = "utilities"
    OTHER = "other"


class ItemStatus(str, Enum):
    """Status of marketplace items"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


class Version(BaseModel):
    """Version information"""
    version: str = Field(description="Semantic version (e.g., 1.2.3)")
    release_date: datetime = Field(default_factory=datetime.utcnow)
    changelog: str = Field(description="Changes in this version")
    download_url: Optional[HttpUrl] = None
    checksum: Optional[str] = None
    min_yago_version: Optional[str] = None
    max_yago_version: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.2.3",
                "changelog": "Fixed bug in authentication",
                "min_yago_version": "8.0.0"
            }
        }


class MarketplaceItem(BaseModel):
    """
    Base class for all marketplace items
    """
    item_id: str = Field(description="Unique item identifier")
    item_type: ItemType = Field(description="Type of item")
    name: str = Field(description="Item name", min_length=3, max_length=100)
    description: str = Field(description="Item description", max_length=500)
    long_description: Optional[str] = None

    # Metadata
    category: ItemCategory = Field(description="Item category")
    tags: List[str] = Field(default_factory=list, max_length=10)
    version: str = Field(description="Current version")
    versions: List[Version] = Field(default_factory=list)

    # Author information
    author: str = Field(description="Author name")
    author_email: Optional[str] = None
    author_url: Optional[HttpUrl] = None
    organization: Optional[str] = None

    # Status
    status: ItemStatus = Field(default=ItemStatus.DRAFT)
    published_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Statistics
    downloads: int = Field(default=0, ge=0)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    review_count: int = Field(default=0, ge=0)

    # URLs
    homepage: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = None
    repository_url: Optional[HttpUrl] = None
    issues_url: Optional[HttpUrl] = None

    # Requirements
    dependencies: List[str] = Field(default_factory=list)
    python_version: Optional[str] = None
    license: str = Field(default="MIT")

    # Additional metadata
    screenshots: List[HttpUrl] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "item_abc123",
                "item_type": "plugin",
                "name": "Slack Integration",
                "description": "Send notifications to Slack channels",
                "category": "communication",
                "tags": ["slack", "notifications", "communication"],
                "version": "1.0.0",
                "author": "John Doe",
                "status": "published",
                "rating": 4.5,
                "downloads": 1250
            }
        }


class Plugin(MarketplaceItem):
    """
    Plugin marketplace item
    """
    item_type: ItemType = Field(default=ItemType.PLUGIN, frozen=True)

    # Plugin-specific fields
    entry_point: str = Field(description="Main entry point (e.g., module:class)")
    plugin_type: str = Field(description="Plugin type (e.g., agent, tool, model)")
    configuration_schema: Optional[Dict[str, Any]] = None
    hooks: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "plugin_abc123",
                "name": "Custom LLM Plugin",
                "entry_point": "custom_llm:CustomLLM",
                "plugin_type": "model"
            }
        }


class Template(MarketplaceItem):
    """
    Template marketplace item
    """
    item_type: ItemType = Field(default=ItemType.TEMPLATE, frozen=True)

    # Template-specific fields
    template_type: str = Field(description="Template type (e.g., project, agent, workflow)")
    template_files: List[str] = Field(default_factory=list)
    variables: List[str] = Field(default_factory=list)
    instructions: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "template_abc123",
                "name": "Web Scraper Template",
                "template_type": "agent",
                "variables": ["target_url", "selector"]
            }
        }


class Integration(MarketplaceItem):
    """
    Integration marketplace item
    """
    item_type: ItemType = Field(default=ItemType.INTEGRATION, frozen=True)

    # Integration-specific fields
    service_name: str = Field(description="Name of the service to integrate")
    api_version: Optional[str] = None
    authentication_type: str = Field(description="Auth type (oauth, api_key, basic)")
    endpoints: List[Dict[str, str]] = Field(default_factory=list)
    webhook_support: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "integration_abc123",
                "name": "GitHub Integration",
                "service_name": "GitHub",
                "authentication_type": "oauth",
                "webhook_support": True
            }
        }


class Review(BaseModel):
    """
    User review for marketplace item
    """
    review_id: str = Field(description="Unique review identifier")
    item_id: str = Field(description="Item being reviewed")
    user_id: str = Field(description="User who wrote the review")
    username: str = Field(description="Username for display")

    # Review content
    rating: float = Field(ge=0.0, le=5.0, description="Rating (0-5 stars)")
    title: str = Field(description="Review title", max_length=100)
    content: str = Field(description="Review content", max_length=2000)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    helpful_count: int = Field(default=0, ge=0)
    verified_purchase: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "review_id": "review_abc123",
                "item_id": "plugin_abc123",
                "user_id": "user_123",
                "username": "johndoe",
                "rating": 5.0,
                "title": "Excellent plugin!",
                "content": "This plugin saved me hours of work. Highly recommended!",
                "verified_purchase": True
            }
        }


class InstallationRecord(BaseModel):
    """
    Record of an installation
    """
    installation_id: str = Field(description="Unique installation identifier")
    item_id: str = Field(description="Installed item")
    item_type: ItemType = Field(description="Type of item")
    version: str = Field(description="Installed version")

    # Installation details
    installed_at: datetime = Field(default_factory=datetime.utcnow)
    installed_by: Optional[str] = None
    installation_path: str = Field(description="Installation path")

    # Status
    active: bool = Field(default=True)
    auto_update: bool = Field(default=False)
    last_updated: Optional[datetime] = None

    # Metadata
    configuration: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "installation_id": "install_abc123",
                "item_id": "plugin_abc123",
                "item_type": "plugin",
                "version": "1.0.0",
                "installation_path": "/plugins/custom_llm",
                "active": True
            }
        }


class SearchFilters(BaseModel):
    """
    Filters for marketplace search
    """
    item_type: Optional[ItemType] = None
    category: Optional[ItemCategory] = None
    tags: Optional[List[str]] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    author: Optional[str] = None
    free_only: bool = Field(default=False)
    verified_only: bool = Field(default=False)


class SearchSort(str, Enum):
    """Sort options for marketplace search"""
    RELEVANCE = "relevance"
    DOWNLOADS = "downloads"
    RATING = "rating"
    RECENT = "recent"
    NAME = "name"


class MarketplaceStats(BaseModel):
    """
    Statistics for the marketplace
    """
    total_items: int = Field(default=0)
    total_downloads: int = Field(default=0)
    total_reviews: int = Field(default=0)

    # By type
    items_by_type: Dict[str, int] = Field(default_factory=dict)
    items_by_category: Dict[str, int] = Field(default_factory=dict)

    # Top items
    most_downloaded: List[Dict[str, Any]] = Field(default_factory=list)
    highest_rated: List[Dict[str, Any]] = Field(default_factory=list)
    recently_added: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "total_items": 150,
                "total_downloads": 12500,
                "total_reviews": 450,
                "items_by_type": {
                    "plugin": 80,
                    "template": 40,
                    "integration": 30
                }
            }
        }
