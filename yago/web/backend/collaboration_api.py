"""
YAGO v7.2 - Team Collaboration API
RESTful API for user and team management
"""

from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import logging

from yago.collaboration import (
    UserManager,
    TeamManager,
    PermissionManager,
    User,
    Team,
    UserRole,
    UserStatus,
    Permission
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/collaboration", tags=["Collaboration"])

# Initialize managers
user_manager = UserManager()
team_manager = TeamManager()
permission_manager = PermissionManager(user_manager, team_manager)


# Request/Response Models

class UserCreateRequest(BaseModel):
    """Request to create user"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """Request to update user"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, bool]] = None


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    old_password: str
    new_password: str


class TeamCreateRequest(BaseModel):
    """Request to create team"""
    name: str
    description: Optional[str] = None


class TeamUpdateRequest(BaseModel):
    """Request to update team"""
    name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class InvitationCreateRequest(BaseModel):
    """Request to create invitation"""
    email: EmailStr
    role: UserRole = UserRole.MEMBER


class MemberRoleUpdateRequest(BaseModel):
    """Request to update member role"""
    role: UserRole


# Helper to get current user from header
async def get_current_user(authorization: str = Header(None)) -> str:
    """Extract user ID from authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )

    # For now, simple user_id extraction
    # TODO: Implement proper JWT/session validation
    if authorization.startswith("Bearer "):
        return authorization[7:]

    return authorization


# User Endpoints

@router.post("/users", response_model=dict)
async def create_user(request: UserCreateRequest):
    """Create a new user"""
    try:
        user = await user_manager.create_user(
            email=request.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed (email or username may already exist)"
            )

        return {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "status": user.status.value
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/auth/login")
async def login(request: LoginRequest):
    """User login"""
    try:
        user = await user_manager.authenticate(request.email, request.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # TODO: Generate JWT token
        token = f"user_{user.id}"

        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/users/me")
async def get_current_user_info(authorization: str = Header(None)):
    """Get current user information"""
    try:
        user_id = await get_current_user(authorization)
        user = await user_manager.get_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "status": user.status.value,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "preferences": user.preferences,
            "notification_settings": user.notification_settings
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )


@router.put("/users/me")
async def update_current_user(
    request: UserUpdateRequest,
    authorization: str = Header(None)
):
    """Update current user"""
    try:
        user_id = await get_current_user(authorization)

        updates = {}
        if request.full_name is not None:
            updates["full_name"] = request.full_name
        if request.avatar_url is not None:
            updates["avatar_url"] = request.avatar_url
        if request.preferences is not None:
            updates["preferences"] = request.preferences
        if request.notification_settings is not None:
            updates["notification_settings"] = request.notification_settings

        user = await user_manager.update_user(user_id, **updates)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.post("/users/me/password")
async def change_password(
    request: PasswordChangeRequest,
    authorization: str = Header(None)
):
    """Change user password"""
    try:
        user_id = await get_current_user(authorization)

        success = await user_manager.change_password(
            user_id,
            request.old_password,
            request.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password change failed (incorrect old password)"
            )

        return {"success": True, "message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.get("/users/search")
async def search_users(
    query: str,
    limit: int = 20,
    authorization: str = Header(None)
):
    """Search users"""
    try:
        user_id = await get_current_user(authorization)

        users = await user_manager.search_users(query, limit)

        return {
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "username": u.username,
                    "full_name": u.full_name,
                    "avatar_url": u.avatar_url
                }
                for u in users
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


# Team Endpoints

@router.post("/teams")
async def create_team(
    request: TeamCreateRequest,
    authorization: str = Header(None)
):
    """Create a new team"""
    try:
        user_id = await get_current_user(authorization)

        team = await team_manager.create_team(
            name=request.name,
            owner_id=user_id,
            description=request.description
        )

        if not team:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Team creation failed"
            )

        return {
            "success": True,
            "team": {
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "owner_id": team.owner_id,
                "created_at": team.created_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating team: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create team"
        )


@router.get("/teams")
async def list_my_teams(authorization: str = Header(None)):
    """List current user's teams"""
    try:
        user_id = await get_current_user(authorization)

        teams = await team_manager.list_user_teams(user_id)

        return {
            "teams": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "owner_id": t.owner_id,
                    "created_at": t.created_at.isoformat()
                }
                for t in teams
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing teams: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list teams"
        )


