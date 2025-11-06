"""
YAGO v8.4 - Integration Tests
End-to-end tests for API endpoints with database
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from database import Base, get_db


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_integration.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Create test client"""
    # Create test database tables
    Base.metadata.create_all(bind=engine)

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Drop test database tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def test_user(client):
    """Create a test user"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "integration@test.com",
            "password": "TestPass123!",
            "full_name": "Integration Test User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    return {
        "user": data["user"],
        "token": data["access_token"],
    }


class TestHealthEndpoints:
    """Test health and system endpoints"""

    def test_root_endpoint(self, client):
        """Test API root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "version" in data

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestAuthenticationFlow:
    """Test complete authentication flow"""

    def test_user_registration(self, client):
        """Test user can register"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "SecurePass123!",
                "full_name": "New User",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@test.com"

    def test_user_login(self, client, test_user):
        """Test user can login"""
        response = client.post(
            "/api/v1/auth/login-json",
            json={
                "email": "integration@test.com",
                "password": "TestPass123!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_get_current_user(self, client, test_user):
        """Test getting current user info"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "integration@test.com"

    def test_invalid_login(self, client):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login-json",
            json={
                "email": "nonexistent@test.com",
                "password": "WrongPass123!",
            },
        )
        assert response.status_code == 401


class TestProjectWorkflow:
    """Test complete project workflow"""

    def test_create_project(self, client, test_user):
        """Test creating a new project"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.post(
            "/api/v1/projects",
            json={
                "brief": {
                    "project_idea": "Test project for integration testing",
                    "features": ["Feature 1", "Feature 2"],
                },
                "config": {
                    "primary_model": "gpt-4",
                    "strategy": "balanced",
                },
            },
            headers=headers,
        )
        # May fail if user authentication is required - adjust test accordingly
        assert response.status_code in [200, 201]
        data = response.json()
        assert "project_id" in data

    def test_list_projects_with_pagination(self, client):
        """Test listing projects with pagination"""
        response = client.get("/api/v1/projects?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 10

    def test_list_projects_with_filters(self, client):
        """Test listing projects with status filter"""
        response = client.get("/api/v1/projects?status=creating&page=1")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "pagination" in data

    def test_get_project_by_id(self, client, test_user):
        """Test getting a specific project"""
        # First create a project
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        create_response = client.post(
            "/api/v1/projects",
            json={
                "brief": {"project_idea": "Test project"},
                "config": {"primary_model": "gpt-4"},
            },
            headers=headers,
        )

        if create_response.status_code in [200, 201]:
            project_id = create_response.json()["project_id"]

            # Get the project
            get_response = client.get(f"/api/v1/projects/{project_id}")
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["id"] == project_id


class TestTemplatesWorkflow:
    """Test template marketplace workflow"""

    def test_list_templates_with_pagination(self, client):
        """Test listing templates with pagination"""
        response = client.get("/api/v1/user-templates?page=1&page_size=20")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "pagination" in data

    def test_submit_template(self, client, test_user):
        """Test submitting a new template"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.post(
            "/api/v1/user-templates/submit",
            json={
                "name": "Test Template",
                "description": "A template for integration testing purposes",
                "category": "web",
                "difficulty": "beginner",
                "icon": "🧪",
                "tags": ["test", "integration"],
                "estimated_time": "1 hour",
                "estimated_cost": 1.0,
                "template_data": {"framework": "fastapi"},
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "template" in data

    def test_get_my_templates(self, client, test_user):
        """Test getting user's own templates"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.get("/api/v1/user-templates/my?page=1", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "pagination" in data


class TestErrorLogging:
    """Test error logging workflow"""

    def test_log_error(self, client):
        """Test logging an error"""
        response = client.post(
            "/api/v1/errors/log",
            json={
                "error_type": "TypeError",
                "error_message": "Test error for integration testing",
                "source": "backend",
                "severity": "error",
                "environment": "test",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "error_id" in data

    def test_list_errors_with_pagination(self, client):
        """Test listing errors with pagination"""
        response = client.get("/api/v1/errors?page=1&page_size=50")
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert "pagination" in data

    def test_get_error_stats(self, client):
        """Test getting error statistics"""
        response = client.get("/api/v1/errors/stats?hours=24")
        assert response.status_code == 200
        data = response.json()
        # Stats endpoint should return statistics
        assert isinstance(data, dict)


class TestAnalytics:
    """Test analytics endpoints"""

    def test_get_analytics(self, client):
        """Test getting comprehensive analytics"""
        response = client.get("/api/v1/analytics?time_range=7d")
        assert response.status_code == 200
        data = response.json()
        assert "overview" in data
        assert "ai_usage" in data
        assert "timeline" in data

    def test_providers_status(self, client):
        """Test checking AI providers status"""
        response = client.get("/api/v1/providers/status")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "total_providers" in data


class TestPaginationConsistency:
    """Test pagination consistency across endpoints"""

    def test_pagination_metadata_structure(self, client):
        """Test that all paginated endpoints return consistent metadata"""
        endpoints = [
            "/api/v1/projects?page=1&page_size=10",
            "/api/v1/user-templates?page=1&page_size=10",
            "/api/v1/errors?page=1&page_size=10",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Failed for {endpoint}"

            data = response.json()
            assert "pagination" in data, f"No pagination in {endpoint}"

            pagination = data["pagination"]
            # Check all required pagination fields
            assert "total" in pagination
            assert "page" in pagination
            assert "page_size" in pagination
            assert "total_pages" in pagination
            assert "has_next" in pagination
            assert "has_prev" in pagination

            # Verify values
            assert pagination["page"] == 1
            assert pagination["page_size"] == 10


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
