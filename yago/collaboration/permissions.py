"""
YAGO v7.2 - Permission Management
Role-based access control (RBAC)
"""

from typing import List, Optional
import logging

from .models import (
    User,
    Team,
    TeamMember,
    Permission,
    UserRole,
    ROLE_PERMISSIONS
)
from .user_manager import UserManager
from .team_manager import TeamManager

logger = logging.getLogger(__name__)


class PermissionManager:
    """
    Manages permissions and access control

    Responsibilities:
    - Check user permissions
    - Validate access to resources
    - Role-based access control
    """

    def __init__(self,
                 user_manager: Optional[UserManager] = None,
                 team_manager: Optional[TeamManager] = None):
        """Initialize permission manager"""
        self.user_manager = user_manager or UserManager()
        self.team_manager = team_manager or TeamManager()

    async def has_permission(self,
                            user_id: str,
                            permission: Permission,
                            team_id: Optional[str] = None) -> bool:
        """
        Check if user has a specific permission

        Args:
            user_id: User ID
            permission: Permission to check
            team_id: Optional team context

        Returns:
            True if user has permission
        """
        try:
            # Get user
            user = await self.user_manager.get_user(user_id)
            if not user:
                return False

            # If team context provided, check team role
            if team_id:
                member = await self.team_manager.get_member(team_id, user_id)
                if not member:
                    return False

                # Check role permissions
                role_perms = ROLE_PERMISSIONS.get(member.role, [])
                if permission in role_perms:
                    return True

                # Check member-specific permissions
                if permission in member.permissions:
                    return True

                return False

            # Global permission check (no team context)
            # For now, allow if user is active
            # TODO: Implement global roles/permissions
            return True

        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False

    async def has_any_permission(self,
                                 user_id: str,
                                 permissions: List[Permission],
                                 team_id: Optional[str] = None) -> bool:
        """Check if user has any of the specified permissions"""
        for permission in permissions:
            if await self.has_permission(user_id, permission, team_id):
                return True
        return False

    async def has_all_permissions(self,
                                  user_id: str,
                                  permissions: List[Permission],
                                  team_id: Optional[str] = None) -> bool:
        """Check if user has all of the specified permissions"""
        for permission in permissions:
            if not await self.has_permission(user_id, permission, team_id):
                return False
        return True

    async def can_access_resource(self,
                                 user_id: str,
                                 resource_type: str,
                                 resource_id: str,
                                 action: str,
                                 team_id: Optional[str] = None) -> bool:
        """
        Check if user can perform action on resource

        Args:
            user_id: User ID
            resource_type: Type of resource (user, team, agent, etc.)
            resource_id: Resource ID
            action: Action to perform (read, update, delete, etc.)
            team_id: Optional team context

        Returns:
            True if user can access resource
        """
        try:
            # Build permission from resource type and action
            permission_str = f"{resource_type}.{action}"

            try:
                permission = Permission(permission_str)
            except ValueError:
                logger.warning(f"Invalid permission: {permission_str}")
                return False

            # Check permission
            return await self.has_permission(user_id, permission, team_id)

        except Exception as e:
            logger.error(f"Error checking resource access: {e}")
            return False

    async def is_team_owner(self, user_id: str, team_id: str) -> bool:
        """Check if user is team owner"""
        try:
            member = await self.team_manager.get_member(team_id, user_id)
            return member and member.role == UserRole.OWNER

        except Exception as e:
            logger.error(f"Error checking team owner: {e}")
            return False

    async def is_team_admin(self, user_id: str, team_id: str) -> bool:
        """Check if user is team admin or owner"""
        try:
            member = await self.team_manager.get_member(team_id, user_id)
            return member and member.role in [UserRole.OWNER, UserRole.ADMIN]

        except Exception as e:
            logger.error(f"Error checking team admin: {e}")
            return False

    async def is_team_member(self, user_id: str, team_id: str) -> bool:
        """Check if user is a member of team"""
        try:
            member = await self.team_manager.get_member(team_id, user_id)
            return member is not None

        except Exception as e:
            logger.error(f"Error checking team membership: {e}")
            return False

    async def get_user_permissions(self,
                                  user_id: str,
                                  team_id: Optional[str] = None) -> List[Permission]:
        """
        Get all permissions for a user

        Args:
            user_id: User ID
            team_id: Optional team context

        Returns:
            List of permissions
        """
        try:
            if team_id:
                member = await self.team_manager.get_member(team_id, user_id)
                if not member:
                    return []

                # Get role permissions
                role_perms = ROLE_PERMISSIONS.get(member.role, [])

                # Add member-specific permissions
                all_perms = set(role_perms) | set(member.permissions)

                return list(all_perms)

            # Global permissions
            # TODO: Implement global roles
            return []

        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []

    async def grant_permission(self,
                              user_id: str,
                              team_id: str,
                              permission: Permission) -> bool:
        """Grant a specific permission to a user in a team"""
        try:
            member = await self.team_manager.get_member(team_id, user_id)
            if not member:
                logger.error(f"User {user_id} not member of team {team_id}")
                return False

            # Add permission if not already granted
            if permission not in member.permissions:
                member.permissions.append(permission)

                # TODO: Update in database
                logger.info(f"Granted {permission.value} to user {user_id} in team {team_id}")

            return True

        except Exception as e:
            logger.error(f"Error granting permission: {e}")
            return False

    async def revoke_permission(self,
                               user_id: str,
                               team_id: str,
                               permission: Permission) -> bool:
        """Revoke a specific permission from a user in a team"""
        try:
            member = await self.team_manager.get_member(team_id, user_id)
            if not member:
                return False

            # Remove permission
            if permission in member.permissions:
                member.permissions.remove(permission)

                # TODO: Update in database
                logger.info(f"Revoked {permission.value} from user {user_id} in team {team_id}")

            return True

        except Exception as e:
            logger.error(f"Error revoking permission: {e}")
            return False

    def get_role_permissions(self, role: UserRole) -> List[Permission]:
        """Get all permissions for a role"""
        return ROLE_PERMISSIONS.get(role, [])

    async def can_manage_team(self, user_id: str, team_id: str) -> bool:
        """Check if user can manage team (owner or admin)"""
        return await self.has_permission(
            user_id,
            Permission.TEAM_UPDATE,
            team_id
        )

    async def can_invite_members(self, user_id: str, team_id: str) -> bool:
        """Check if user can invite members to team"""
        return await self.has_permission(
            user_id,
            Permission.TEAM_INVITE,
            team_id
        )

    async def can_manage_members(self, user_id: str, team_id: str) -> bool:
        """Check if user can manage team members"""
        return await self.is_team_admin(user_id, team_id)

    async def can_delete_team(self, user_id: str, team_id: str) -> bool:
        """Check if user can delete team (owner only)"""
        return await self.is_team_owner(user_id, team_id)