@router.get("/teams/{team_id}")
async def get_team(team_id: str, authorization: str = Header(None)):
    """Get team details"""
    try:
        user_id = await get_current_user(authorization)

        # Check if user is member
        if not await permission_manager.is_team_member(user_id, team_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        team = await team_manager.get_team(team_id)

        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        return {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "owner_id": team.owner_id,
            "avatar_url": team.avatar_url,
            "created_at": team.created_at.isoformat(),
            "settings": team.settings,
            "max_members": team.max_members
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get team"
        )


@router.put("/teams/{team_id}")
async def update_team(
    team_id: str,
    request: TeamUpdateRequest,
    authorization: str = Header(None)
):
    """Update team"""
    try:
        user_id = await get_current_user(authorization)

        # Check permission
        if not await permission_manager.can_manage_team(user_id, team_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )

        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        if request.avatar_url is not None:
            updates["avatar_url"] = request.avatar_url
        if request.settings is not None:
            updates["settings"] = request.settings

        team = await team_manager.update_team(team_id, **updates)

        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        return {"success": True, "team": {"id": team.id, "name": team.name}}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating team: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update team"
        )


@router.delete("/teams/{team_id}")
async def delete_team(team_id: str, authorization: str = Header(None)):
    """Delete team"""
    try:
        user_id = await get_current_user(authorization)

        # Check permission (owner only)
        if not await permission_manager.can_delete_team(user_id, team_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owner can delete team"
            )

        success = await team_manager.delete_team(team_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        return {"success": True, "message": "Team deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting team: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete team"
        )


# Team Member Endpoints

@router.get("/teams/{team_id}/members")
async def list_team_members(team_id: str, authorization: str = Header(None)):
    """List team members"""
    try:
        user_id = await get_current_user(authorization)

        # Check if user is member
        if not await permission_manager.is_team_member(user_id, team_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        members = await team_manager.list_members(team_id)

        return {
            "members": [
                {
                    "id": m.id,
                    "user_id": m.user_id,
                    "role": m.role.value,
                    "joined_at": m.joined_at.isoformat()
                }
                for m in members
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing members: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list members"
        )


@router.delete("/teams/{team_id}/members/{user_id_to_remove}")
async def remove_team_member(
    team_id: str,
    user_id_to_remove: str,
    authorization: str = Header(None)
):
    """Remove team member"""
    try:
        user_id = await get_current_user(authorization)

        # Check permission
        if not await permission_manager.can_manage_members(user_id, team_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )

        success = await team_manager.remove_member(team_id, user_id_to_remove)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        return {"success": True, "message": "Member removed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove member"
        )


@router.put("/teams/{team_id}/members/{member_user_id}/role")
async def update_member_role(
    team_id: str,
    member_user_id: str,
    request: MemberRoleUpdateRequest,
    authorization: str = Header(None)
):
    """Update member role"""
    try:
        user_id = await get_current_user(authorization)

        # Check permission
        if not await permission_manager.can_manage_members(user_id, team_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )

        success = await team_manager.update_member_role(
            team_id,
            member_user_id,
            request.role
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        return {"success": True, "message": "Role updated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role"
        )


# Invitation Endpoints

@router.post("/teams/{team_id}/invitations")
async def create_invitation(
    team_id: str,
    request: InvitationCreateRequest,
    authorization: str = Header(None)
):
    """Create team invitation"""
    try:
        user_id = await get_current_user(authorization)

        # Check permission
        if not await permission_manager.can_invite_members(user_id, team_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )

        invitation = await team_manager.create_invitation(
            team_id,
            request.email,
            request.role,
            user_id
        )

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invitation creation failed"
            )

        return {
            "success": True,
            "invitation": {
                "id": invitation.id,
                "email": invitation.email,
                "role": invitation.role.value,
                "token": invitation.token,
                "expires_at": invitation.expires_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create invitation"
        )


@router.post("/invitations/{token}/accept")
async def accept_invitation(token: str, authorization: str = Header(None)):
    """Accept team invitation"""
    try:
        user_id = await get_current_user(authorization)

        success = await team_manager.accept_invitation(token, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation acceptance failed (invalid or expired)"
            )

        return {"success": True, "message": "Invitation accepted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept invitation"
        )


@router.get("/teams/{team_id}/invitations")
async def list_team_invitations(team_id: str, authorization: str = Header(None)):
    """List team invitations"""
    try:
        user_id = await get_current_user(authorization)

        # Check permission
        if not await permission_manager.can_manage_members(user_id, team_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )

        invitations = await team_manager.list_team_invitations(team_id)

        return {
            "invitations": [
                {
                    "id": inv.id,
                    "email": inv.email,
                    "role": inv.role.value,
                    "status": inv.status.value,
                    "created_at": inv.created_at.isoformat(),
                    "expires_at": inv.expires_at.isoformat()
                }
                for inv in invitations
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing invitations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list invitations"
        )


# Export router
collaboration_router = router
