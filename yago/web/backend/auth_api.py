"""YAGO v8.0 - Authentication API"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import logging

from yago.auth import (
    SAMLProvider, OAuthProvider, LDAPProvider,
    MFAManager, SessionManager, RBACManager,
    AuthProvider, MFAMethod, UserRole
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Initialize components
mfa_manager = MFAManager()
session_manager = SessionManager()
rbac_manager = RBACManager()

class LoginRequest(BaseModel):
    username: str
    password: str
    provider: str = "local"

class MFAEnableRequest(BaseModel):
    user_id: str
    method: str

class MFAVerifyRequest(BaseModel):
    challenge_id: str
    code: str

@router.post("/login")
async def login(request: LoginRequest):
    """User login"""
    try:
        # Mock user for demo
        from yago.auth.base import User
        import uuid
        user = User(
            user_id=f"user_{uuid.uuid4().hex[:12]}",
            username=request.username,
            email=f"{request.username}@example.com",
            roles=[UserRole.USER],
            provider=AuthProvider(request.provider)
        )
        session = await session_manager.create_session(user)
        return {"success": True, "session_id": session.session_id, "user_id": user.user_id}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout(session_id: str = Header(..., alias="X-Session-ID")):
    """User logout"""
    success = await session_manager.revoke_session(session_id)
    return {"success": success}

@router.post("/mfa/enable")
async def enable_mfa(request: MFAEnableRequest):
    """Enable MFA"""
    result = await mfa_manager.enable_mfa(request.user_id, MFAMethod(request.method))
    return {"success": True, "data": result}

@router.post("/mfa/verify")
async def verify_mfa(request: MFAVerifyRequest):
    """Verify MFA code"""
    verified = await mfa_manager.verify_challenge(request.challenge_id, request.code)
    return {"success": verified}

@router.get("/session")
async def get_session(session_id: str = Header(..., alias="X-Session-ID")):
    """Get session info"""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session.session_id, "user_id": session.user_id, "expires_at": session.expires_at.isoformat()}

@router.get("/providers")
async def list_providers():
    """List auth providers"""
    return {"providers": [{"id": p.value, "name": p.value.upper()} for p in AuthProvider]}

@router.get("/roles")
async def list_roles():
    """List user roles"""
    return {"roles": [{"id": r.value, "name": r.value.title()} for r in UserRole]}

auth_router = router
