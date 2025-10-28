"""
YAGO v8.0 - Enterprise SSO Base
Core authentication abstractions
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr


class AuthProvider(str, Enum):
    """Authentication providers"""
    SAML = "saml"
    OAUTH = "oauth"
    LDAP = "ldap"
    LOCAL = "local"


class AuthMethod(str, Enum):
    """Authentication methods"""
    PASSWORD = "password"
    SSO = "sso"
    API_KEY = "api_key"
    MFA = "mfa"


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    DEVELOPER = "developer"


class MFAMethod(str, Enum):
    """Multi-factor authentication methods"""
    TOTP = "totp"  # Time-based OTP
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"


class User(BaseModel):
    """User model"""
    user_id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    roles: List[UserRole] = Field(default_factory=list)
    provider: AuthProvider = AuthProvider.LOCAL
    mfa_enabled: bool = Field(default=False)
    mfa_methods: List[MFAMethod] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    active: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    """User session"""
    session_id: str
    user_id: str
    provider: AuthProvider
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Token(BaseModel):
    """Authentication token"""
    token_id: str
    token_type: str  # access, refresh, api_key
    user_id: str
    token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    scopes: List[str] = Field(default_factory=list)


class MFAChallenge(BaseModel):
    """MFA challenge"""
    challenge_id: str
    user_id: str
    method: MFAMethod
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    verified: bool = Field(default=False)
