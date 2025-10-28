"""
YAGO v8.0 - Marketplace Registry
Central registry for marketplace items
"""

import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime

from .base import (
    MarketplaceItem,
    Plugin,
    Template,
    Integration,
    Review,
    ItemType,
    ItemCategory,
    ItemStatus,
    SearchFilters,
    SearchSort,
    MarketplaceStats,
)

logger = logging.getLogger(__name__)


class MarketplaceRegistry:
    """
    Central registry for all marketplace items
    """

    def __init__(self):
        # Items storage
        self.items: Dict[str, MarketplaceItem] = {}
        self.reviews: Dict[str, List[Review]] = {}  # item_id -> reviews

        # Pre-populate with some items
        self._populate_initial_items()

    def register_item(self, item: MarketplaceItem) -> bool:
        """
        Register a new item

        Args:
            item: Marketplace item to register

        Returns:
            True if successful
        """
        if item.item_id in self.items:
            logger.warning(f"Item already registered: {item.item_id}")
            return False

        self.items[item.item_id] = item
        self.reviews[item.item_id] = []

        logger.info(
            f"Registered {item.item_type.value}: {item.name} ({item.item_id})"
        )

        return True

    def update_item(self, item_id: str, updates: Dict) -> bool:
        """
        Update an existing item

        Args:
            item_id: Item identifier
            updates: Dictionary of updates

        Returns:
            True if successful
        """
        if item_id not in self.items:
            logger.error(f"Item not found: {item_id}")
            return False

        item = self.items[item_id]

        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)

        item.updated_at = datetime.utcnow()

        logger.info(f"Updated item: {item_id}")
        return True

    def get_item(self, item_id: str) -> Optional[MarketplaceItem]:
        """Get item by ID"""
        return self.items.get(item_id)

    def list_items(
        self,
        item_type: Optional[ItemType] = None,
        category: Optional[ItemCategory] = None,
        status: Optional[ItemStatus] = None,
        limit: Optional[int] = None
    ) -> List[MarketplaceItem]:
        """
        List items with filters

        Args:
            item_type: Filter by type
            category: Filter by category
            status: Filter by status
            limit: Maximum items to return

        Returns:
            List of marketplace items
        """
        items = list(self.items.values())

        # Apply filters
        if item_type:
            items = [i for i in items if i.item_type == item_type]

        if category:
            items = [i for i in items if i.category == category]

        if status:
            items = [i for i in items if i.status == status]
        else:
            # Default: only published items
            items = [i for i in items if i.status == ItemStatus.PUBLISHED]

        # Sort by downloads (most popular first)
        items.sort(key=lambda i: i.downloads, reverse=True)

        # Apply limit
        if limit:
            items = items[:limit]

        return items

    def search_items(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        sort_by: SearchSort = SearchSort.RELEVANCE,
        limit: int = 20
    ) -> List[MarketplaceItem]:
        """
        Search for items

        Args:
            query: Search query
            filters: Search filters
            sort_by: Sort method
            limit: Maximum results

        Returns:
            List of matching items
        """
        items = list(self.items.values())

        # Apply filters
        if filters:
            if filters.item_type:
                items = [i for i in items if i.item_type == filters.item_type]

            if filters.category:
                items = [i for i in items if i.category == filters.category]

            if filters.tags:
                items = [
                    i for i in items
                    if any(tag in i.tags for tag in filters.tags)
                ]

            if filters.min_rating:
                items = [i for i in items if i.rating >= filters.min_rating]

            if filters.author:
                items = [i for i in items if i.author == filters.author]

        # Only published items
        items = [i for i in items if i.status == ItemStatus.PUBLISHED]

        # Search in name, description, tags
        if query:
            query_lower = query.lower()
            items = [
                i for i in items
                if (query_lower in i.name.lower() or
                    query_lower in i.description.lower() or
                    any(query_lower in tag.lower() for tag in i.tags) or
                    any(query_lower in kw.lower() for kw in i.keywords))
            ]

        # Sort
        if sort_by == SearchSort.DOWNLOADS:
            items.sort(key=lambda i: i.downloads, reverse=True)
        elif sort_by == SearchSort.RATING:
            items.sort(key=lambda i: i.rating, reverse=True)
        elif sort_by == SearchSort.RECENT:
            items.sort(key=lambda i: i.published_at or datetime.min, reverse=True)
        elif sort_by == SearchSort.NAME:
            items.sort(key=lambda i: i.name.lower())
        # RELEVANCE: keep order from search

        return items[:limit]

    def add_review(self, review: Review) -> bool:
        """
        Add a review for an item

        Args:
            review: Review to add

        Returns:
            True if successful
        """
        if review.item_id not in self.items:
            logger.error(f"Item not found: {review.item_id}")
            return False

        self.reviews[review.item_id].append(review)

        # Update item rating
        self._update_item_rating(review.item_id)

        logger.info(f"Added review for item: {review.item_id}")
        return True

    def get_reviews(
        self,
        item_id: str,
        limit: Optional[int] = None
    ) -> List[Review]:
        """Get reviews for an item"""
        reviews = self.reviews.get(item_id, [])

        # Sort by helpful count
        reviews.sort(key=lambda r: r.helpful_count, reverse=True)

        if limit:
            reviews = reviews[:limit]

        return reviews

    def increment_downloads(self, item_id: str):
        """Increment download count for an item"""
        if item_id in self.items:
            self.items[item_id].downloads += 1

    def get_featured_items(self, limit: int = 10) -> List[MarketplaceItem]:
        """
        Get featured items (highest rated with good download count)

        Args:
            limit: Maximum items to return

        Returns:
            List of featured items
        """
        items = [
            i for i in self.items.values()
            if i.status == ItemStatus.PUBLISHED and
            i.rating >= 4.0 and
            i.downloads >= 10
        ]

        # Sort by rating * log(downloads)
        items.sort(
            key=lambda i: i.rating * (1 + i.downloads / 100),
            reverse=True
        )

        return items[:limit]

    def get_stats(self) -> MarketplaceStats:
        """Get marketplace statistics"""
        published_items = [
            i for i in self.items.values()
            if i.status == ItemStatus.PUBLISHED
        ]

        # Count by type
        items_by_type = {}
        for item_type in ItemType:
            count = len([i for i in published_items if i.item_type == item_type])
            if count > 0:
                items_by_type[item_type.value] = count

        # Count by category
        items_by_category = {}
        for category in ItemCategory:
            count = len([i for i in published_items if i.category == category])
            if count > 0:
                items_by_category[category.value] = count

        # Most downloaded
        most_downloaded = sorted(
            published_items,
            key=lambda i: i.downloads,
            reverse=True
        )[:10]

        # Highest rated
        highest_rated = sorted(
            [i for i in published_items if i.review_count >= 3],
            key=lambda i: i.rating,
            reverse=True
        )[:10]

        # Recently added
        recently_added = sorted(
            published_items,
            key=lambda i: i.published_at or datetime.min,
            reverse=True
        )[:10]

        return MarketplaceStats(
            total_items=len(published_items),
            total_downloads=sum(i.downloads for i in published_items),
            total_reviews=sum(len(r) for r in self.reviews.values()),
            items_by_type=items_by_type,
            items_by_category=items_by_category,
            most_downloaded=[
                {
                    "item_id": i.item_id,
                    "name": i.name,
                    "downloads": i.downloads
                }
                for i in most_downloaded
            ],
            highest_rated=[
                {
                    "item_id": i.item_id,
                    "name": i.name,
                    "rating": i.rating,
                    "review_count": i.review_count
                }
                for i in highest_rated
            ],
            recently_added=[
                {
                    "item_id": i.item_id,
                    "name": i.name,
                    "published_at": i.published_at.isoformat() if i.published_at else None
                }
                for i in recently_added
            ]
        )

    def _update_item_rating(self, item_id: str):
        """Update item rating based on reviews"""
        if item_id not in self.items or item_id not in self.reviews:
            return

        reviews = self.reviews[item_id]

        if not reviews:
            return

        # Calculate average rating
        avg_rating = sum(r.rating for r in reviews) / len(reviews)

        # Update item
        self.items[item_id].rating = round(avg_rating, 1)
        self.items[item_id].review_count = len(reviews)

    def _populate_initial_items(self):
        """Populate with some initial items"""
        # Plugin: Slack Integration
        slack_plugin = Plugin(
            item_id=f"plugin_{uuid.uuid4().hex[:12]}",
            name="Slack Integration",
            description="Send notifications and messages to Slack channels",
            long_description="Complete Slack integration with support for channels, direct messages, file uploads, and interactive components.",
            category=ItemCategory.COMMUNICATION,
            tags=["slack", "notifications", "messaging", "webhooks"],
            version="1.2.0",
            author="YAGO Community",
            status=ItemStatus.PUBLISHED,
            published_at=datetime.utcnow(),
            downloads=1250,
            rating=4.5,
            review_count=45,
            entry_point="slack_plugin:SlackIntegration",
            plugin_type="integration",
            license="MIT",
            keywords=["slack", "chat", "notifications"]
        )
        self.register_item(slack_plugin)

        # Plugin: Custom LLM
        llm_plugin = Plugin(
            item_id=f"plugin_{uuid.uuid4().hex[:12]}",
            name="Custom LLM Provider",
            description="Add your own LLM providers and models",
            category=ItemCategory.AI_ML,
            tags=["llm", "ai", "models", "providers"],
            version="2.0.1",
            author="YAGO Team",
            status=ItemStatus.PUBLISHED,
            published_at=datetime.utcnow(),
            downloads=850,
            rating=4.8,
            review_count=32,
            entry_point="custom_llm:CustomLLMProvider",
            plugin_type="model",
            license="Apache-2.0"
        )
        self.register_item(llm_plugin)

        # Template: Web Scraper
        scraper_template = Template(
            item_id=f"template_{uuid.uuid4().hex[:12]}",
            name="Web Scraper Agent",
            description="Ready-to-use web scraping agent template",
            category=ItemCategory.DATA_PROCESSING,
            tags=["scraping", "web", "data", "automation"],
            version="1.0.0",
            author="Community Contributor",
            status=ItemStatus.PUBLISHED,
            published_at=datetime.utcnow(),
            downloads=620,
            rating=4.3,
            review_count=28,
            template_type="agent",
            variables=["target_url", "selector", "output_format"],
            license="MIT"
        )
        self.register_item(scraper_template)

        # Integration: GitHub
        github_integration = Integration(
            item_id=f"integration_{uuid.uuid4().hex[:12]}",
            name="GitHub Integration",
            description="Integrate with GitHub repositories, issues, and pull requests",
            category=ItemCategory.DEVELOPMENT,
            tags=["github", "git", "repository", "ci/cd"],
            version="1.5.0",
            author="YAGO Team",
            status=ItemStatus.PUBLISHED,
            published_at=datetime.utcnow(),
            downloads=980,
            rating=4.7,
            review_count=52,
            service_name="GitHub",
            api_version="v3",
            authentication_type="oauth",
            webhook_support=True,
            license="MIT"
        )
        self.register_item(github_integration)

        # Template: Data Pipeline
        pipeline_template = Template(
            item_id=f"template_{uuid.uuid4().hex[:12]}",
            name="Data Pipeline Template",
            description="ETL pipeline template for data processing workflows",
            category=ItemCategory.DATA_PROCESSING,
            tags=["etl", "pipeline", "data", "processing"],
            version="1.1.0",
            author="Data Team",
            status=ItemStatus.PUBLISHED,
            published_at=datetime.utcnow(),
            downloads=450,
            rating=4.2,
            review_count=18,
            template_type="workflow",
            variables=["source", "destination", "transformations"],
            license="MIT"
        )
        self.register_item(pipeline_template)


# Singleton instance
_registry = None


def get_registry() -> MarketplaceRegistry:
    """Get the global marketplace registry"""
    global _registry
    if _registry is None:
        _registry = MarketplaceRegistry()
    return _registry
