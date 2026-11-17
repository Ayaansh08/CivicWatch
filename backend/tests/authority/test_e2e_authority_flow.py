"""
End-to-end acceptance test for the authority review-to-resolve flow (CW-310).

Uses in-memory SQLite with get_db and get_current_user overrides so no Docker
or PostgreSQL is needed.
"""
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
from backend.app.citizen.models import StatusHistory

# In-memory SQLite database for the e2e test
SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


def override_get_db():
    """Provide a test database session."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before the test, drop after."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def seed_data():
    """Seed an officer, citizen, category, department, and a Submitted complaint."""
    db = TestSessionLocal()
    officer = User(name="Officer", email="officer@test.com",
                   password_hash="h", role="officer")
    citizen = User(name="Citizen", email="citizen@test.com",
                   password_hash="h", role="citizen")
    cat = Category(name="Pothole")
    dept = Department(name="Roads Department")
    db.add_all([officer, citizen, cat, dept])
    db.commit()
    db.refresh(officer)
    db.refresh(citizen)
    db.refresh(cat)
    db.refresh(dept)
    complaint = Complaint(
        title="Big pothole on 5th Ave",
        category_id=cat.id,
        status="Submitted",
        priority="Medium",
        user_id=citizen.id,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    db.expunge_all()
    db.close()
    return {"officer": officer, "citizen": citizen, "cat": cat,
            "dept": dept, "complaint": complaint}


def _client_as(user):
    """Return a TestClient authenticated as the given user."""
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def test_full_happy_path_review_to_resolve(seed_data):
    """Walk a complaint from Submitted to Resolved and verify history."""
    d = seed_data
    client = _client_as(d["officer"])
    cid = d["complaint"].id

    # Step 1: Review (Submitted -> Under Review)
    r = client.post(f"/authority/complaints/{cid}/review")
    assert r.status_code == 200
    assert r.json()["status"] == "Under Review"

    # Step 2: Assign (Under Review -> Assigned)
    r = client.post(f"/authority/complaints/{cid}/assign", json={
        "department_id": d["dept"].id, "priority": "High",
    })
    assert r.status_code == 200
    assert r.json()["status"] == "Assigned"

    # Step 3: In Progress (Assigned -> In Progress)
    r = client.post(f"/authority/complaints/{cid}/status",
                    json={"status": "In Progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "In Progress"

    # Step 4: Resolve (In Progress -> Resolved)
    r = client.post(f"/authority/complaints/{cid}/status",
                    json={"status": "Resolved"})
    assert r.status_code == 200
    assert r.json()["status"] == "Resolved"

    # Verify history shows all transitions in order
    db = TestSessionLocal()
    history = (db.query(StatusHistory)
               .filter(StatusHistory.complaint_id == cid)
               .order_by(StatusHistory.changed_at)
               .all())
    statuses = [h.status for h in history]
    db.close()
    assert statuses == ["Under Review", "Assigned", "In Progress", "Resolved"]


def test_direct_submitted_to_resolved_returns_400(seed_data):
    """Skipping steps: Submitted cannot jump to Resolved."""
    d = seed_data
    client = _client_as(d["officer"])
    cid = d["complaint"].id
    r = client.post(f"/authority/complaints/{cid}/status",
                    json={"status": "Resolved"})
    assert r.status_code == 400


def test_citizen_gets_403_on_every_authority_endpoint(seed_data):
    """A citizen user gets 403 on all authority endpoints."""
    d = seed_data
    client = _client_as(d["citizen"])
    cid = d["complaint"].id
    # Each authority endpoint should reject the citizen
    assert client.get("/authority/complaints").status_code == 403
    assert client.post(f"/authority/complaints/{cid}/review").status_code == 403
    assert client.post(f"/authority/complaints/{cid}/assign",
                       json={"department_id": 1, "priority": "High"}).status_code == 403
    assert client.post(f"/authority/complaints/{cid}/status",
                       json={"status": "Under Review"}).status_code == 403
    assert client.post("/authority/escalate").status_code == 403
