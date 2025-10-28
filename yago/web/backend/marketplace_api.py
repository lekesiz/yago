"""
YAGO v8.0 - Marketplace API
RESTful API for marketplace operations
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import uuid

from yago.marketplace import (
    MarketplaceRegistry,
    MarketplaceStore,
    PackageInstaller,
    ItemValidator,
    Plugin,
    Template,
    Integration,
    Review,
    ItemType,
    ItemCategory,
    ItemStatus,
    SearchFilters,
    SearchSort,
)
from yago.marketplace.registry import get_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/marketplace", tags=["Marketplace"])

# Initialize components
registry = get_registry()
store = MarketplaceStore(registry)
installer = PackageInstaller()
validator = ItemValidator()


# Request Models

class PluginCreateRequest(BaseModel):
    """Request to create a plugin"""
    name: str
    description: str
    category: str
    tags: List[str] = []
    version: str = "1.0.0"
    author: str
    entry_point: str
    plugin_type: str
    license: str = "MIT"


class TemplateCreateRequest(BaseModel):
    """Request to create a template"""
    name: str
    description: str
    category: str
    tags: List[str] = []
    version: str = "1.0.0"
    author: str
    template_type: str
    variables: List[str] = []
    license: str = "MIT"


class IntegrationCreateRequest(BaseModel):
    """Request to create an integration"""
    name: str
    description: str
    category: str
    tags: List[str] = []
    version: str = "1.0.0"
    author: str
    service_name: str
    authentication_type: str
    webhook_support: bool = False
    license: str = "MIT"


class ReviewCreateRequest(BaseModel):
    """Request to create a review"""
    item_id: str
    rating: float
    title: str
    content: str
    user_id: str = "anonymous"
    username: str = "Anonymous"


class InstallRequest(BaseModel):
    """Request to install an item"""
    item_id: str
    auto_update: bool = False
    configuration: Optional[Dict[str, Any]] = None


# Endpoints

@router.get("/items")
async def list_items(
    item_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """
    List marketplace items

    Args:
        item_type: Filter by type (plugin, template, integration)
        category: Filter by category
        status: Filter by status
        limit: Maximum items to return

    Returns:
        List of marketplace items
    """
    try:
        # Convert strings to enums
        type_filter = ItemType(item_type) if item_type else None
        category_filter = ItemCategory(category) if category else None
        status_filter = ItemStatus(status) if status else None

        items = registry.list_items(
            item_type=type_filter,
            category=category_filter,
            status=status_filter,
            limit=limit
        )

        return {
            "total": len(items),
            "items": [
                {
                    "item_id": item.item_id,
                    "item_type": item.item_type.value,
                    "name": item.name,
                    "description": item.description,
                    "category": item.category.value,
                    "tags": item.tags,
                    "version": item.version,
                    "author": item.author,
                    "status": item.status.value,
                    "downloads": item.downloads,
                    "rating": item.rating,
                    "review_count": item.review_count
                }
                for item in items
            ]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error listing items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list items"
        )


@router.get("/items/{item_id}")
async def get_item(item_id: str):
    """Get item details"""
    try:
        item = registry.get_item(item_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        return {
            "item_id": item.item_id,
            "item_type": item.item_type.value,
            "name": item.name,
            "description": item.description,
            "long_description": item.long_description,
            "category": item.category.value,
            "tags": item.tags,
            "version": item.version,
            "author": item.author,
            "author_email": item.author_email,
            "organization": item.organization,
            "status": item.status.value,
            "published_at": item.published_at.isoformat() if item.published_at else None,
            "updated_at": item.updated_at.isoformat(),
            "downloads": item.downloads,
            "rating": item.rating,
            "review_count": item.review_count,
            "homepage": str(item.homepage) if item.homepage else None,
            "documentation_url": str(item.documentation_url) if item.documentation_url else None,
            "repository_url": str(item.repository_url) if item.repository_url else None,
            "dependencies": item.dependencies,
            "license": item.license,
            "keywords": item.keywords
        }

    except Exception as e:
        logger.error(f"Error getting item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get item"
        )


@router.get("/search")
async def search_items(
    q: str = Query(..., min_length=1),
    item_type: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "relevance",
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search marketplace items

    Args:
        q: Search query
        item_type: Filter by type
        category: Filter by category
        tags: Comma-separated tags
        min_rating: Minimum rating
        sort_by: Sort method (relevance, downloads, rating, recent, name)
        limit: Maximum results

    Returns:
        Search results
    """
    try:
        # Build filters
        filters = SearchFilters()

        if item_type:
            filters.item_type = ItemType(item_type)

        if category:
            filters.category = ItemCategory(category)

        if tags:
            filters.tags = [t.strip() for t in tags.split(',')]

        if min_rating is not None:
            filters.min_rating = min_rating

        # Parse sort
        sort = SearchSort(sort_by)

        # Search
        items = registry.search_items(
            query=q,
            filters=filters,
            sort_by=sort,
            limit=limit
        )

        return {
            "query": q,
            "total": len(items),
            "items": [
                {
                    "item_id": item.item_id,
                    "item_type": item.item_type.value,
                    "name": item.name,
                    "description": item.description,
                    "category": item.category.value,
                    "tags": item.tags,
                    "version": item.version,
                    "author": item.author,
                    "downloads": item.downloads,
                    "rating": item.rating,
                    "review_count": item.review_count
                }
                for item in items
            ]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error searching items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search items"
        )