# Decorator for permission checking
def require_permission(permission: Permission, team_id_param: str = "team_id"):
    """
    Decorator to require a permission for an API endpoint

    Usage:
        @require_permission(Permission.AGENT_CREATE)
        async def create_agent(user_id: str, team_id: str, ...):
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id and team_id from kwargs
            user_id = kwargs.get("user_id")
            team_id = kwargs.get(team_id_param)

            if not user_id:
                raise ValueError("user_id required")

            # Check permission
            pm = PermissionManager()
            has_perm = await pm.has_permission(user_id, permission, team_id)

            if not has_perm:
                raise PermissionError(f"User {user_id} lacks permission: {permission.value}")

            # Call original function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_team_role(role: UserRole):
    """
    Decorator to require a specific team role

    Usage:
        @require_team_role(UserRole.ADMIN)
        async def delete_member(user_id: str, team_id: str, ...):
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            team_id = kwargs.get("team_id")

            if not user_id or not team_id:
                raise ValueError("user_id and team_id required")

            # Check role
            tm = TeamManager()
            member = await tm.get_member(team_id, user_id)

            if not member:
                raise PermissionError(f"User {user_id} not member of team {team_id}")

            # Check if role is sufficient
            role_hierarchy = {
                UserRole.GUEST: 0,
                UserRole.VIEWER: 1,
                UserRole.MEMBER: 2,
                UserRole.ADMIN: 3,
                UserRole.OWNER: 4
            }

            if role_hierarchy[member.role] < role_hierarchy[role]:
                raise PermissionError(
                    f"User {user_id} role {member.role.value} insufficient, "
                    f"requires {role.value}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator
