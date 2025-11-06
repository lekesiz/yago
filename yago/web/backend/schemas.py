"""
YAGO v8.4 - API Schemas
Pydantic models for API request/response validation and OpenAPI documentation
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


# ============================================================================
# Pagination Schemas
# ============================================================================

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    class Config:
        schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "has_next": True,
                "has_prev": False
            }
        }


# ============================================================================
# Project Schemas
# ============================================================================

class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    brief: Dict[str, Any] = Field(..., description="Project brief with requirements")
    config: Dict[str, Any] = Field(default_factory=dict, description="Project configuration")

    class Config:
        schema_extra = {
            "example": {
                "brief": {
                    "project_idea": "Build a task management app",
                    "features": ["User authentication", "Task CRUD", "Notifications"]
                },
                "config": {
                    "primary_model": "gpt-4",
                    "strategy": "balanced",
                    "temperature": 0.7
                }
            }
        }


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: str = Field(..., description="Unique project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: str = Field(..., description="Project status (creating, in_progress, completed, failed, paused)")
    progress: int = Field(..., description="Progress percentage (0-100)")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    files_generated: Optional[int] = Field(0, description="Number of files generated")
    lines_of_code: Optional[int] = Field(0, description="Total lines of code generated")
    actual_cost: Optional[float] = Field(0.0, description="Actual cost in USD")

    class Config:
        schema_extra = {
            "example": {
                "id": "proj_123abc",
                "name": "Task Manager App",
                "description": "A modern task management application",
                "status": "completed",
                "progress": 100,
                "created_at": "2025-11-06T10:30:00Z",
                "updated_at": "2025-11-06T11:45:00Z",
                "files_generated": 42,
                "lines_of_code": 3567,
                "actual_cost": 2.45
            }
        }


class ProjectListResponse(BaseModel):
    """Schema for paginated project list"""
    projects: List[ProjectResponse] = Field(..., description="List of projects")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")


# ============================================================================
# Template Schemas
# ============================================================================

class TemplateSubmit(BaseModel):
    """Schema for submitting a new template"""
    name: str = Field(..., min_length=3, max_length=100, description="Template name")
    description: str = Field(..., min_length=10, max_length=500, description="Template description")
    category: str = Field(..., description="Template category (web, mobile, backend, etc.)")
    difficulty: str = Field(default="intermediate", description="Difficulty level (beginner, intermediate, advanced)")
    icon: str = Field(default="📦", description="Template icon emoji")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    estimated_time: Optional[str] = Field(None, description="Estimated completion time")
    estimated_cost: float = Field(default=0.0, description="Estimated cost in USD")
    template_data: dict = Field(..., description="Template configuration data")

    class Config:
        schema_extra = {
            "example": {
                "name": "REST API Starter",
                "description": "A production-ready REST API with authentication",
                "category": "backend",
                "difficulty": "intermediate",
                "icon": "🔌",
                "tags": ["api", "fastapi", "postgresql"],
                "estimated_time": "1 week",
                "estimated_cost": 8.5,
                "template_data": {
                    "framework": "fastapi",
                    "database": "postgresql",
                    "auth": "jwt"
                }
            }
        }


class TemplateResponse(BaseModel):
    """Schema for template response"""
    id: str
    name: str
    description: str
    category: str
    difficulty: str
    icon: str
    tags: List[str]
    status: str
    is_published: bool
    created_at: str

    class Config:
        schema_extra = {
            "example": {
                "id": "tmpl_456def",
                "name": "REST API Starter",
                "description": "A production-ready REST API",
                "category": "backend",
                "difficulty": "intermediate",
                "icon": "🔌",
                "tags": ["api", "fastapi"],
                "status": "approved",
                "is_published": True,
                "created_at": "2025-11-06T09:00:00Z"
            }
        }


class TemplateListResponse(BaseModel):
    """Schema for paginated template list"""
    templates: List[TemplateResponse] = Field(..., description="List of templates")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")


# ============================================================================
# Error Logging Schemas
# ============================================================================

class ErrorLogCreate(BaseModel):
    """Schema for logging an error"""
    error_type: str = Field(..., description="Type of error (TypeError, ReferenceError, etc.)")
    error_message: str = Field(..., description="Error message")
    source: str = Field(..., description="Error source (frontend, backend)")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    component: Optional[str] = Field(None, description="Component name where error occurred")
    file_path: Optional[str] = Field(None, description="File path where error occurred")
    line_number: Optional[int] = Field(None, description="Line number where error occurred")
    session_id: Optional[str] = Field(None, description="User session ID")
    user_agent: Optional[str] = Field(None, description="Browser user agent")
    url: Optional[str] = Field(None, description="URL where error occurred")
    request_data: Optional[dict] = Field(None, description="Request data when error occurred")
    environment: str = Field(default="development", description="Environment (development, production)")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
    severity: str = Field(default="error", description="Error severity (warning, error, critical)")

    class Config:
        schema_extra = {
            "example": {
                "error_type": "TypeError",
                "error_message": "Cannot read property 'map' of undefined",
                "source": "frontend",
                "component": "ProjectList",
                "file_path": "/src/pages/Projects.tsx",
                "line_number": 42,
                "severity": "error",
                "environment": "production"
            }
        }


class ErrorLogResponse(BaseModel):
    """Schema for error log response"""
    id: str
    error_type: str
    error_message: str
    source: str
    severity: str
    resolved: bool
    created_at: str

    class Config:
        schema_extra = {
            "example": {
                "id": "err_789ghi",
                "error_type": "TypeError",
                "error_message": "Cannot read property 'map' of undefined",
                "source": "frontend",
                "severity": "error",
                "resolved": False,
                "created_at": "2025-11-06T12:15:00Z"
            }
        }


class ErrorListResponse(BaseModel):
    """Schema for paginated error list"""
    errors: List[ErrorLogResponse] = Field(..., description="List of error logs")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="User's full name")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether email is verified")
    created_at: Optional[str] = Field(None, description="Account creation date")
    last_login: Optional[str] = Field(None, description="Last login timestamp")

    class Config:
        schema_extra = {
            "example": {
                "id": "user_123abc",
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_verified": True,
                "created_at": "2025-11-01T10:00:00Z",
                "last_login": "2025-11-06T14:30:00Z"
            }
        }


# ============================================================================
# API Response Schemas
# ============================================================================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": "123", "status": "created"}
            }
        }


class ErrorResponse(BaseModel):
    """Generic error response"""
    detail: str = Field(..., description="Error detail message")

    class Config:
        schema_extra = {
            "example": {
                "detail": "Resource not found"
            }
        }
