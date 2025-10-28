"""YAGO v8.0 - Session Manager"""
import logging
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
from .base import Session, User, AuthProvider

logger = logging.getLogger(__name__)

class SessionManager:
    """Manage user sessions"""
    
    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = session_timeout_minutes
    
    async def create_session(self, user: User, ip_address: Optional[str] = None) -> Session:
        """Create new session"""
        session = Session(
            session_id=f"sess_{uuid.uuid4().hex[:12]}",
            user_id=user.user_id,
            provider=user.provider,
            expires_at=datetime.utcnow() + timedelta(minutes=self.session_timeout),
            ip_address=ip_address
        )
        self.sessions[session.session_id] = session
        logger.info(f"Session created for user {user.user_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session and datetime.utcnow() < session.expires_at:
            session.last_activity = datetime.utcnow()
            return session
        return None
    
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session revoked: {session_id}")
            return True
        return False
    
    def cleanup_expired(self):
        """Remove expired sessions"""
        now = datetime.utcnow()
        expired = [sid for sid, sess in self.sessions.items() if sess.expires_at < now]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
