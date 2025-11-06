"""
Tests for input validation utilities
"""
import pytest
from pydantic import ValidationError
from utils.validation import (
    ValidationUtils,
    ProjectCreateRequest,
    UserRegisterRequest,
    ClarificationStartRequest,
    PaginationParams
)


class TestValidationUtils:
    """Test validation utility functions"""

    def test_contains_sql_injection(self):
        """Test SQL injection detection"""
        # Safe strings
        assert not ValidationUtils.contains_sql_injection("Normal project name")
        assert not ValidationUtils.contains_sql_injection("Project-123")

        # Dangerous strings
        assert ValidationUtils.contains_sql_injection("'; DROP TABLE users--")
        assert ValidationUtils.contains_sql_injection("1' OR '1'='1")
        assert ValidationUtils.contains_sql_injection("SELECT * FROM users")
        assert ValidationUtils.contains_sql_injection("'; DELETE FROM projects")

    def test_contains_xss(self):
        """Test XSS detection"""
        # Safe strings
        assert not ValidationUtils.contains_xss("Normal text")
        assert not ValidationUtils.contains_xss("<b>Bold text</b>")

        # Dangerous strings
        assert ValidationUtils.contains_xss("<script>alert('XSS')</script>")
        assert ValidationUtils.contains_xss("javascript:alert(1)")
        assert ValidationUtils.contains_xss("<img onerror='alert(1)'>")
        assert ValidationUtils.contains_xss("<iframe src='evil.com'></iframe>")

    def test_sanitize_string(self):
        """Test string sanitization"""
        # Whitespace trimming
        assert ValidationUtils.sanitize_string("  text  ") == "text"

        # Length limiting
        long_text = "a" * 1000
        assert len(ValidationUtils.sanitize_string(long_text, 10)) == 10

    def test_validate_safe_string(self):
        """Test safe string validation"""
        # Safe strings should pass
        safe = ValidationUtils.validate_safe_string("Normal text", "test_field")
        assert safe == "Normal text"

        # SQL injection should fail
        with pytest.raises(ValueError, match="SQL patterns"):
            ValidationUtils.validate_safe_string("'; DROP TABLE", "test_field")

        # XSS should fail
        with pytest.raises(ValueError, match="script patterns"):
            ValidationUtils.validate_safe_string("<script>alert(1)</script>", "test_field")


class TestProjectCreateRequest:
    """Test project creation validation"""

    def test_valid_project(self):
        """Test valid project creation request"""
        request = ProjectCreateRequest(
            name="My Project",
            description="A test project",
            primary_model="gpt-4",
            temperature=0.7
        )

        assert request.name == "My Project"
        assert request.description == "A test project"
        assert request.temperature == 0.7

    def test_empty_name(self):
        """Test that empty name is rejected"""
        with pytest.raises(ValidationError):
            ProjectCreateRequest(name="   ")

    def test_sql_injection_in_name(self):
        """Test SQL injection in name is rejected"""
        with pytest.raises(ValidationError):
            ProjectCreateRequest(name="'; DROP TABLE projects--")

    def test_xss_in_description(self):
        """Test XSS in description is rejected"""
        with pytest.raises(ValidationError):
            ProjectCreateRequest(
                name="Project",
                description="<script>alert('XSS')</script>"
            )

    def test_invalid_strategy(self):
        """Test invalid strategy is rejected"""
        with pytest.raises(ValidationError):
            ProjectCreateRequest(
                name="Project",
                strategy="invalid_strategy"
            )

    def test_temperature_range(self):
        """Test temperature validation"""
        # Valid range
        ProjectCreateRequest(name="Project", temperature=0.0)
        ProjectCreateRequest(name="Project", temperature=2.0)

        # Invalid range
        with pytest.raises(ValidationError):
            ProjectCreateRequest(name="Project", temperature=-0.1)

        with pytest.raises(ValidationError):
            ProjectCreateRequest(name="Project", temperature=2.1)


class TestUserRegisterRequest:
    """Test user registration validation"""

    def test_valid_user(self):
        """Test valid user registration"""
        request = UserRegisterRequest(
            email="test@example.com",
            password="StrongPass123!",
            full_name="Test User"
        )

        assert request.email == "test@example.com"
        assert request.password == "StrongPass123!"

    def test_invalid_email(self):
        """Test invalid email is rejected"""
        with pytest.raises(ValidationError):
            UserRegisterRequest(
                email="invalid-email",
                password="StrongPass123!"
            )

    def test_weak_password(self):
        """Test weak passwords are rejected"""
        # Too short
        with pytest.raises(ValidationError, match="at least 8 characters"):
            UserRegisterRequest(
                email="test@example.com",
                password="Short1!"
            )

        # No uppercase
        with pytest.raises(ValidationError, match="uppercase"):
            UserRegisterRequest(
                email="test@example.com",
                password="lowercase123!"
            )

        # No lowercase
        with pytest.raises(ValidationError, match="lowercase"):
            UserRegisterRequest(
                email="test@example.com",
                password="UPPERCASE123!"
            )

        # No digit
        with pytest.raises(ValidationError, match="digit"):
            UserRegisterRequest(
                email="test@example.com",
                password="NoDigits!"
            )

        # No special character
        with pytest.raises(ValidationError, match="special character"):
            UserRegisterRequest(
                email="test@example.com",
                password="NoSpecial123"
            )


class TestClarificationStartRequest:
    """Test clarification session validation"""

    def test_valid_request(self):
        """Test valid clarification request"""
        request = ClarificationStartRequest(
            project_idea="Build a web application for task management",
            depth="standard"
        )

        assert len(request.project_idea) >= 10

    def test_too_short_idea(self):
        """Test that too short ideas are rejected"""
        with pytest.raises(ValidationError):
            ClarificationStartRequest(
                project_idea="Too short"
            )


class TestPaginationParams:
    """Test pagination parameter validation"""

    def test_valid_params(self):
        """Test valid pagination parameters"""
        params = PaginationParams(skip=0, limit=20)
        assert params.skip == 0
        assert params.limit == 20

    def test_limit_bounds(self):
        """Test limit boundaries"""
        # Valid range
        PaginationParams(limit=1)
        PaginationParams(limit=100)

        # Too small
        with pytest.raises(ValidationError):
            PaginationParams(limit=0)

        # Too large
        with pytest.raises(ValidationError):
            PaginationParams(limit=101)

    def test_skip_negative(self):
        """Test negative skip is rejected"""
        with pytest.raises(ValidationError):
            PaginationParams(skip=-1)

    def test_invalid_sort_field(self):
        """Test invalid sort field characters"""
        # Valid
        PaginationParams(sort_by="created_at")
        PaginationParams(sort_by="user_id")

        # Invalid characters
        with pytest.raises(ValidationError):
            PaginationParams(sort_by="name'; DROP TABLE")

    def test_invalid_order(self):
        """Test invalid order value"""
        # Valid
        PaginationParams(order="asc")
        PaginationParams(order="desc")

        # Invalid
        with pytest.raises(ValidationError):
            PaginationParams(order="invalid")
