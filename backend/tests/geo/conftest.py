"""
Shared pytest fixtures for geo API tests.
Uses an in-memory SQLite database with dependency overrides.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.platform import models  # noqa: F401
from backend.app.platform.database import Base, get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User, Category, Complaint

# Shared in-memory SQLite engine for tests
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
    """Provide a test database session for each API request."""
    # Create new session for request
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Always close session after request
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create clean database tables before each test and drop them afterward."""
    # Create all tables in SQLite
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    # Clean up dependency overrides and drop tables
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create and return a citizen user for tests."""
    # Open db session
    db = TestingSessionLocal()
    user = User(
        name="Test Citizen",
        email="citizen@example.com",
        password_hash="hashed-pw",
        role="citizen",
    )
    # Save user to test db
    db.add(user)
    db.commit()
    db.refresh(user)
    db.expunge(user)
    db.close()
    return user


@pytest.fixture
def test_category():
    """Create and return a complaint category for tests."""
    # Open db session
    db = TestingSessionLocal()
    category = Category(name="Pothole")
    # Save category to test db
    db.add(category)
    db.commit()
    db.refresh(category)
    db.expunge(category)
    db.close()
    return category


@pytest.fixture
def second_category():
    """Create and return a second complaint category for tests."""
    # Open db session
    db = TestingSessionLocal()
    category = Category(name="Garbage")
    # Save category to test db
    db.add(category)
    db.commit()
    db.refresh(category)
    db.expunge(category)
    db.close()
    return category


@pytest.fixture
def officer_user():
    """Create and return an authority officer user for tests."""
    # Open db session
    db = TestingSessionLocal()
    user = User(
        name="Test Officer",
        email="officer@example.com",
        password_hash="hashed-pw",
        role="officer",
    )
    # Save officer to test db
    db.add(user)
    db.commit()
    db.refresh(user)
    db.expunge(user)
    db.close()
    return user


@pytest.fixture
def insert_complaint(test_user, test_category):
    """Helper function to insert a complaint at given latitude and longitude."""
    def _create(
        lat,
        lon,
        title="Test Complaint",
        category_id=None,
        status="Submitted",
        priority="Medium",
        created_at=None,
        updated_at=None,
    ):
        # Open db session to create complaint
        db = TestingSessionLocal()
        complaint = Complaint(
            title=title,
            description="Test Description",
            category_id=category_id or test_category.id,
            status=status,
            priority=priority,
            latitude=lat,
            longitude=lon,
            user_id=test_user.id,
        )
        if created_at is not None:
            complaint.created_at = created_at
        if updated_at is not None:
            complaint.updated_at = updated_at
        # Commit to test database
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        db.expunge(complaint)
        db.close()
        return complaint

    return _create


@pytest.fixture
def authenticated_client(test_user):
    """Return a TestClient authenticated as the test user."""
    # Override get_current_user to return test citizen
    app.dependency_overrides[get_current_user] = lambda: test_user
    return TestClient(app)


@pytest.fixture
def officer_client(officer_user):
    """Return a TestClient authenticated as the test officer."""
    # Override get_current_user to return test officer
    app.dependency_overrides[get_current_user] = lambda: officer_user
    return TestClient(app)


@pytest.fixture
def plain_client():
    """Return an unauthenticated TestClient."""
    # No authentication override
    return TestClient(app)
