"""
YAGO v7.2 - Collaboration Models
Data models for team collaboration
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User role in a team"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
    GUEST = "guest"


class Permission(str, Enum):
    """System permissions"""
    # User permissions
    USER_CREATE = "user.create"
    USER_READ = "user.read"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"

    # Team permissions
    TEAM_CREATE = "team.create"
    TEAM_READ = "team.read"
    TEAM_UPDATE = "team.update"
    TEAM_DELETE = "team.delete"
    TEAM_INVITE = "team.invite"

    # Agent permissions
    AGENT_CREATE = "agent.create"
    AGENT_READ = "agent.read"
    AGENT_UPDATE = "agent.update"
    AGENT_DELETE = "agent.delete"
    AGENT_EXECUTE = "agent.execute"

    # Session permissions
    SESSION_CREATE = "session.create"
    SESSION_READ = "session.read"
    SESSION_UPDATE = "session.update"
    SESSION_DELETE = "session.delete"
    SESSION_SHARE = "session.share"

    # Dashboard permissions
    DASHBOARD_CREATE = "dashboard.create"
    DASHBOARD_READ = "dashboard.read"
    DASHBOARD_UPDATE = "dashboard.update"
    DASHBOARD_DELETE = "dashboard.delete"

    # Plugin permissions
    PLUGIN_INSTALL = "plugin.install"
    PLUGIN_MANAGE = "plugin.manage"
    PLUGIN_EXECUTE = "plugin.execute"

    # Settings permissions
    SETTINGS_READ = "settings.read"
    SETTINGS_UPDATE = "settings.update"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class InvitationStatus(str, Enum):
    """Invitation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    status: UserStatus = UserStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Settings
    preferences: Dict[str, Any] = Field(default_factory=dict)
    notification_settings: Dict[str, bool] = Field(default_factory=dict)

    # Security
    two_factor_enabled: bool = False
    password_hash: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "status": "active"
            }
        }


class Role(BaseModel):
    """Role with permissions"""
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[Permission] = Field(default_factory=list)
    is_system_role: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "role_admin",
                "name": "Administrator",
                "permissions": ["user.read", "user.update"]
            }
        }


class Team(BaseModel):
    """Team/Organization model"""
    id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    owner_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict)
    max_members: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "team_123",
                "name": "Engineering Team",
                "owner_id": "user_123"
            }
        }


class TeamMember(BaseModel):
    """Team membership"""
    id: str
    team_id: str
    user_id: str
    role: UserRole = UserRole.MEMBER
    permissions: List[Permission] = Field(default_factory=list)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "member_123",
                "team_id": "team_123",
                "user_id": "user_456",
                "role": "member"
            }
        }


class Invitation(BaseModel):
    """Team invitation"""
    id: str
    team_id: str
    email: EmailStr
    role: UserRole = UserRole.MEMBER
    invited_by: str
    status: InvitationStatus = InvitationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    token: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "invite_123",
                "team_id": "team_123",
                "email": "newuser@example.com",
                "role": "member",
                "invited_by": "user_123"
            }
        }


class Session(BaseModel):
    """Collaboration session"""
    id: str
    team_id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    # Participants
    participants: List[str] = Field(default_factory=list)  # user_ids

    # Session data
    data: Dict[str, Any] = Field(default_factory=dict)
    shared_context: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "session_123",
                "team_id": "team_123",
                "name": "Project Planning",
                "owner_id": "user_123"
            }
        }


class ActivityLog(BaseModel):
    """Activity log entry"""
    id: str
    user_id: str
    team_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "log_123",
                "user_id": "user_123",
                "action": "session.create",
                "resource_type": "session",
                "resource_id": "session_123"
            }
        }


class Comment(BaseModel):
    """Comment on a resource"""
    id: str
    user_id: str
    resource_type: str
    resource_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    edited: bool = False
    parent_id: Optional[str] = None  # For threaded comments
    reactions: Dict[str, List[str]] = Field(default_factory=dict)  # emoji -> user_ids

    class Config:
        json_schema_extra = {
            "example": {
                "id": "comment_123",
                "user_id": "user_123",
                "resource_type": "session",
                "resource_id": "session_123",
                "content": "Great work on this!"
            }
        }


# Role permission mappings
ROLE_PERMISSIONS = {
    UserRole.OWNER: [
        # Full access to everything
        Permission.USER_CREATE,
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.TEAM_CREATE,
        Permission.TEAM_READ,
        Permission.TEAM_UPDATE,
        Permission.TEAM_DELETE,
        Permission.TEAM_INVITE,
        Permission.AGENT_CREATE,
        Permission.AGENT_READ,
        Permission.AGENT_UPDATE,
        Permission.AGENT_DELETE,
        Permission.AGENT_EXECUTE,
        Permission.SESSION_CREATE,
        Permission.SESSION_READ,
        Permission.SESSION_UPDATE,
        Permission.SESSION_DELETE,
        Permission.SESSION_SHARE,
        Permission.DASHBOARD_CREATE,
        Permission.DASHBOARD_READ,
        Permission.DASHBOARD_UPDATE,
        Permission.DASHBOARD_DELETE,
        Permission.PLUGIN_INSTALL,
        Permission.PLUGIN_MANAGE,
        Permission.PLUGIN_EXECUTE,
        Permission.SETTINGS_READ,
        Permission.SETTINGS_UPDATE,
    ],
    UserRole.ADMIN: [
        # Admin access (no user delete, team delete)
        Permission.USER_READ,
        Permission.USER_UPDATE,
        Permission.TEAM_READ,
        Permission.TEAM_UPDATE,
        Permission.TEAM_INVITE,
        Permission.AGENT_CREATE,
        Permission.AGENT_READ,
        Permission.AGENT_UPDATE,
        Permission.AGENT_DELETE,
        Permission.AGENT_EXECUTE,
        Permission.SESSION_CREATE,
        Permission.SESSION_READ,
        Permission.SESSION_UPDATE,
        Permission.SESSION_DELETE,
        Permission.SESSION_SHARE,
        Permission.DASHBOARD_CREATE,
        Permission.DASHBOARD_READ,
        Permission.DASHBOARD_UPDATE,
        Permission.DASHBOARD_DELETE,
        Permission.PLUGIN_INSTALL,
        Permission.PLUGIN_MANAGE,
        Permission.PLUGIN_EXECUTE,
        Permission.SETTINGS_READ,
    ],
    UserRole.MEMBER: [
        # Regular member access
        Permission.USER_READ,
        Permission.TEAM_READ,
        Permission.AGENT_CREATE,
        Permission.AGENT_READ,
        Permission.AGENT_UPDATE,
        Permission.AGENT_EXECUTE,
        Permission.SESSION_CREATE,
        Permission.SESSION_READ,
        Permission.SESSION_UPDATE,
        Permission.SESSION_SHARE,
        Permission.DASHBOARD_CREATE,
        Permission.DASHBOARD_READ,
        Permission.DASHBOARD_UPDATE,
        Permission.PLUGIN_EXECUTE,
        Permission.SETTINGS_READ,
    ],
    UserRole.VIEWER: [
        # Read-only access
        Permission.USER_READ,
        Permission.TEAM_READ,
        Permission.AGENT_READ,
        Permission.SESSION_READ,
        Permission.DASHBOARD_READ,
        Permission.SETTINGS_READ,
    ],
    UserRole.GUEST: [
        # Limited read access
        Permission.TEAM_READ,
        Permission.SESSION_READ,
        Permission.DASHBOARD_READ,
    ],
}
