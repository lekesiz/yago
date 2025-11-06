"""
YAGO v8.3 - Input Validation Utilities
Secure input validation to prevent SQL injection and XSS attacks
"""
import re
from typing import Optional, List
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum


# Enums for constrained values
class ProjectStatus(str, Enum):
    CREATING = "creating"
    IN_PROGRESS = "in_progress"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ClarificationDepth(str, Enum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    FULL = "full"


class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    CURSOR = "cursor"


class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TemplateStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# Validation utilities
class ValidationUtils:
    """Utility functions for input validation"""

    # Dangerous patterns for SQL injection
    SQL_INJECTION_PATTERNS = [
        r"(\bDROP\b|\bDELETE\b|\bUPDATE\b|\bINSERT\b|\bEXEC\b|\bSELECT\b).*\b(FROM|INTO|TABLE|DATABASE)\b",
        r"--",
        r";.*\b(DROP|DELETE|UPDATE|INSERT|EXEC)\b",
        r"\bOR\b.*=.*",
        r"\bAND\b.*=.*",
        r"[\'\";].*(\bOR\b|\bAND\b).*[\'\";]",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe[^>]*>",
    ]

    @classmethod
    def contains_sql_injection(cls, text: str) -> bool:
        """Check if text contains SQL injection patterns"""
        if not text:
            return False

        text_upper = text.upper()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        return False

    @classmethod
    def contains_xss(cls, text: str) -> bool:
        """Check if text contains XSS patterns"""
        if not text:
            return False

        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @classmethod
    def sanitize_string(cls, text: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input"""
        if not text:
            return ""

        # Strip whitespace
        text = text.strip()

        # Truncate if needed
        if max_length and len(text) > max_length:
            text = text[:max_length]

        return text

    @classmethod
    def validate_safe_string(cls, text: str, field_name: str = "field") -> str:
        """Validate that string is safe (no SQL injection or XSS)"""
        if not text:
            return text

        if cls.contains_sql_injection(text):
            raise ValueError(f"{field_name} contains potentially dangerous SQL patterns")

        if cls.contains_xss(text):
            raise ValueError(f"{field_name} contains potentially dangerous script patterns")

        return text


# Pydantic models for API requests
class ProjectCreateRequest(BaseModel):
    """Validated project creation request"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    primary_model: Optional[str] = Field(None, max_length=100)
    agent_role: Optional[str] = Field(None, max_length=100)
    strategy: Optional[str] = Field("balanced", max_length=50)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(4000, ge=100, le=32000)

    @validator('name')
    def validate_name(cls, v):
        """Validate project name is safe"""
        v = ValidationUtils.sanitize_string(v, max_length=200)
        if not v:
            raise ValueError('Name cannot be empty or whitespace')
        return ValidationUtils.validate_safe_string(v, 'Project name')

    @validator('description')
    def validate_description(cls, v):
        """Validate description is safe"""
        if v:
            v = ValidationUtils.sanitize_string(v, max_length=2000)
            return ValidationUtils.validate_safe_string(v, 'Description')
        return v

    @validator('strategy')
    def validate_strategy(cls, v):
        """Validate strategy value"""
        allowed = ['balanced', 'creative', 'precise', 'fast']
        if v not in allowed:
            raise ValueError(f'Strategy must be one of: {", ".join(allowed)}')
        return v


class ProjectUpdateRequest(BaseModel):
    """Validated project update request"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[ProjectStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)

    @validator('name')
    def validate_name(cls, v):
        if v:
            v = ValidationUtils.sanitize_string(v, max_length=200)
            return ValidationUtils.validate_safe_string(v, 'Project name')
        return v

    @validator('description')
    def validate_description(cls, v):
        if v:
            v = ValidationUtils.sanitize_string(v, max_length=2000)
            return ValidationUtils.validate_safe_string(v, 'Description')
        return v


class ClarificationStartRequest(BaseModel):
    """Validated clarification session start request"""
    project_idea: str = Field(..., min_length=10, max_length=5000)
    depth: ClarificationDepth = Field(ClarificationDepth.STANDARD)
    ai_provider: Optional[AIProvider] = None

    @validator('project_idea')
    def validate_project_idea(cls, v):
        """Validate project idea is safe"""
        v = ValidationUtils.sanitize_string(v, max_length=5000)
        if len(v) < 10:
            raise ValueError('Project idea must be at least 10 characters')
        return ValidationUtils.validate_safe_string(v, 'Project idea')


class ClarificationAnswerRequest(BaseModel):
    """Validated clarification answer request"""
    question_id: str = Field(..., min_length=1, max_length=50)
    answer: str = Field(..., min_length=1, max_length=5000)

    @validator('question_id')
    def validate_question_id(cls, v):
        """Validate question ID format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Question ID contains invalid characters')
        return v

    @validator('answer')
    def validate_answer(cls, v):
        """Validate answer is safe"""
        v = ValidationUtils.sanitize_string(v, max_length=5000)
        if not v:
            raise ValueError('Answer cannot be empty')
        return ValidationUtils.validate_safe_string(v, 'Answer')


class UserRegisterRequest(BaseModel):
    """Validated user registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=200)

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')

        # Check for complexity
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')

        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name is safe"""
        if v:
            v = ValidationUtils.sanitize_string(v, max_length=200)
            return ValidationUtils.validate_safe_string(v, 'Full name')
        return v


class TemplateSubmitRequest(BaseModel):
    """Validated template submission request"""
    name: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: str = Field(..., min_length=3, max_length=50)
    difficulty: str = Field(..., pattern=r'^(beginner|intermediate|advanced)$')
    tags: Optional[List[str]] = Field(None, max_items=10)
    template_data: dict = Field(...)

    @validator('name')
    def validate_name(cls, v):
        v = ValidationUtils.sanitize_string(v, max_length=200)
        return ValidationUtils.validate_safe_string(v, 'Template name')

    @validator('description')
    def validate_description(cls, v):
        v = ValidationUtils.sanitize_string(v, max_length=2000)
        return ValidationUtils.validate_safe_string(v, 'Description')

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags are safe"""
        if v:
            validated_tags = []
            for tag in v:
                tag = ValidationUtils.sanitize_string(tag, max_length=50)
                if tag:
                    validated_tags.append(ValidationUtils.validate_safe_string(tag, 'Tag'))
            return validated_tags[:10]  # Max 10 tags
        return v


class ErrorLogRequest(BaseModel):
    """Validated error log request"""
    error_type: str = Field(..., max_length=100)
    message: str = Field(..., max_length=1000)
    stack_trace: Optional[str] = Field(None, max_length=5000)
    source: str = Field(..., pattern=r'^(frontend|backend)$')
    severity: ErrorSeverity = Field(ErrorSeverity.MEDIUM)
    context: Optional[dict] = None

    @validator('error_type', 'message')
    def validate_strings(cls, v, field):
        """Validate error strings are safe"""
        v = ValidationUtils.sanitize_string(v)
        return ValidationUtils.validate_safe_string(v, field.name)


# Pagination helpers
class PaginationParams(BaseModel):
    """Validated pagination parameters"""
    skip: int = Field(0, ge=0, le=10000)
    limit: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = Field(None, max_length=50)
    order: Optional[str] = Field("desc", pattern=r'^(asc|desc)$')

    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Validate sort field"""
        if v:
            # Only allow alphanumeric and underscore
            if not re.match(r'^[a-zA-Z0-9_]+$', v):
                raise ValueError('Sort field contains invalid characters')
        return v
