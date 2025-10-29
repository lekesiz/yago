"""
YAGO v8.1 - E2E Test Configuration
Pytest fixtures and setup for end-to-end testing
"""

import pytest
import asyncio
import os
import sys
import shutil
from pathlib import Path
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from httpx import AsyncClient, ASGITransport
import tempfile

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "yago" / "web" / "backend"))

from yago.web.backend.main import app
from yago.web.backend.database import Base, get_db
from yago.web.backend import models


# Test database configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_yago.db")
TEST_GENERATED_PROJECTS_DIR = Path("./test_generated_projects")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
        echo=False
    )

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    yield test_engine

    # Cleanup: Drop all tables
    Base.metadata.drop_all(bind=test_engine)

    # Remove SQLite database file if exists
    if "sqlite" in TEST_DATABASE_URL:
        db_file = TEST_DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_file):
            os.remove(db_file)


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """
    Create a new database session for each test.
    Automatically rolls back after test completion.
    """
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """
    Create HTTP client with test database session.
    Tests will hit real API endpoints at localhost:8000
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Use real server instead of ASGI transport for true E2E testing
    async with AsyncClient(base_url="http://localhost:8000", timeout=60.0) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_project_data():
    """Sample project data for testing"""
    return {
        "name": "E2E Test Project",
        "description": "A test project for end-to-end testing",
        "brief": {
            "project_idea": "Simple REST API for task management",
            "key_features": ["CRUD operations", "User authentication"],
            "tech_stack": "FastAPI, PostgreSQL",
            "target_audience": "Developers",
            "constraints": "Must be RESTful",
            "success_criteria": "100% test coverage"
        },
        "config": {
            "primary_model": "gpt-4-turbo-preview",
            "agent_role": "senior_developer",
            "strategy": "balanced",
            "temperature": 0.7,
            "max_tokens": 4000
        }
    }


@pytest.fixture(scope="function")
def test_clarification_data():
    """Sample clarification session data"""
    return {
        "project_idea": "E-commerce platform with product catalog",
        "depth": "standard",
        "provider": "openai"
    }


@pytest.fixture(scope="function")
def cleanup_generated_projects():
    """Cleanup generated test projects"""
    yield

    # Cleanup after test
    if TEST_GENERATED_PROJECTS_DIR.exists():
        shutil.rmtree(TEST_GENERATED_PROJECTS_DIR)


@pytest.fixture(scope="function")
def mock_ai_responses():
    """Mock AI provider responses for faster testing"""
    return {
        "architecture": """
        # System Architecture

        ## Technology Stack
        - Backend: FastAPI
        - Database: PostgreSQL
        - Authentication: JWT

        ## Components
        1. API Layer
        2. Business Logic
        3. Data Layer
        """,
        "main_file": """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
""",
        "tests": """
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
"""
    }


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("GENERATED_PROJECTS_DIR", str(TEST_GENERATED_PROJECTS_DIR))
    monkeypatch.setenv("TESTING", "true")


# Markers for test categorization
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "requires_api: marks tests that require API to be running")
    config.addinivalue_line("markers", "requires_ai: marks tests that require AI provider keys")


# Helper functions for tests
def create_test_project(db_session: Session, **kwargs) -> models.Project:
    """Helper to create a test project in database"""
    project_data = {
        "name": "Test Project",
        "description": "Test Description",
        "status": "creating",
        "progress": 0,
        "brief": {"project_idea": "Test idea"},
        "config": {"primary_model": "gpt-4-turbo-preview"},
    }
    project_data.update(kwargs)

    project = models.Project(**project_data)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    return project


def create_test_clarification_session(db_session: Session, project_id: str, **kwargs) -> models.ClarificationSession:
    """Helper to create a test clarification session"""
    session_data = {
        "project_id": project_id,
        "project_idea": "Test idea",
        "depth": "standard",
        "questions": [{"id": 0, "question": "Test question?"}],
        "answers": {},
        "total_questions": 1,
        "ai_provider": "openai"
    }
    session_data.update(kwargs)

    session = models.ClarificationSession(**session_data)
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    return session


# Make helpers available to tests
@pytest.fixture
def db_helpers():
    """Database helper functions"""
    return {
        "create_project": create_test_project,
        "create_clarification": create_test_clarification_session,
    }
