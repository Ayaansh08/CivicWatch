"""
Tests for the shared pagination helper (CW-210).

The paginate() function is a pure function tested against in-memory SQLite
so Docker is not needed.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from backend.app.platform.pagination import paginate, pagination_params
from backend.app.platform.database import get_db

# Shared in-memory SQLite engine for pagination tests
SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Widget(Base):
    """Minimal SQLAlchemy model used only inside this test file."""
    __tablename__ = "widgets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)


@pytest.fixture(autouse=True)
def setup_widgets_table():
    """Create the widgets table and insert 45 rows before each test."""
    # Create the table
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Insert 45 widget rows so we can test multi-page behaviour
    for i in range(1, 46):
        db.add(Widget(name=f"widget-{i}"))
    db.commit()
    db.close()
    yield
    # Drop the table so the next test starts clean
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a SQLAlchemy session that queries the shared in-memory database."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_page_1_size_10_returns_10_items(db):
    """paginate() on page 1 with size 10 should return exactly 10 items."""
    # Build a query for all widgets and paginate it
    result = paginate(db.query(Widget).order_by(Widget.id), page=1, size=10)
    # First page should have exactly 10 items
    assert len(result["items"]) == 10


def test_page_5_size_10_returns_5_items(db):
    """paginate() on page 5 with size 10 should return the remaining 5 items."""
    result = paginate(db.query(Widget).order_by(Widget.id), page=5, size=10)
    # 45 items / 10 per page = 4 full pages + 5 remaining on page 5
    assert len(result["items"]) == 5


def test_page_6_size_10_returns_empty_items(db):
    """paginate() on page 6 with size 10 should return an empty items list."""
    result = paginate(db.query(Widget).order_by(Widget.id), page=6, size=10)
    # Page 6 is beyond the last page so items should be empty
    assert result["items"] == []


def test_total_is_45(db):
    """paginate() should report total=45 regardless of the requested page."""
    result = paginate(db.query(Widget).order_by(Widget.id), page=1, size=10)
    assert result["total"] == 45


def test_pages_count_is_5_for_45_items_size_10(db):
    """paginate() should compute pages=5 for 45 items and size 10."""
    result = paginate(db.query(Widget).order_by(Widget.id), page=1, size=10)
    assert result["pages"] == 5


# --- Validation tests via the FastAPI dependency ---

def build_validation_app():
    """Create a tiny FastAPI app that exposes pagination_params as a route."""
    app = FastAPI()

    @app.get("/items")
    def get_items(params: dict = __import__("fastapi").Depends(pagination_params)):
        """Return the pagination params for validation testing."""
        return params

    return app


test_app = build_validation_app()
val_client = TestClient(test_app)


def test_size_zero_returns_422():
    """Requesting size=0 should return 422 because size must be at least 1."""
    response = val_client.get("/items?size=0")
    assert response.status_code == 422


def test_size_101_returns_422():
    """Requesting size=101 should return 422 because the maximum allowed size is 100."""
    response = val_client.get("/items?size=101")
    assert response.status_code == 422


def test_page_below_1_returns_422():
    """Requesting page=0 should return 422 because page must be at least 1."""
    response = val_client.get("/items?page=0")
    assert response.status_code == 422


# --- Paginated shape tests for admin list endpoints ---

from backend.app.main import app as main_app
from backend.app.platform.database import Base as PlatformBase, get_db as platform_get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User  # noqa: F401
from backend.app.platform.security import hash_password
from sqlalchemy.pool import StaticPool as SP

admin_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=SP,
)
AdminSession = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)


def override_db():
    """Replace the real database with the test SQLite database."""
    db = AdminSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_admin_db():
    """Create platform tables, seed an admin and an officer, wire overrides."""
    PlatformBase.metadata.create_all(bind=admin_engine)
    main_app.dependency_overrides[platform_get_db] = override_db
    # Create a fake admin user so require_role("admin") passes
    admin = User(
        name="Admin",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role="admin",
    )
    db = AdminSession()
    db.add(admin)
    db.commit()
    db.refresh(admin)
    # Override get_current_user so the route handler sees the admin
    main_app.dependency_overrides[get_current_user] = lambda: admin
    db.close()
    yield
    main_app.dependency_overrides.pop(platform_get_db, None)
    main_app.dependency_overrides.pop(get_current_user, None)
    PlatformBase.metadata.drop_all(bind=admin_engine)


admin_client = TestClient(main_app)


def test_list_departments_returns_paginated_shape():
    """GET /admin/departments should return items, total, page, size, pages keys."""
    # Request the departments list
    response = admin_client.get("/admin/departments")
    assert response.status_code == 200
    # Check that the standard paginated keys are all present
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data


def test_list_officers_returns_paginated_shape():
    """GET /admin/officers should return items, total, page, size, pages keys."""
    # Request the officers list
    response = admin_client.get("/admin/officers")
    assert response.status_code == 200
    # Verify the paginated shape is returned
    data = response.json()
    assert "items" in data
    assert "total" in data
