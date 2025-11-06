"""
Tests for authentication service
"""
import pytest
from services.auth_service import AuthService
from models import User


class TestAuthService:
    """Test authentication service"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)

        # Hash should be different from plain password
        assert hashed != password

        # Verification should work
        assert AuthService.verify_password(password, hashed)

        # Wrong password should fail
        assert not AuthService.verify_password("wrongpassword", hashed)

    def test_password_hash_is_unique(self):
        """Test that same password produces different hashes"""
        password = "testpassword123"
        hash1 = AuthService.get_password_hash(password)
        hash2 = AuthService.get_password_hash(password)

        # Hashes should be different (bcrypt uses salt)
        assert hash1 != hash2

        # But both should verify
        assert AuthService.verify_password(password, hash1)
        assert AuthService.verify_password(password, hash2)

    def test_create_access_token(self):
        """Test JWT token creation"""
        user_id = "test-user-123"
        token = AuthService.create_access_token(data={"sub": user_id})

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token(self):
        """Test JWT token verification"""
        user_id = "test-user-123"
        token = AuthService.create_access_token(data={"sub": user_id})

        payload = AuthService.verify_token(token)

        assert payload is not None
        assert payload["sub"] == user_id
        assert "exp" in payload

    def test_verify_invalid_token(self):
        """Test that invalid tokens are rejected"""
        invalid_token = "invalid.token.here"
        payload = AuthService.verify_token(invalid_token)

        assert payload is None

    def test_create_user(self, db_session):
        """Test user creation"""
        email = "newuser@example.com"
        password = "newpassword123"
        full_name = "New User"

        user = AuthService.create_user(
            db=db_session,
            email=email,
            password=password,
            full_name=full_name
        )

        assert user is not None
        assert user.email == email
        assert user.full_name == full_name
        assert user.is_active is True
        assert user.is_verified is False

        # Password should be hashed
        assert user.hashed_password != password
        assert AuthService.verify_password(password, user.hashed_password)

    def test_create_duplicate_user(self, db_session, test_user):
        """Test that duplicate email is rejected"""
        with pytest.raises(ValueError, match="already exists"):
            AuthService.create_user(
                db=db_session,
                email=test_user.email,
                password="password123"
            )

    def test_authenticate_user_success(self, db_session, test_user):
        """Test successful user authentication"""
        user = AuthService.authenticate_user(
            db=db_session,
            email=test_user.email,
            password="testpassword123"
        )

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_authenticate_user_wrong_password(self, db_session, test_user):
        """Test authentication with wrong password"""
        user = AuthService.authenticate_user(
            db=db_session,
            email=test_user.email,
            password="wrongpassword"
        )

        assert user is None

    def test_authenticate_user_nonexistent(self, db_session):
        """Test authentication with non-existent user"""
        user = AuthService.authenticate_user(
            db=db_session,
            email="nonexistent@example.com",
            password="password123"
        )

        assert user is None

    def test_authenticate_inactive_user(self, db_session, test_user):
        """Test that inactive users cannot authenticate"""
        test_user.is_active = False
        db_session.commit()

        user = AuthService.authenticate_user(
            db=db_session,
            email=test_user.email,
            password="testpassword123"
        )

        assert user is None
