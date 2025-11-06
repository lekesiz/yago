"""Add performance indexes

Revision ID: 2025_11_06_perf_idx
Revises: 237c4addff1c
Create Date: 2025-11-06 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025_11_06_perf_idx'
down_revision = '237c4addff1c'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance-critical indexes"""

    # Composite indexes for common query patterns
    # Projects table - Filter by user and status
    op.create_index(
        'idx_projects_user_status',
        'projects',
        ['user_id', 'status'],
        unique=False
    )

    # Projects table - Filter by status and created_at for sorting
    op.create_index(
        'idx_projects_status_created',
        'projects',
        ['status', 'created_at'],
        unique=False
    )

    # Error logs - Unresolved critical errors (most common query)
    op.create_index(
        'idx_errors_resolved_severity',
        'error_logs',
        ['resolved', 'severity'],
        unique=False
    )

    # Error logs - Recent errors by source
    op.create_index(
        'idx_errors_source_created',
        'error_logs',
        ['source', 'created_at'],
        unique=False
    )

    # AI Provider Usage - Provider analytics
    op.create_index(
        'idx_usage_provider_created',
        'ai_provider_usage',
        ['provider', 'created_at'],
        unique=False
    )

    # AI Provider Usage - Project cost tracking
    op.create_index(
        'idx_usage_project_created',
        'ai_provider_usage',
        ['project_id', 'created_at'],
        unique=False
    )

    # Foreign key indexes (if not already created)
    # Generated files - Project lookup
    try:
        op.create_index(
            'idx_files_project_id',
            'generated_files',
            ['project_id'],
            unique=False
        )
    except:
        # Index might already exist
        pass

    # Templates - User submissions
    try:
        op.create_index(
            'idx_templates_user_status',
            'templates',
            ['user_id', 'status'],
            unique=False
        )
    except:
        pass

    # Templates - Popular templates (approved and high rating)
    try:
        op.create_index(
            'idx_templates_status_rating',
            'templates',
            ['status', 'rating'],
            unique=False
        )
    except:
        pass

    # Clarification sessions - Project lookup
    try:
        op.create_index(
            'idx_sessions_completed',
            'clarification_sessions',
            ['is_completed', 'created_at'],
            unique=False
        )
    except:
        pass

    print("✅ Performance indexes created successfully")


def downgrade():
    """Remove performance indexes"""

    # Drop all indexes in reverse order
    op.drop_index('idx_sessions_completed', table_name='clarification_sessions')
    op.drop_index('idx_templates_status_rating', table_name='templates')
    op.drop_index('idx_templates_user_status', table_name='templates')
    op.drop_index('idx_files_project_id', table_name='generated_files')
    op.drop_index('idx_usage_project_created', table_name='ai_provider_usage')
    op.drop_index('idx_usage_provider_created', table_name='ai_provider_usage')
    op.drop_index('idx_errors_source_created', table_name='error_logs')
    op.drop_index('idx_errors_resolved_severity', table_name='error_logs')
    op.drop_index('idx_projects_status_created', table_name='projects')
    op.drop_index('idx_projects_user_status', table_name='projects')

    print("⚠️  Performance indexes removed")
