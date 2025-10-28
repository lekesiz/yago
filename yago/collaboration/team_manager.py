"""
YAGO v7.2 - Team Management
Team and team membership management
"""

import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

from .models import (
    Team,
    TeamMember,
    Invitation,
    UserRole,
    InvitationStatus
)
from ..config import DATABASE_PATH

logger = logging.getLogger(__name__)


class TeamManager:
    """
    Manages teams and team memberships

    Responsibilities:
    - Create/update/delete teams
    - Manage team members
    - Handle invitations
    - Role management
    """

    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize team manager"""
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Teams table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                avatar_url TEXT,
                owner_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                settings TEXT,
                max_members INTEGER,
                metadata TEXT,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        """)

        # Team members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                permissions TEXT,
                joined_at TEXT NOT NULL,
                invited_by TEXT,
                metadata TEXT,
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(team_id, user_id)
            )
        """)

        # Invitations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invitations (
                id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                invited_by TEXT NOT NULL,
                status TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                accepted_at TEXT,
                metadata TEXT,
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (invited_by) REFERENCES users(id)
            )
        """)

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_teams_owner ON teams(owner_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invitations_team ON invitations(team_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invitations_email ON invitations(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invitations_token ON invitations(token)")

        conn.commit()
        conn.close()

    async def create_team(self,
                         name: str,
                         owner_id: str,
                         description: Optional[str] = None,
                         **kwargs) -> Optional[Team]:
        """Create a new team"""
        try:
            team_id = f"team_{secrets.token_hex(8)}"

            team = Team(
                id=team_id,
                name=name,
                description=description,
                owner_id=owner_id,
                **kwargs
            )

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO teams (
                    id, name, description, avatar_url, owner_id,
                    created_at, updated_at, settings, max_members, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                team.id,
                team.name,
                team.description,
                team.avatar_url,
                team.owner_id,
                team.created_at.isoformat(),
                team.updated_at.isoformat(),
                str(team.settings),
                team.max_members,
                str(team.metadata)
            ))

            conn.commit()
            conn.close()

            # Add owner as member
            await self.add_member(team.id, owner_id, UserRole.OWNER)

            logger.info(f"Team created: {team.id} ({team.name})")
            return team

        except Exception as e:
            logger.error(f"Error creating team: {e}")
            return None

    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get team by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return self._row_to_team(row)

        except Exception as e:
            logger.error(f"Error getting team {team_id}: {e}")
            return None

    async def update_team(self, team_id: str, **updates) -> Optional[Team]:
        """Update team fields"""
        try:
            team = await self.get_team(team_id)
            if not team:
                return None

            # Update fields
            for key, value in updates.items():
                if hasattr(team, key):
                    setattr(team, key, value)

            team.updated_at = datetime.utcnow()

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE teams SET
                    name = ?,
                    description = ?,
                    avatar_url = ?,
                    updated_at = ?,
                    settings = ?,
                    max_members = ?,
                    metadata = ?
                WHERE id = ?
            """, (
                team.name,
                team.description,
                team.avatar_url,
                team.updated_at.isoformat(),
                str(team.settings),
                team.max_members,
                str(team.metadata),
                team.id
            ))

            conn.commit()
            conn.close()

            logger.info(f"Team updated: {team.id}")
            return team

        except Exception as e:
            logger.error(f"Error updating team {team_id}: {e}")
            return None

    async def delete_team(self, team_id: str) -> bool:
        """Delete a team and all memberships"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete team members
            cursor.execute("DELETE FROM team_members WHERE team_id = ?", (team_id,))

            # Delete invitations
            cursor.execute("DELETE FROM invitations WHERE team_id = ?", (team_id,))

            # Delete team
            cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))

            deleted = cursor.rowcount > 0

            conn.commit()
            conn.close()

            if deleted:
                logger.info(f"Team deleted: {team_id}")

            return deleted

        except Exception as e:
            logger.error(f"Error deleting team {team_id}: {e}")
            return False

    async def add_member(self,
                        team_id: str,
                        user_id: str,
                        role: UserRole = UserRole.MEMBER,
                        invited_by: Optional[str] = None) -> Optional[TeamMember]:
        """Add a member to a team"""
        try:
            member_id = f"member_{secrets.token_hex(8)}"

            member = TeamMember(
                id=member_id,
                team_id=team_id,
                user_id=user_id,
                role=role,
                invited_by=invited_by
            )

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO team_members (
                    id, team_id, user_id, role, permissions,
                    joined_at, invited_by, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                member.id,
                member.team_id,
                member.user_id,
                member.role.value,
                str(member.permissions),
                member.joined_at.isoformat(),
                member.invited_by,
                str(member.metadata)
            ))

            conn.commit()
            conn.close()

            logger.info(f"Member added to team {team_id}: {user_id}")
            return member

        except sqlite3.IntegrityError:
            logger.warning(f"User {user_id} already member of team {team_id}")
            return None
        except Exception as e:
            logger.error(f"Error adding member: {e}")
            return None

    async def remove_member(self, team_id: str, user_id: str) -> bool:
        """Remove a member from a team"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM team_members
                WHERE team_id = ? AND user_id = ?
            """, (team_id, user_id))

            removed = cursor.rowcount > 0

            conn.commit()
            conn.close()

            if removed:
                logger.info(f"Member removed from team {team_id}: {user_id}")

            return removed

        except Exception as e:
            logger.error(f"Error removing member: {e}")
            return False

    async def update_member_role(self,
                                 team_id: str,
                                 user_id: str,
                                 role: UserRole) -> bool:
        """Update a member's role"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE team_members
                SET role = ?
                WHERE team_id = ? AND user_id = ?
            """, (role.value, team_id, user_id))

            updated = cursor.rowcount > 0

            conn.commit()
            conn.close()

            if updated:
                logger.info(f"Member role updated in team {team_id}: {user_id} -> {role.value}")

            return updated

        except Exception as e:
            logger.error(f"Error updating member role: {e}")
            return False

    async def get_member(self, team_id: str, user_id: str) -> Optional[TeamMember]:
        """Get team member"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM team_members
                WHERE team_id = ? AND user_id = ?
            """, (team_id, user_id))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return self._row_to_member(row)

        except Exception as e:
            logger.error(f"Error getting member: {e}")
            return None

    async def list_members(self, team_id: str) -> List[TeamMember]:
        """List all members of a team"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM team_members
                WHERE team_id = ?
                ORDER BY joined_at ASC
            """, (team_id,))

            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_member(row) for row in rows]

        except Exception as e:
            logger.error(f"Error listing members: {e}")
            return []

    async def list_user_teams(self, user_id: str) -> List[Team]:
        """List all teams a user belongs to"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT t.* FROM teams t
                JOIN team_members tm ON t.id = tm.team_id
                WHERE tm.user_id = ?
                ORDER BY t.created_at DESC
            """, (user_id,))

            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_team(row) for row in rows]

        except Exception as e:
            logger.error(f"Error listing user teams: {e}")
            return []

    async def create_invitation(self,
                               team_id: str,
                               email: str,
                               role: UserRole,
                               invited_by: str,
                               expires_in_days: int = 7) -> Optional[Invitation]:
        """Create team invitation"""
        try:
            invite_id = f"invite_{secrets.token_hex(8)}"
            token = secrets.token_urlsafe(32)

            invitation = Invitation(
                id=invite_id,
                team_id=team_id,
                email=email,
                role=role,
                invited_by=invited_by,
                token=token,
                expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
            )

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO invitations (
                    id, team_id, email, role, invited_by, status, token,
                    created_at, expires_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invitation.id,
                invitation.team_id,
                invitation.email,
                invitation.role.value,
                invitation.invited_by,
                invitation.status.value,
                invitation.token,
                invitation.created_at.isoformat(),
                invitation.expires_at.isoformat(),
                str(invitation.metadata)
            ))

            conn.commit()
            conn.close()

            logger.info(f"Invitation created: {invite_id} for {email}")
            return invitation

        except Exception as e:
            logger.error(f"Error creating invitation: {e}")
            return None

    async def accept_invitation(self, token: str, user_id: str) -> bool:
        """Accept team invitation"""
        try:
            # Get invitation
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM invitations WHERE token = ?
            """, (token,))

            row = cursor.fetchone()

            if not row:
                logger.error("Invitation not found")
                conn.close()
                return False

            invitation = self._row_to_invitation(row)

            # Check if expired
            if invitation.expires_at < datetime.utcnow():
                logger.error("Invitation expired")
                cursor.execute("""
                    UPDATE invitations SET status = ? WHERE id = ?
                """, (InvitationStatus.EXPIRED.value, invitation.id))
                conn.commit()
                conn.close()
                return False

            # Check if already accepted
            if invitation.status != InvitationStatus.PENDING:
                logger.error(f"Invitation already {invitation.status.value}")
                conn.close()
                return False

            # Add member to team
            member = await self.add_member(
                invitation.team_id,
                user_id,
                invitation.role,
                invitation.invited_by
            )

            if not member:
                conn.close()
                return False

            # Update invitation status
            cursor.execute("""
                UPDATE invitations
                SET status = ?, accepted_at = ?
                WHERE id = ?
            """, (
                InvitationStatus.ACCEPTED.value,
                datetime.utcnow().isoformat(),
                invitation.id
            ))

            conn.commit()
            conn.close()

            logger.info(f"Invitation accepted: {invitation.id}")
            return True

        except Exception as e:
            logger.error(f"Error accepting invitation: {e}")
            return False

    async def list_team_invitations(self, team_id: str) -> List[Invitation]:
        """List invitations for a team"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM invitations
                WHERE team_id = ?
                ORDER BY created_at DESC
            """, (team_id,))

            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_invitation(row) for row in rows]

        except Exception as e:
            logger.error(f"Error listing invitations: {e}")
            return []

    def _row_to_team(self, row) -> Team:
        """Convert database row to Team object"""
        import ast

        return Team(
            id=row[0],
            name=row[1],
            description=row[2],
            avatar_url=row[3],
            owner_id=row[4],
            created_at=datetime.fromisoformat(row[5]),
            updated_at=datetime.fromisoformat(row[6]),
            settings=ast.literal_eval(row[7]) if row[7] else {},
            max_members=row[8],
            metadata=ast.literal_eval(row[9]) if row[9] else {}
        )

    def _row_to_member(self, row) -> TeamMember:
        """Convert database row to TeamMember object"""
        import ast

        return TeamMember(
            id=row[0],
            team_id=row[1],
            user_id=row[2],
            role=UserRole(row[3]),
            permissions=[p for p in ast.literal_eval(row[4])] if row[4] else [],
            joined_at=datetime.fromisoformat(row[5]),
            invited_by=row[6],
            metadata=ast.literal_eval(row[7]) if row[7] else {}
        )

    def _row_to_invitation(self, row) -> Invitation:
        """Convert database row to Invitation object"""
        import ast

        return Invitation(
            id=row[0],
            team_id=row[1],
            email=row[2],
            role=UserRole(row[3]),
            invited_by=row[4],
            status=InvitationStatus(row[5]),
            token=row[6],
            created_at=datetime.fromisoformat(row[7]),
            expires_at=datetime.fromisoformat(row[8]),
            accepted_at=datetime.fromisoformat(row[9]) if row[9] else None,
            metadata=ast.literal_eval(row[10]) if row[10] else {}
        )
