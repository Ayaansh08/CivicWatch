"""Shared fixtures for citizen complaint API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.platform import models  # noqa: F401
from backend.app.platform.database import Base, get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User, Category

# Use one shared in-memory SQLite database for API tests.
SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    """Provide a database session for each API request."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create clean database tables before each test."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create and return a citizen user for tests."""
    db = TestingSessionLocal()
    user = User(
        name="Test Citizen",
        email="citizen@example.com",
        password_hash="test-hash",
        role="citizen",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.expunge(user)
    db.close()
    return user


@pytest.fixture
def test_category():
    """Create and return a complaint category for tests."""
    db = TestingSessionLocal()
    category = Category(name="Pothole")
    db.add(category)
    db.commit()
    db.refresh(category)
    db.expunge(category)
    db.close()
    return category


@pytest.fixture
def other_user():
    """Create and return a second citizen user for tests."""
    db = TestingSessionLocal()
    user = User(
        name="Other Citizen",
        email="other@example.com",
        password_hash="test-hash-2",
        role="citizen",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.expunge(user)
    db.close()
    return user


@pytest.fixture
def other_authenticated_client(other_user):
    """Return a client that acts as the second citizen."""
    def client_factory():
        app.dependency_overrides[get_current_user] = lambda: other_user
        return TestClient(app)
    return client_factory


@pytest.fixture
def authenticated_client(test_user):
    """Return a client that acts as the test citizen."""
    app.dependency_overrides[get_current_user] = lambda: test_user
    return TestClient(app)


@pytest.fixture
def plain_client():
    """Return a client without an authentication override."""
    return TestClient(app)
