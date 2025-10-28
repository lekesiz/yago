"""
YAGO v7.2 - Team Collaboration Module
Multi-user collaboration features for YAGO
"""

from .models import (
    User,
    Team,
    Role,
    Permission,
    TeamMember,
    Invitation,
)

from .user_manager import UserManager
from .team_manager import TeamManager
from .permissions import PermissionManager

__all__ = [
    # Models
    'User',
    'Team',
    'Role',
    'Permission',
    'TeamMember',
    'Invitation',

    # Managers
    'UserManager',
    'TeamManager',
    'PermissionManager',
]
