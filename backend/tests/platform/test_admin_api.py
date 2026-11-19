"""
Tests for the admin management endpoints (/admin/departments, /admin/officers,
/admin/users/{id}/role) and the create_admin_user helper.

Uses an in-memory SQLite database via a get_db override so Docker is not needed.
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
from backend.app.platform.models import Category, Complaint, Department, User
from backend.app.platform.security import hash_password

# Use an in-memory SQLite database with StaticPool so tables persist across requests
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
    """Replace the real PostgreSQL session with an in-memory SQLite session."""
    # Open a session against the shared in-memory SQLite database
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Close the session after the request completes
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create tables before each test and clean up overrides and tables afterward."""
    # Create all tables in the in-memory SQLite database
    Base.metadata.create_all(bind=engine)
    # Point FastAPI's get_db dependency to our test SQLite database
    app.dependency_overrides[get_db] = override_get_db
    yield
    # Remove overrides and drop all tables so each test starts clean
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a direct SQLAlchemy session for creating test records."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_user(db_session):
    """Create and save an admin user in the test database."""
    user = User(
        name="Admin One",
        email="admin@civicwatch.com",
        password_hash=hash_password("admin123"),
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def officer_user(db_session):
    """Create and save an officer user in the test database."""
    user = User(
        name="Officer One",
        email="officer@civicwatch.com",
        password_hash=hash_password("officer123"),
        role="officer",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def citizen_user(db_session):
    """Create and save a citizen user in the test database."""
    user = User(
        name="Citizen One",
        email="citizen@civicwatch.com",
        password_hash=hash_password("citizen123"),
        role="citizen",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def act_as(user: User):
    """Override get_current_user so requests run as the chosen user."""
    app.dependency_overrides[get_current_user] = lambda: user


client = TestClient(app)


# --- Department management tests ---


def test_admin_creates_a_department_and_gets_201(admin_user):
    """An admin creating a valid department should get HTTP 201 and the new record."""
    act_as(admin_user)
    response = client.post("/admin/departments", json={"name": "Water Department"})
    assert response.status_code == 201
    assert response.json()["name"] == "Water Department"


def test_creating_duplicate_department_name_returns_400(admin_user):
    """Creating a department with a name that already exists should return 400."""
    act_as(admin_user)
    client.post("/admin/departments", json={"name": "Roads Department"})
    response = client.post("/admin/departments", json={"name": "Roads Department"})
    assert response.status_code == 400


def test_department_name_shorter_than_3_characters_returns_422(admin_user):
    """Creating a department with a name shorter than 3 characters should return 422."""
    act_as(admin_user)
    response = client.post("/admin/departments", json={"name": "PW"})
    assert response.status_code == 422


def test_get_departments_lists_all_departments(admin_user):
    """GET /admin/departments should return a paginated dict with every department."""
    act_as(admin_user)
    client.post("/admin/departments", json={"name": "Water Department"})
    client.post("/admin/departments", json={"name": "Sanitation"})
    response = client.get("/admin/departments")
    assert response.status_code == 200
    # Response is now paginated: {"items": [...], "total": n, "page": 1, "size": 20, "pages": 1}
    data = response.json()
    names = [dept["name"] for dept in data["items"]]
    assert "Water Department" in names
    assert "Sanitation" in names


def test_put_department_renames_existing_department(admin_user):
    """PUT /admin/departments/{id} should update the department's name."""
    act_as(admin_user)
    created = client.post("/admin/departments", json={"name": "Water Dept"}).json()
    response = client.put(
        f"/admin/departments/{created['id']}",
        json={"name": "Water Supply Department"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Water Supply Department"


def test_put_department_with_missing_id_returns_404(admin_user):
    """PUT /admin/departments/{id} for a nonexistent id should return 404."""
    act_as(admin_user)
    response = client.put("/admin/departments/9999", json={"name": "Lighting"})
    assert response.status_code == 404


def test_delete_unused_department_returns_204(admin_user):
    """DELETE /admin/departments/{id} should remove an unused department with 204."""
    act_as(admin_user)
    created = client.post("/admin/departments", json={"name": "Parks Dept"}).json()
    response = client.delete(f"/admin/departments/{created['id']}")
    assert response.status_code == 204


def test_delete_department_with_assigned_complaints_returns_400(
    admin_user, citizen_user, db_session
):
    """Deleting a department that has complaints assigned should return 400."""
    # Create a department, category, and complaint linked to that department
    department = Department(name="Drainage Department")
    category = Category(name="Drainage")
    db_session.add(department)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(department)
    db_session.refresh(category)

    complaint = Complaint(
        title="Blocked drain",
        description="Water logging near gate",
        category_id=category.id,
        user_id=citizen_user.id,
        department_id=department.id,
    )
    db_session.add(complaint)
    db_session.commit()

    # Attempt to delete the in-use department as admin
    act_as(admin_user)
    response = client.delete(f"/admin/departments/{department.id}")
    assert response.status_code == 400
    assert "complaint" in response.json()["detail"].lower()


# --- Officer and user role management tests ---


def test_admin_creates_an_officer_and_hides_password(admin_user):
    """POST /admin/officers should return 201, role 'officer', and no password."""
    act_as(admin_user)
    response = client.post(
        "/admin/officers",
        json={
            "name": "New Officer",
            "email": "newofficer@civicwatch.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "officer"
    assert "password" not in data
    assert "password_hash" not in data


def test_creating_duplicate_officer_email_returns_400(admin_user, officer_user):
    """Creating an officer with an already-registered email should return 400."""
    act_as(admin_user)
    response = client.post(
        "/admin/officers",
        json={
            "name": "Duplicate Officer",
            "email": officer_user.email,
            "password": "password123",
        },
    )
    assert response.status_code == 400


def test_officer_password_under_6_characters_returns_422(admin_user):
    """Creating an officer with a password shorter than 6 characters should return 422."""
    act_as(admin_user)
    response = client.post(
        "/admin/officers",
        json={
            "name": "Short Pass",
            "email": "short@civicwatch.com",
            "password": "123",
        },
    )
    assert response.status_code == 422


def test_get_officers_returns_only_users_with_officer_role(
    admin_user, officer_user, citizen_user
):
    """GET /admin/officers should return a paginated dict with only officers."""
    act_as(admin_user)
    response = client.get("/admin/officers")
    assert response.status_code == 200
    # Response is now paginated: {"items": [...], "total": n, ...}
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["email"] == officer_user.email
    assert data["items"][0]["role"] == "officer"


def test_patch_user_role_changes_role(admin_user, citizen_user):
    """PATCH /admin/users/{id}/role should update the target user's role."""
    act_as(admin_user)
    response = client.patch(
        f"/admin/users/{citizen_user.id}/role",
        json={"role": "officer"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "officer"


def test_patch_user_role_with_invalid_role_returns_422(admin_user, citizen_user):
    """PATCH /admin/users/{id}/role with an invalid role value should return 422."""
    act_as(admin_user)
    response = client.patch(
        f"/admin/users/{citizen_user.id}/role",
        json={"role": "superhero"},
    )
    assert response.status_code == 422


def test_admin_cannot_change_their_own_role(admin_user):
    """An admin attempting to change their own role should get HTTP 400."""
    act_as(admin_user)
    response = client.patch(
        f"/admin/users/{admin_user.id}/role",
        json={"role": "citizen"},
    )
    assert response.status_code == 400


# --- Access control tests for /admin ---


def test_citizen_calling_admin_endpoint_gets_403(citizen_user):
    """A citizen calling any /admin endpoint should be rejected with 403."""
    act_as(citizen_user)
    response = client.get("/admin/departments")
    assert response.status_code == 403


def test_officer_calling_admin_endpoint_gets_403(officer_user):
    """An officer calling any /admin endpoint should be rejected with 403."""
    act_as(officer_user)
    response = client.get("/admin/officers")
    assert response.status_code == 403


def test_request_with_no_token_to_admin_endpoint_gets_401():
    """Calling an /admin endpoint without a Bearer token should return 401."""
    # Ensure get_current_user is not overridden so real JWT checking runs
    app.dependency_overrides.pop(get_current_user, None)
    response = client.get("/admin/departments")
    assert response.status_code == 401


# --- create_admin_user helper tests ---


def test_create_admin_user_creates_admin_with_hashed_password(db_session):
    """create_admin_user should save a user with role 'admin' and a hashed password."""
    from backend.app.platform.create_admin import create_admin_user

    user = create_admin_user(
        db_session,
        name="Root Admin",
        email="root@civicwatch.com",
        password="secret123",
    )
    assert user.role == "admin"
    assert user.email == "root@civicwatch.com"
    assert user.password_hash != "secret123"


def test_create_admin_user_returns_existing_user_for_duplicate_email(db_session):
    """Calling create_admin_user twice with the same email should not create a duplicate."""
    from backend.app.platform.create_admin import create_admin_user

    first = create_admin_user(
        db_session,
        name="Root Admin",
        email="root@civicwatch.com",
        password="secret123",
    )
    second = create_admin_user(
        db_session,
        name="Root Admin Again",
        email="root@civicwatch.com",
        password="otherpassword",
    )
    assert second.id == first.id
    assert db_session.query(User).filter(User.email == "root@civicwatch.com").count() == 1
