"""
YAGO v8.3 - Error Logging Service
Centralized error tracking and logging
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

try:
    from . import models
except ImportError:
    import models


class ErrorLoggingService:
    """Service for error logging and retrieval"""

    @staticmethod
    def log_error(
        db: Session,
        error_type: str,
        error_message: str,
        source: str,
        stack_trace: Optional[str] = None,
        component: Optional[str] = None,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        url: Optional[str] = None,
        request_data: Optional[Dict] = None,
        environment: str = "development",
        error_metadata: Optional[Dict] = None,
        severity: str = "error"
    ) -> models.ErrorLog:
        """
        Log an error to the database

        Args:
            db: Database session
            error_type: Type of error (TypeError, ReferenceError, etc.)
            error_message: Error message
            source: Source of error (frontend, backend)
            stack_trace: Full stack trace
            component: Component/module name
            file_path: File where error occurred
            line_number: Line number
            user_id: User ID if authenticated
            session_id: Browser session ID
            user_agent: User agent string
            url: URL where error occurred
            request_data: Request payload/data
            environment: Environment (development, production)
            error_metadata: Additional metadata
            severity: debug, info, warning, error, critical

        Returns:
            Created ErrorLog instance
        """
        # Convert dicts to JSON strings for SQLite compatibility
        request_data_str = json.dumps(request_data) if request_data else None
        error_metadata_str = json.dumps(error_metadata) if metadata else None

        error_log = models.ErrorLog(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            source=source,
            component=component,
            file_path=file_path,
            line_number=line_number,
            user_id=user_id,
            session_id=session_id,
            user_agent=user_agent,
            url=url,
            request_data=request_data_str,
            environment=environment,
            error_metadata=error_metadata_str,
            severity=severity,
            resolved=False
        )

        db.add(error_log)
        db.commit()
        db.refresh(error_log)

        return error_log

    @staticmethod
    def get_errors(
        db: Session,
        limit: int = 100,
        offset: int = 0,
        source: Optional[str] = None,
        severity: Optional[str] = None,
        resolved: Optional[bool] = None,
        error_type: Optional[str] = None,
        component: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[models.ErrorLog]:
        """
        Retrieve error logs with filters

        Args:
            db: Database session
            limit: Maximum number of results
            offset: Offset for pagination
            source: Filter by source (frontend/backend)
            severity: Filter by severity level
            resolved: Filter by resolved status
            error_type: Filter by error type
            component: Filter by component
            user_id: Filter by user ID
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            List of ErrorLog instances
        """
        query = db.query(models.ErrorLog)

        # Apply filters
        if source:
            query = query.filter(models.ErrorLog.source == source)
        if severity:
            query = query.filter(models.ErrorLog.severity == severity)
        if resolved is not None:
            query = query.filter(models.ErrorLog.resolved == resolved)
        if error_type:
            query = query.filter(models.ErrorLog.error_type == error_type)
        if component:
            query = query.filter(models.ErrorLog.component.ilike(f"%{component}%"))
        if user_id:
            query = query.filter(models.ErrorLog.user_id == user_id)
        if start_date:
            query = query.filter(models.ErrorLog.created_at >= start_date)
        if end_date:
            query = query.filter(models.ErrorLog.created_at <= end_date)

        # Order by most recent first
        query = query.order_by(models.ErrorLog.created_at.desc())

        # Apply pagination
        return query.limit(limit).offset(offset).all()

    @staticmethod
    def get_error_stats(
        db: Session,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get error statistics for the specified time period

        Args:
            db: Database session
            hours: Number of hours to look back

        Returns:
            Dictionary with error statistics
        """
        since = datetime.utcnow() - timedelta(hours=hours)

        # Total errors
        total_errors = db.query(models.ErrorLog).filter(
            models.ErrorLog.created_at >= since
        ).count()

        # Errors by source
        frontend_errors = db.query(models.ErrorLog).filter(
            models.ErrorLog.created_at >= since,
            models.ErrorLog.source == "frontend"
        ).count()

        backend_errors = db.query(models.ErrorLog).filter(
            models.ErrorLog.created_at >= since,
            models.ErrorLog.source == "backend"
        ).count()

        # Errors by severity
        critical_errors = db.query(models.ErrorLog).filter(
            models.ErrorLog.created_at >= since,
            models.ErrorLog.severity == "critical"
        ).count()

        error_level_errors = db.query(models.ErrorLog).filter(
            models.ErrorLog.created_at >= since,
            models.ErrorLog.severity == "error"
        ).count()

        # Resolved vs unresolved
        resolved_errors = db.query(models.ErrorLog).filter(
            models.ErrorLog.created_at >= since,
            models.ErrorLog.resolved == True
        ).count()

        unresolved_errors = db.query(models.ErrorLog).filter(
            models.ErrorLog.created_at >= since,
            models.ErrorLog.resolved == False
        ).count()

        # Most common error types
        from sqlalchemy import func
        common_errors = db.query(
            models.ErrorLog.error_type,
            func.count(models.ErrorLog.id).label('count')
        ).filter(
            models.ErrorLog.created_at >= since
        ).group_by(
            models.ErrorLog.error_type
        ).order_by(
            func.count(models.ErrorLog.id).desc()
        ).limit(10).all()

        return {
            "total_errors": total_errors,
            "frontend_errors": frontend_errors,
            "backend_errors": backend_errors,
            "critical_errors": critical_errors,
            "error_level_errors": error_level_errors,
            "resolved_errors": resolved_errors,
            "unresolved_errors": unresolved_errors,
            "common_error_types": [
                {"error_type": err[0], "count": err[1]}
                for err in common_errors
            ],
            "period_hours": hours
        }

    @staticmethod
    def resolve_error(
        db: Session,
        error_id: str,
        resolved_by: Optional[str] = None
    ) -> Optional[models.ErrorLog]:
        """
        Mark an error as resolved

        Args:
            db: Database session
            error_id: Error log ID
            resolved_by: User ID who resolved the error

        Returns:
            Updated ErrorLog instance or None
        """
        error_log = db.query(models.ErrorLog).filter(
            models.ErrorLog.id == error_id
        ).first()

        if error_log:
            error_log.resolved = True
            error_log.resolved_at = datetime.utcnow()
            error_log.resolved_by = resolved_by
            db.commit()
            db.refresh(error_log)

        return error_log

    @staticmethod
    def delete_old_errors(
        db: Session,
        days: int = 30
    ) -> int:
        """
        Delete error logs older than specified days

        Args:
            db: Database session
            days: Number of days to keep logs

        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted_count = db.query(models.ErrorLog).filter(
            models.ErrorLog.created_at < cutoff_date,
            models.ErrorLog.resolved == True
        ).delete()

        db.commit()

        return deleted_count