@router.post("/plugins")
async def create_plugin(request: PluginCreateRequest):
    """Create a new plugin"""
    try:
        plugin = Plugin(
            item_id=f"plugin_{uuid.uuid4().hex[:12]}",
            name=request.name,
            description=request.description,
            category=ItemCategory(request.category),
            tags=request.tags,
            version=request.version,
            author=request.author,
            entry_point=request.entry_point,
            plugin_type=request.plugin_type,
            license=request.license,
            status=ItemStatus.DRAFT
        )

        # Validate
        is_valid, errors = validator.validate_item(plugin)

        if not is_valid:
            return {
                "success": False,
                "message": "Validation failed",
                "errors": [e.to_dict() for e in errors]
            }

        # Register
        success = registry.register_item(plugin)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register plugin"
            )

        return {
            "success": True,
            "item_id": plugin.item_id,
            "message": f"Plugin '{plugin.name}' created successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating plugin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create plugin"
        )


@router.post("/templates")
async def create_template(request: TemplateCreateRequest):
    """Create a new template"""
    try:
        template = Template(
            item_id=f"template_{uuid.uuid4().hex[:12]}",
            name=request.name,
            description=request.description,
            category=ItemCategory(request.category),
            tags=request.tags,
            version=request.version,
            author=request.author,
            template_type=request.template_type,
            variables=request.variables,
            license=request.license,
            status=ItemStatus.DRAFT
        )

        # Validate
        is_valid, errors = validator.validate_item(template)

        if not is_valid:
            return {
                "success": False,
                "message": "Validation failed",
                "errors": [e.to_dict() for e in errors]
            }

        # Register
        success = registry.register_item(template)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register template"
            )

        return {
            "success": True,
            "item_id": template.item_id,
            "message": f"Template '{template.name}' created successfully"
        }

    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template"
        )


@router.post("/integrations")
async def create_integration(request: IntegrationCreateRequest):
    """Create a new integration"""
    try:
        integration = Integration(
            item_id=f"integration_{uuid.uuid4().hex[:12]}",
            name=request.name,
            description=request.description,
            category=ItemCategory(request.category),
            tags=request.tags,
            version=request.version,
            author=request.author,
            service_name=request.service_name,
            authentication_type=request.authentication_type,
            webhook_support=request.webhook_support,
            license=request.license,
            status=ItemStatus.DRAFT
        )

        # Validate
        is_valid, errors = validator.validate_item(integration)

        if not is_valid:
            return {
                "success": False,
                "message": "Validation failed",
                "errors": [e.to_dict() for e in errors]
            }

        # Register
        success = registry.register_item(integration)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register integration"
            )

        return {
            "success": True,
            "item_id": integration.item_id,
            "message": f"Integration '{integration.name}' created successfully"
        }

    except Exception as e:
        logger.error(f"Error creating integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create integration"
        )


@router.get("/items/{item_id}/reviews")
async def get_reviews(item_id: str, limit: int = Query(10, ge=1, le=50)):
    """Get reviews for an item"""
    try:
        reviews = registry.get_reviews(item_id, limit=limit)

        return {
            "item_id": item_id,
            "total": len(reviews),
            "reviews": [
                {
                    "review_id": r.review_id,
                    "user_id": r.user_id,
                    "username": r.username,
                    "rating": r.rating,
                    "title": r.title,
                    "content": r.content,
                    "created_at": r.created_at.isoformat(),
                    "helpful_count": r.helpful_count,
                    "verified_purchase": r.verified_purchase
                }
                for r in reviews
            ]
        }

    except Exception as e:
        logger.error(f"Error getting reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reviews"
        )


