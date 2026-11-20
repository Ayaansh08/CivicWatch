"""
Test that the OpenAPI schema has the correct title, version, and tag names.
Checks GET /openapi.json returns the expected metadata set in main.py.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.platform.database import Base, get_db

# In-memory SQLite for these tests
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Replace PostgreSQL session with SQLite session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Set up and tear down the in-memory database for each test."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_openapi_title_is_civicwatch_api():
    """GET /openapi.json should return the title 'CivicWatch API'."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "CivicWatch API"


def test_openapi_version_is_1_0_0():
    """GET /openapi.json should return version '1.0.0'."""
    response = client.get("/openapi.json")
    assert response.json()["info"]["version"] == "1.0.0"


def test_openapi_includes_expected_tag_names():
    """GET /openapi.json should include tag names for auth and admin at minimum."""
    response = client.get("/openapi.json")
    tags = {t["name"] for t in response.json().get("tags", [])}
    # These two tags are always required for Gaurav's work
    assert "auth" in tags
    assert "admin" in tags
