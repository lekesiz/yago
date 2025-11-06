"""
Tests for API endpoints
"""
import pytest
from fastapi import status


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_register_user(self, client):
        """Test user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "StrongPass123!",
                "full_name": "New User"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "Password123!",
                "full_name": "Duplicate User"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,  # OAuth2 uses 'username' field
                "password": "testpassword123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client, auth_headers):
        """Test get current user endpoint"""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert "id" in data

    def test_get_current_user_no_token(self, client):
        """Test get current user without token"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProjectEndpoints:
    """Test project management endpoints"""

    def test_create_project(self, client, auth_headers):
        """Test project creation"""
        response = client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={
                "name": "New Project",
                "description": "A new test project",
                "primary_model": "gpt-4"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Project"
        assert "id" in data

    def test_list_projects(self, client, auth_headers, test_project):
        """Test listing projects"""
        response = client.get(
            "/api/v1/projects",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_get_project(self, client, auth_headers, test_project):
        """Test getting single project"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_project.id

    def test_get_nonexistent_project(self, client, auth_headers):
        """Test getting non-existent project"""
        response = client.get(
            "/api/v1/projects/nonexistent-id",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project(self, client, auth_headers, test_project):
        """Test project deletion"""
        response = client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify project is deleted
        get_response = client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestClarificationEndpoints:
    """Test clarification flow endpoints"""

    def test_start_clarification(self, client):
        """Test starting clarification session"""
        response = client.post(
            "/api/v1/clarifications",
            json={
                "project_idea": "Build a task management application with user authentication",
                "depth": "standard"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "session_id" in data
        assert "current_question" in data

    def test_get_clarification_session(self, client, db_session):
        """Test getting clarification session"""
        # First create a session
        create_response = client.post(
            "/api/v1/clarifications",
            json={
                "project_idea": "Test project",
                "depth": "minimal"
            }
        )
        session_id = create_response.json()["session_id"]

        # Then get it
        response = client.get(f"/api/v1/clarifications/{session_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == session_id
