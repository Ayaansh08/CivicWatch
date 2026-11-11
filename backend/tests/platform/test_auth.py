"""
Tests for the authentication endpoints: /auth/register, /auth/login, /auth/me.

These tests use an in-memory SQLite database via a get_db override,
so Docker is NOT needed to run them.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.platform import models  # noqa: F401
from backend.app.platform.database import Base, get_db

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
    # Tell FastAPI to use our test database instead of the real one
    app.dependency_overrides[get_db] = override_get_db
    yield
    # Clean up the dependency override and drop all tables so each test starts clean
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_register_creates_a_citizen_user():
    """Registering with valid data should return 201 and create a citizen user."""
    # Send a valid registration payload
    response = client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret123",
    })
    # Verify HTTP 201 and citizen role
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "citizen"


def test_register_never_returns_the_password():
    """The register response must not include the password or password_hash."""
    # Register a new user
    response = client.post("/auth/register", json={
        "name": "Bob",
        "email": "bob@example.com",
        "password": "secret123",
    })
    # Verify neither password nor password_hash appears in the response
    data = response.json()
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email_returns_400():
    """Registering the same email twice should return 400 Bad Request."""
    # Register the email once, then attempt a second registration with the same email
    payload = {"name": "Carol", "email": "carol@example.com", "password": "secret123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    # Verify the duplicate registration is rejected with 400
    assert response.status_code == 400


def test_register_short_password_returns_422():
    """A password shorter than 6 characters should return 422 Unprocessable Entity."""
    # Send a registration request with a 3-character password
    response = client.post("/auth/register", json={
        "name": "Dave",
        "email": "dave@example.com",
        "password": "abc",
    })
    # Verify Pydantic validation rejects it with 422
    assert response.status_code == 422


def test_login_with_correct_credentials_returns_access_token():
    """Logging in with the right email and password should return an access_token."""
    # Register a user first, then log in with the same credentials
    client.post("/auth/register", json={
        "name": "Eve",
        "email": "eve@example.com",
        "password": "secret123",
    })
    response = client.post("/auth/login", json={
        "email": "eve@example.com",
        "password": "secret123",
    })
    # Verify HTTP 200 and presence of access_token
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_returns_401():
    """Logging in with the wrong password should return 401 Unauthorized."""
    # Register a user, then attempt login with a bad password
    client.post("/auth/register", json={
        "name": "Frank",
        "email": "frank@example.com",
        "password": "secret123",
    })
    response = client.post("/auth/login", json={
        "email": "frank@example.com",
        "password": "wrongpassword",
    })
    # Verify login fails with 401
    assert response.status_code == 401


def test_login_with_unknown_email_returns_401():
    """Logging in with an email that was never registered should return 401."""
    # Attempt login for a user that does not exist
    response = client.post("/auth/login", json={
        "email": "ghost@example.com",
        "password": "secret123",
    })
    # Verify login fails with 401
    assert response.status_code == 401


def test_get_me_with_valid_token_returns_user():
    """GET /auth/me with a valid Bearer token should return the logged-in user."""
    # Register and log in to obtain a JWT token
    client.post("/auth/register", json={
        "name": "Grace",
        "email": "grace@example.com",
        "password": "secret123",
    })
    login_response = client.post("/auth/login", json={
        "email": "grace@example.com",
        "password": "secret123",
    })
    token = login_response.json()["access_token"]
    # Request the current user profile with the Bearer token
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    # Verify HTTP 200 and matching email
    assert response.status_code == 200
    assert response.json()["email"] == "grace@example.com"


def test_get_me_without_token_returns_401():
    """GET /auth/me without an Authorization header should return 401."""
    # Call /auth/me without credentials
    response = client.get("/auth/me")
    # Verify access is denied with 401
    assert response.status_code == 401
