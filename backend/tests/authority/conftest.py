"""Shared fixtures for authority API tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.platform import models as platform_models  # noqa: F401
from backend.app.citizen import models as citizen_models  # noqa: F401
from backend.app.platform.database import Base, get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User, Category, Department, Complaint

# In-memory SQLite for fast, isolated tests
SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Provide a SQLite session for each test request."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create all tables before each test, tear them down after."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a direct database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def officer_user():
    """Create and return an officer user."""
    db = TestingSessionLocal()
    user = User(name="Officer Ali", email="officer@example.com",
                password_hash="hash", role="officer")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.expunge(user)
    db.close()
    return user


@pytest.fixture
def citizen_user():
    """Create and return a plain citizen user."""
    db = TestingSessionLocal()
    user = User(name="Citizen Bob", email="citizen@example.com",
                password_hash="hash", role="citizen")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.expunge(user)
    db.close()
    return user


@pytest.fixture
def test_category():
    """Create and return a complaint category."""
    db = TestingSessionLocal()
    cat = Category(name="Pothole")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    db.expunge(cat)
    db.close()
    return cat


@pytest.fixture
def test_department():
    """Create and return a department."""
    db = TestingSessionLocal()
    dept = Department(name="Roads Department")
    db.add(dept)
    db.commit()
    db.refresh(dept)
    db.expunge(dept)
    db.close()
    return dept


@pytest.fixture
def submitted_complaint(officer_user, test_category):
    """Create a Submitted complaint owned by the officer user."""
    db = TestingSessionLocal()
    complaint = Complaint(
        title="Broken road",
        category_id=test_category.id,
        status="Submitted",
        priority="Medium",
        user_id=officer_user.id,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    db.expunge(complaint)
    db.close()
    return complaint


@pytest.fixture
def officer_client(officer_user):
    """Return a TestClient authenticated as an officer."""
    app.dependency_overrides[get_current_user] = lambda: officer_user
    return TestClient(app)


@pytest.fixture
def citizen_client(citizen_user):
    """Return a TestClient authenticated as a citizen."""
    app.dependency_overrides[get_current_user] = lambda: citizen_user
    return TestClient(app)


@pytest.fixture
def plain_client():
    """Return a TestClient with no authentication."""
    return TestClient(app)


@pytest.fixture
def under_review_complaint(officer_client, submitted_complaint):
    """Return a complaint already moved to Under Review (used by assign tests)."""
    from backend.app.platform.models import Complaint as ComplaintModel
    # Drive the complaint through the review endpoint
    officer_client.post(f"/authority/complaints/{submitted_complaint.id}/review")
    # Reload from DB to get the updated status
    db = TestingSessionLocal()
    c = db.query(ComplaintModel).filter(ComplaintModel.id == submitted_complaint.id).first()
    db.expunge(c)
    db.close()
    return c
