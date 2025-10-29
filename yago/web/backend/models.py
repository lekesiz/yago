"""
YAGO v8.0 - Database Models
SQLAlchemy ORM models for PostgreSQL
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, CheckConstraint, Index, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import text

try:
    from .database import Base
except ImportError:
    from database import Base


# Helper function for UUID
def generate_uuid():
    return str(uuid.uuid4())


class Project(Base):
    """Main project table"""
    __tablename__ = "projects"

    # Primary key
    id = Column(String, primary_key=True, default=generate_uuid)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="creating")
    progress = Column(Integer, default=0)

    # Configuration (stored as JSON)
    brief = Column(JSONB) if 'postgresql' in str(Base.metadata.bind) else Column(Text)  # Fallback for SQLite
    config = Column(JSONB) if 'postgresql' in str(Base.metadata.bind) else Column(Text)

    # Model selection
    primary_model = Column(String(100))
    agent_role = Column(String(100))
    strategy = Column(String(50), default="balanced")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4000)

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)

    # Results
    project_path = Column(String(500))
    cost_estimate = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    files_generated = Column(Integer, default=0)
    lines_of_code = Column(Integer, default=0)

    # Errors and logs (stored as JSON)
    errors = Column(JSONB, default=list) if 'postgresql' in str(Base.metadata.bind) else Column(Text, default="[]")
    logs = Column(JSONB, default=list) if 'postgresql' in str(Base.metadata.bind) else Column(Text, default="[]")

    # User reference (for future auth)
    user_id = Column(String)

    # Relationships
    clarification_session = relationship("ClarificationSession", back_populates="project", uselist=False)
    generated_files = relationship("GeneratedFile", back_populates="project")
    ai_usage = relationship("AIProviderUsage", back_populates="project")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            status.in_(['creating', 'in_progress', 'executing', 'completed', 'failed', 'paused']),
            name='status_check'
        ),
        Index('idx_projects_status', 'status'),
        Index('idx_projects_created_at', 'created_at'),
        Index('idx_projects_user_id', 'user_id'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "progress": self.progress,
            "brief": self.brief,
            "config": self.config,
            "primary_model": self.primary_model,
            "agent_role": self.agent_role,
            "strategy": self.strategy,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "project_path": self.project_path,
            "cost_estimate": self.cost_estimate,
            "actual_cost": self.actual_cost,
            "files_generated": self.files_generated,
            "lines_of_code": self.lines_of_code,
            "errors": self.errors or [],
            "logs": self.logs or [],
        }


class ClarificationSession(Base):
    """Clarification Q&A sessions"""
    __tablename__ = "clarification_sessions"

    # Primary key
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"))

    # Session data
    project_idea = Column(Text, nullable=False)
    depth = Column(String(20), nullable=False)
    questions = Column(JSONB, nullable=False) if 'postgresql' in str(Base.metadata.bind) else Column(Text, nullable=False)
    answers = Column(JSONB, default=dict) if 'postgresql' in str(Base.metadata.bind) else Column(Text, default="{}")

    # State
    current_question = Column(Integer, default=0)
    total_questions = Column(Integer, nullable=False)
    is_completed = Column(Boolean, default=False)

    # AI provider used
    ai_provider = Column(String(50))

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(TIMESTAMP)

    # Relationships
    project = relationship("Project", back_populates="clarification_session")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            depth.in_(['minimal', 'standard', 'full']),
            name='depth_check'
        ),
        Index('idx_sessions_project_id', 'project_id'),
        Index('idx_sessions_created_at', 'created_at'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_idea": self.project_idea,
            "depth": self.depth,
            "questions": self.questions,
            "answers": self.answers or {},
            "current_question": self.current_question,
            "total_questions": self.total_questions,
            "is_completed": self.is_completed,
            "ai_provider": self.ai_provider,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class GeneratedFile(Base):
    """Generated code files"""
    __tablename__ = "generated_files"

    # Primary key
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"))

    # File info
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    content = Column(Text)
    size = Column(Integer)
    lines = Column(Integer)

    # Metadata
    ai_provider = Column(String(50))
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="generated_files")

    # Constraints
    __table_args__ = (
        Index('idx_files_project_id', 'project_id'),
        Index('idx_files_type', 'file_type'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "size": self.size,
            "lines": self.lines,
            "ai_provider": self.ai_provider,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }


class AIProviderUsage(Base):
    """AI provider usage tracking"""
    __tablename__ = "ai_provider_usage"

    # Primary key
    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    # Provider details
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)

    # Usage metrics
    request_type = Column(String(50))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    cost = Column(Float)

    # Performance
    latency_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)

    # Timestamp
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="ai_usage")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            provider.in_(['openai', 'anthropic', 'gemini', 'cursor']),
            name='provider_check'
        ),
        Index('idx_usage_provider', 'provider'),
        Index('idx_usage_project_id', 'project_id'),
        Index('idx_usage_created_at', 'created_at'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "provider": self.provider,
            "model": self.model,
            "request_type": self.request_type,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost": self.cost,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class User(Base):
    """User accounts (for future auth)"""
    __tablename__ = "users"

    # Primary key
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(TIMESTAMP)

    # Constraints
    __table_args__ = (
        Index('idx_users_email', 'email'),
    )

    def to_dict(self):
        """Convert to dictionary (excluding password)"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
