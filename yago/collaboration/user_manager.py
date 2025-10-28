"""
YAGO v7.2 - User Management
User account management and authentication
"""

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

from .models import User, UserStatus, ActivityLog
from ..config import DATABASE_PATH

logger = logging.getLogger(__name__)


class UserManager:
    """
    Manages user accounts

    Responsibilities:
    - Create/update/delete users
    - User authentication
    - Password management
    - User search and listing
    - Activity logging
    """

    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize user manager"""
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                avatar_url TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                password_hash TEXT,
                two_factor_enabled INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_login TEXT,
                preferences TEXT,
                notification_settings TEXT,
                metadata TEXT
            )
        """)

        # Activity logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                team_id TEXT,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_team ON activity_logs(team_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_logs(timestamp)")

        conn.commit()
        conn.close()

    async def create_user(self,
                         email: str,
                         username: str,
                         password: str,
                         full_name: Optional[str] = None,
                         **kwargs) -> Optional[User]:
        """
        Create a new user

        Args:
            email: User email
            username: Username
            password: Plain text password
            full_name: Full name
            **kwargs: Additional user fields

        Returns:
            Created user or None if failed
        """
        try:
            # Generate user ID
            user_id = f"user_{secrets.token_hex(8)}"

            # Hash password
            password_hash = self._hash_password(password)

            # Create user object
            user = User(
                id=user_id,
                email=email,
                username=username,
                full_name=full_name,
                password_hash=password_hash,
                status=UserStatus.ACTIVE,
                **kwargs
            )

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO users (
                    id, email, username, full_name, avatar_url, status,
                    password_hash, two_factor_enabled, created_at, updated_at,
                    preferences, notification_settings, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.id,
                user.email,
                user.username,
                user.full_name,
                user.avatar_url,
                user.status.value,
                user.password_hash,
                int(user.two_factor_enabled),
                user.created_at.isoformat(),
                user.updated_at.isoformat(),
                str(user.preferences),
                str(user.notification_settings),
                str(user.metadata)
            ))

            conn.commit()
            conn.close()

            # Log activity
            await self.log_activity(
                user_id=user.id,
                action="user.created",
                resource_type="user",
                resource_id=user.id
            )

            logger.info(f"User created: {user.id} ({user.email})")
            return user

        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed (duplicate): {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return self._row_to_user(row)

        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return self._row_to_user(row)

        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return self._row_to_user(row)

        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None

    async def update_user(self, user_id: str, **updates) -> Optional[User]:
        """Update user fields"""
        try:
            user = await self.get_user(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return None

            # Update fields
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            user.updated_at = datetime.utcnow()

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users SET
                    email = ?,
                    username = ?,
                    full_name = ?,
                    avatar_url = ?,
                    status = ?,
                    updated_at = ?,
                    preferences = ?,
                    notification_settings = ?,
                    metadata = ?
                WHERE id = ?
            """, (
                user.email,
                user.username,
                user.full_name,
                user.avatar_url,
                user.status.value,
                user.updated_at.isoformat(),
                str(user.preferences),
                str(user.notification_settings),
                str(user.metadata),
                user.id
            ))

            conn.commit()
            conn.close()

            # Log activity
            await self.log_activity(
                user_id=user.id,
                action="user.updated",
                resource_type="user",
                resource_id=user.id
            )

            logger.info(f"User updated: {user.id}")
            return user

        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            deleted = cursor.rowcount > 0

            conn.commit()
            conn.close()

            if deleted:
                logger.info(f"User deleted: {user_id}")

            return deleted

        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    async def list_users(self,
                        status: Optional[UserStatus] = None,
                        limit: int = 100,
                        offset: int = 0) -> List[User]:
        """List users with optional filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if status:
                cursor.execute("""
                    SELECT * FROM users
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (status.value, limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM users
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))

            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_user(row) for row in rows]

        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    async def search_users(self, query: str, limit: int = 20) -> List[User]:
        """Search users by email, username, or name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT * FROM users
                WHERE email LIKE ? OR username LIKE ? OR full_name LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (search_pattern, search_pattern, search_pattern, limit))

            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_user(row) for row in rows]

        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None

            if user.status != UserStatus.ACTIVE:
                logger.warning(f"Inactive user login attempt: {email}")
                return None

            # Verify password
            if not self._verify_password(password, user.password_hash):
                return None

            # Update last login
            user.last_login = datetime.utcnow()
            await self.update_user(user.id, last_login=user.last_login)

            # Log activity
            await self.log_activity(
                user_id=user.id,
                action="user.login",
                resource_type="user",
                resource_id=user.id
            )

            return user

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return False

            # Verify old password
            if not self._verify_password(old_password, user.password_hash):
                return False

            # Hash new password
            new_hash = self._hash_password(new_password)

            # Update in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users SET password_hash = ?, updated_at = ?
                WHERE id = ?
            """, (new_hash, datetime.utcnow().isoformat(), user_id))

            conn.commit()
            conn.close()

            # Log activity
            await self.log_activity(
                user_id=user.id,
                action="user.password_changed",
                resource_type="user",
                resource_id=user.id
            )

            logger.info(f"Password changed for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False

    async def log_activity(self,
                          user_id: str,
                          action: str,
                          resource_type: str,
                          resource_id: str,
                          team_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None,
                          ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None):
        """Log user activity"""
        try:
            log_id = f"log_{secrets.token_hex(8)}"

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO activity_logs (
                    id, user_id, team_id, action, resource_type, resource_id,
                    timestamp, metadata, ip_address, user_agent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_id,
                user_id,
                team_id,
                action,
                resource_type,
                resource_id,
                datetime.utcnow().isoformat(),
                str(metadata or {}),
                ip_address,
                user_agent
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error logging activity: {e}")

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash

    def _row_to_user(self, row) -> User:
        """Convert database row to User object"""
        import ast

        return User(
            id=row[0],
            email=row[1],
            username=row[2],
            full_name=row[3],
            avatar_url=row[4],
            status=UserStatus(row[5]),
            password_hash=row[6],
            two_factor_enabled=bool(row[7]),
            created_at=datetime.fromisoformat(row[8]),
            updated_at=datetime.fromisoformat(row[9]),
            last_login=datetime.fromisoformat(row[10]) if row[10] else None,
            preferences=ast.literal_eval(row[11]) if row[11] else {},
            notification_settings=ast.literal_eval(row[12]) if row[12] else {},
            metadata=ast.literal_eval(row[13]) if row[13] else {}
        )
