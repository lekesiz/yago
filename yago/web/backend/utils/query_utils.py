"""
YAGO v8.3 - Database Query Utilities
Pagination, filtering, and N+1 query prevention utilities
"""
from typing import List, Optional, Dict, Any, Type, TypeVar
from sqlalchemy.orm import Session, Query, joinedload, selectinload
from sqlalchemy import desc, asc
from pydantic import BaseModel
from math import ceil


# Generic type for SQLAlchemy models
T = TypeVar('T')


class PaginationResult(BaseModel):
    """Pagination result wrapper"""
    items: List[Dict[Any, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

    class Config:
        arbitrary_types_allowed = True


class QueryUtils:
    """Utility functions for database queries"""

    @staticmethod
    def paginate(
        query: Query,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100
    ) -> tuple[Query, Dict[str, Any]]:
        """
        Apply pagination to a SQLAlchemy query

        Args:
            query: SQLAlchemy query object
            page: Page number (1-indexed)
            page_size: Items per page
            max_page_size: Maximum allowed page size

        Returns:
            Tuple of (paginated_query, pagination_meta)
        """
        # Validate and limit page size
        page_size = min(page_size, max_page_size)
        page = max(1, page)  # Ensure page is at least 1

        # Get total count
        total = query.count()

        # Calculate pagination metadata
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1

        # Calculate offset
        offset = (page - 1) * page_size

        # Apply pagination to query
        paginated_query = query.offset(offset).limit(page_size)

        # Metadata
        meta = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }

        return paginated_query, meta

    @staticmethod
    def apply_sorting(
        query: Query,
        model: Type[T],
        sort_by: Optional[str] = None,
        order: str = "desc"
    ) -> Query:
        """
        Apply sorting to a query

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model class
            sort_by: Field name to sort by
            order: "asc" or "desc"

        Returns:
            Query with sorting applied
        """
        if not sort_by:
            return query

        # Check if field exists on model
        if not hasattr(model, sort_by):
            return query

        # Get the field
        field = getattr(model, sort_by)

        # Apply sorting
        if order.lower() == "asc":
            return query.order_by(asc(field))
        else:
            return query.order_by(desc(field))

    @staticmethod
    def apply_filters(
        query: Query,
        model: Type[T],
        filters: Dict[str, Any]
    ) -> Query:
        """
        Apply filters to a query

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model class
            filters: Dictionary of field: value pairs

        Returns:
            Query with filters applied
        """
        for field, value in filters.items():
            if value is None:
                continue

            # Check if field exists
            if not hasattr(model, field):
                continue

            # Apply filter
            query = query.filter(getattr(model, field) == value)

        return query


class EagerLoadingMixin:
    """Mixin for models with N+1 query prevention"""

    @classmethod
    def with_relationships(cls, query: Query, *relationships) -> Query:
        """
        Add eager loading for relationships to prevent N+1 queries

        Usage:
            query = db.query(Project)
            query = Project.with_relationships(query, 'files', 'ai_usage')
            projects = query.all()
        """
        for rel in relationships:
            if hasattr(cls, rel):
                query = query.options(selectinload(getattr(cls, rel)))
        return query

    @classmethod
    def with_joined_relationships(cls, query: Query, *relationships) -> Query:
        """
        Add joined eager loading for relationships (for one-to-one or many-to-one)

        Usage:
            query = db.query(Project)
            query = Project.with_joined_relationships(query, 'clarification_session')
            projects = query.all()
        """
        for rel in relationships:
            if hasattr(cls, rel):
                query = query.options(joinedload(getattr(cls, rel)))
        return query


def paginate_response(
    db: Session,
    query: Query,
    model: Type[T],
    page: int = 1,
    page_size: int = 20,
    sort_by: Optional[str] = None,
    order: str = "desc",
    filters: Optional[Dict[str, Any]] = None,
    eager_load: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Complete pagination helper with filtering, sorting, and eager loading

    Args:
        db: Database session
        query: Initial query
        model: SQLAlchemy model
        page: Page number (1-indexed)
        page_size: Items per page
        sort_by: Field to sort by
        order: Sort order ("asc" or "desc")
        filters: Dictionary of filters
        eager_load: List of relationships to eager load

    Returns:
        Dictionary with items and pagination metadata
    """
    # Apply filters
    if filters:
        query = QueryUtils.apply_filters(query, model, filters)

    # Apply sorting
    if sort_by:
        query = QueryUtils.apply_sorting(query, model, sort_by, order)

    # Apply eager loading
    if eager_load:
        for relationship in eager_load:
            if hasattr(model, relationship):
                query = query.options(selectinload(getattr(model, relationship)))

    # Apply pagination
    paginated_query, meta = QueryUtils.paginate(query, page, page_size)

    # Execute query
    items = paginated_query.all()

    # Convert to dict if model has to_dict method
    if hasattr(model, 'to_dict'):
        items_dict = [item.to_dict() for item in items]
    else:
        items_dict = items

    return {
        "items": items_dict,
        "pagination": meta
    }


# Convenience functions for common patterns

def get_projects_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc"
):
    """Get projects with pagination and eager loading"""
    from ..models import Project

    query = db.query(Project)

    filters = {}
    if user_id:
        filters['user_id'] = user_id
    if status:
        filters['status'] = status

    return paginate_response(
        db=db,
        query=query,
        model=Project,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        filters=filters,
        eager_load=['generated_files', 'ai_usage', 'clarification_session']
    )


def get_templates_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    status: Optional[str] = None,
    published_only: bool = True,
    sort_by: str = "created_at",
    order: str = "desc"
):
    """Get templates with pagination"""
    from ..models import Template

    query = db.query(Template)

    filters = {}
    if category:
        filters['category'] = category
    if status:
        filters['status'] = status
    if published_only:
        filters['is_published'] = True

    return paginate_response(
        db=db,
        query=query,
        model=Template,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        filters=filters
    )


def get_errors_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    sort_by: str = "created_at",
    order: str = "desc"
):
    """Get error logs with pagination"""
    from ..models import ErrorLog

    query = db.query(ErrorLog)

    filters = {}
    if source:
        filters['source'] = source
    if severity:
        filters['severity'] = severity
    if resolved is not None:
        filters['resolved'] = resolved

    return paginate_response(
        db=db,
        query=query,
        model=ErrorLog,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        filters=filters
    )