@router.post("/reviews")
async def create_review(request: ReviewCreateRequest):
    """Create a review"""
    try:
        review = Review(
            review_id=f"review_{uuid.uuid4().hex[:12]}",
            item_id=request.item_id,
            user_id=request.user_id,
            username=request.username,
            rating=request.rating,
            title=request.title,
            content=request.content
        )

        success = registry.add_review(review)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add review"
            )

        return {
            "success": True,
            "review_id": review.review_id,
            "message": "Review added successfully"
        }

    except Exception as e:
        logger.error(f"Error creating review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )


@router.post("/install")
async def install_item(request: InstallRequest):
    """Install a marketplace item"""
    try:
        installation = store.install_item(
            item_id=request.item_id,
            auto_update=request.auto_update,
            configuration=request.configuration
        )

        if not installation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Installation failed"
            )

        return {
            "success": True,
            "installation_id": installation.installation_id,
            "item_id": installation.item_id,
            "version": installation.version,
            "installation_path": installation.installation_path,
            "message": "Item installed successfully"
        }

    except Exception as e:
        logger.error(f"Error installing item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to install item"
        )


@router.delete("/install/{item_id}")
async def uninstall_item(item_id: str):
    """Uninstall an item"""
    try:
        success = store.uninstall_item(item_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uninstallation failed"
            )

        return {
            "success": True,
            "message": "Item uninstalled successfully"
        }

    except Exception as e:
        logger.error(f"Error uninstalling item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to uninstall item"
        )


@router.get("/installations")
async def list_installations(
    item_type: Optional[str] = None,
    active_only: bool = True
):
    """List all installations"""
    try:
        type_filter = ItemType(item_type) if item_type else None

        installations = store.list_installations(
            item_type=type_filter,
            active_only=active_only
        )

        return {
            "total": len(installations),
            "installations": [
                {
                    "installation_id": i.installation_id,
                    "item_id": i.item_id,
                    "item_type": i.item_type.value,
                    "version": i.version,
                    "installed_at": i.installed_at.isoformat(),
                    "active": i.active,
                    "auto_update": i.auto_update,
                    "installation_path": i.installation_path
                }
                for i in installations
            ]
        }

    except Exception as e:
        logger.error(f"Error listing installations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list installations"
        )


@router.get("/updates")
async def check_updates():
    """Check for available updates"""
    try:
        updates = store.check_updates()

        return {
            "total": len(updates),
            "updates": updates
        }

    except Exception as e:
        logger.error(f"Error checking updates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check updates"
        )


@router.get("/featured")
async def get_featured(limit: int = Query(10, ge=1, le=50)):
    """Get featured items"""
    try:
        items = registry.get_featured_items(limit=limit)

        return {
            "total": len(items),
            "items": [
                {
                    "item_id": item.item_id,
                    "item_type": item.item_type.value,
                    "name": item.name,
                    "description": item.description,
                    "category": item.category.value,
                    "rating": item.rating,
                    "downloads": item.downloads
                }
                for item in items
            ]
        }

    except Exception as e:
        logger.error(f"Error getting featured items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get featured items"
        )


@router.get("/stats")
async def get_stats():
    """Get marketplace statistics"""
    try:
        stats = registry.get_stats()

        return {
            "total_items": stats.total_items,
            "total_downloads": stats.total_downloads,
            "total_reviews": stats.total_reviews,
            "items_by_type": stats.items_by_type,
            "items_by_category": stats.items_by_category,
            "most_downloaded": stats.most_downloaded,
            "highest_rated": stats.highest_rated,
            "recently_added": stats.recently_added
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )


@router.get("/categories")
async def list_categories():
    """List all categories"""
    return {
        "categories": [
            {
                "id": c.value,
                "name": c.value.replace("_", " ").title()
            }
            for c in ItemCategory
        ]
    }


@router.post("/items/{item_id}/validate")
async def validate_item(item_id: str):
    """Validate an item"""
    try:
        item = registry.get_item(item_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        report = validator.get_validation_report(item)

        return report

    except Exception as e:
        logger.error(f"Error validating item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate item"
        )


# Export router
marketplace_router = router
