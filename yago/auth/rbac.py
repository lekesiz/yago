"""YAGO v8.0 - Role-Based Access Control Manager"""
import logging
from typing import List, Set, Dict
from .base import User, UserRole

logger = logging.getLogger(__name__)

class RBACManager:
    """Role-Based Access Control manager"""
    
    def __init__(self):
        self.role_permissions: Dict[UserRole, Set[str]] = {
            UserRole.ADMIN: {"*"},  # All permissions
            UserRole.DEVELOPER: {"read", "write", "execute", "deploy"},
            UserRole.USER: {"read", "write"},
            UserRole.VIEWER: {"read"}
        }
    
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has permission"""
        for role in user.roles:
            role_perms = self.role_permissions.get(role, set())
            if "*" in role_perms or permission in role_perms:
                return True
        return False
    
    def get_user_permissions(self, user: User) -> Set[str]:
        """Get all permissions for user"""
        perms = set()
        for role in user.roles:
            perms.update(self.role_permissions.get(role, set()))
        return perms
    
    def assign_role(self, user: User, role: UserRole) -> bool:
        """Assign role to user"""
        if role not in user.roles:
            user.roles.append(role)
            logger.info(f"Assigned role {role.value} to user {user.user_id}")
            return True
        return False
    
    def revoke_role(self, user: User, role: UserRole) -> bool:
        """Revoke role from user"""
        if role in user.roles:
            user.roles.remove(role)
            logger.info(f"Revoked role {role.value} from user {user.user_id}")
            return True
        return False
