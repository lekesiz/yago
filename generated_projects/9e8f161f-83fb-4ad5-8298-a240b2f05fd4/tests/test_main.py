# File: tests/test_main.py

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.main import app
from src.database import Base
from src.models import User
from src.schemas import UserCreate

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_user_happy_path(client, setup_database):
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    data = response.json()
    assert response.status_code == 200
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_create_user_duplicate_email(client, setup_database):
    # Setup initial user
    client.post("/users/", json={"email": "test@example.com", "password": "testpassword"})

    # Attempt to create another user with the same email
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "newpassword"}
    )
    assert response.status_code == 400

def test_create_user_invalid_email(client, setup_database):
    response = client.post(
        "/users/",
        json={"email": "invalid-email", "password": "testpassword"}
    )
    assert response.status_code == 422

def test_create_user_missing_email(client, setup_database):
    response = client.post(
        "/users/",
        json={"password": "testpassword"}
    )
    assert response.status_code == 422

def test_create_user_missing_password(client, setup_database):
    response = client.post(
        "/users/",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 422