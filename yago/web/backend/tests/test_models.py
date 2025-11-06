"""
Tests for database models
"""
import pytest
import json
from datetime import datetime
from models import Project, User, ClarificationSession, AIProviderUsage


class TestProjectModel:
    """Test Project model"""

    def test_create_project(self, db_session, test_user):
        """Test project creation"""
        project = Project(
            name="Test Project",
            description="A test project",
            status="creating",
            user_id=test_user.id
        )

        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)

        assert project.id is not None
        assert project.name == "Test Project"
        assert project.status == "creating"
        assert project.progress == 0
        assert project.user_id == test_user.id

    def test_project_to_dict(self, db_session, test_user):
        """Test project serialization"""
        project = Project(
            name="Test Project",
            description="Test description",
            status="completed",
            progress=100,
            user_id=test_user.id
        )

        db_session.add(project)
        db_session.commit()

        project_dict = project.to_dict()

        assert project_dict["name"] == "Test Project"
        assert project_dict["status"] == "completed"
        assert project_dict["progress"] == 100
        assert "created_at" in project_dict

    def test_project_status_constraint(self, db_session, test_user):
        """Test project status constraint"""
        project = Project(
            name="Test",
            status="creating",
            user_id=test_user.id
        )

        db_session.add(project)
        db_session.commit()

        # Valid statuses should work
        for status in ['creating', 'in_progress', 'executing', 'completed', 'failed', 'paused']:
            project.status = status
            db_session.commit()


class TestUserModel:
    """Test User model"""

    def test_create_user(self, db_session):
        """Test user creation"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_here",
            full_name="Test User",
            is_active=True,
            is_verified=False
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_verified is False

    def test_user_email_unique(self, db_session):
        """Test that email must be unique"""
        user1 = User(
            email="duplicate@example.com",
            hashed_password="password1"
        )
        user2 = User(
            email="duplicate@example.com",
            hashed_password="password2"
        )

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestClarificationSession:
    """Test ClarificationSession model"""

    def test_create_session(self, db_session, test_project):
        """Test clarification session creation"""
        questions = [
            {"id": "q1", "text": "Question 1?", "type": "text"},
            {"id": "q2", "text": "Question 2?", "type": "select"}
        ]

        session = ClarificationSession(
            project_id=test_project.id,
            project_idea="Test project idea",
            depth="standard",
            questions=json.dumps(questions),
            answers=json.dumps({}),
            total_questions=len(questions),
            is_completed=False
        )

        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)

        assert session.id is not None
        assert session.project_id == test_project.id
        assert session.depth == "standard"
        assert session.total_questions == 2

    def test_session_to_dict(self, db_session, test_project):
        """Test session serialization"""
        session = ClarificationSession(
            project_id=test_project.id,
            project_idea="Test idea",
            depth="minimal",
            questions=json.dumps([]),
            total_questions=0
        )

        db_session.add(session)
        db_session.commit()

        session_dict = session.to_dict()

        assert session_dict["project_id"] == test_project.id
        assert session_dict["depth"] == "minimal"
        assert "created_at" in session_dict


class TestAIProviderUsage:
    """Test AIProviderUsage model"""

    def test_create_usage_record(self, db_session, test_project):
        """Test AI usage record creation"""
        usage = AIProviderUsage(
            project_id=test_project.id,
            provider="openai",
            model="gpt-4",
            request_type="completion",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost=0.003,
            latency_ms=1500,
            success=True
        )

        db_session.add(usage)
        db_session.commit()
        db_session.refresh(usage)

        assert usage.id is not None
        assert usage.provider == "openai"
        assert usage.total_tokens == 150
        assert usage.cost == 0.003
        assert usage.success is True
