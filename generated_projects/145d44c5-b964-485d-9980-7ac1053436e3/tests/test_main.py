# tests/test_main.py

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base_class import Base
from app.core.config import settings
import pytest

# Test configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the test DB
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

# Happy path test
def test_read_main(client):
    response = client.get(f"{settings.API_V1_STR}/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

# Edge case test
def test_read_main_with_unexpected_path(client):
    response = client.get(f"{settings.API_V1_STR}/unexpected_path")
    assert response.status_code == 404

# Error handling test
def test_error_handling(client):
    # Assuming there's an endpoint that might raise an HTTPException
    response = client.get(f"{settings.API_V1_STR}/error_endpoint")
    assert response.status_code == 400
    assert "detail" in response.json()