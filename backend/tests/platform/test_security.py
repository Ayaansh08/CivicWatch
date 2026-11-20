"""
Tests for security hardening features (CW-211):
- Password length enforcement (6–72 chars)
- Name validation (not only spaces, 2–60 chars)
- Mixed-case email login
- Rate limiting on /auth/login (5 failures → 429)
- Security headers on /health
- CORS origin checking
- Production config safety check

Uses an in-memory SQLite database via a get_db override.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.platform import models  # noqa: F401
from backend.app.platform.database import Base, get_db

# In-memory SQLite database for these tests
SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Replace the real PostgreSQL session with an in-memory SQLite session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create tables before each test and clean up afterward."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# --- Password length validation ---

def test_password_of_73_characters_returns_422():
    """Registering with a 73-character password should return 422 (bcrypt limit is 72)."""
    # Create a password that is 1 character over the bcrypt limit
    long_password = "a" * 73
    response = client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": long_password,
    })
    # Pydantic should reject it with 422 before it reaches bcrypt
    assert response.status_code == 422


# --- Name validation ---

def test_spaces_only_name_returns_422():
    """Registering with a name that is only whitespace should return 422."""
    response = client.post("/auth/register", json={
        "name": "   ",
        "email": "spacename@example.com",
        "password": "valid123",
    })
    # Name validation strips the spaces so it fails the minimum length check
    assert response.status_code == 422


# --- Email case-insensitive login ---

def test_mixed_case_email_logs_in_successfully():
    """Logging in with a differently-cased version of the registration email should succeed."""
    # Register with a lower-case email
    client.post("/auth/register", json={
        "name": "Eve",
        "email": "eve@example.com",
        "password": "secret123",
    })
    # Attempt login with mixed-case email
    response = client.post("/auth/login", json={
        "email": "EVE@EXAMPLE.COM",
        "password": "secret123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


# --- Rate limiting ---

def test_five_failed_logins_return_429_on_the_sixth():
    """After 5 failed logins, the 6th attempt for the same key should return 429."""
    # Attempt 5 failing logins
    for _ in range(5):
        client.post("/auth/login", json={
            "email": "ghost@example.com",
            "password": "wrongpassword",
        })
    # The 6th attempt should be rate-limited
    response = client.post("/auth/login", json={
        "email": "ghost@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 429
    assert "Too many failed login attempts" in response.json()["detail"]


def test_429_response_contains_retry_after_header():
    """A 429 response should include a Retry-After header."""
    # Trigger the rate limit with 5 failures first
    for _ in range(5):
        client.post("/auth/login", json={
            "email": "rat@example.com",
            "password": "wrong",
        })
    response = client.post("/auth/login", json={
        "email": "rat@example.com",
        "password": "wrong",
    })
    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_successful_login_resets_the_failed_attempt_counter():
    """A successful login should clear the rate-limit counter so the next failure starts fresh."""
    # Register the user
    client.post("/auth/register", json={
        "name": "Sam",
        "email": "sam@example.com",
        "password": "secret123",
    })
    # Fail 4 times (one below the threshold)
    for _ in range(4):
        client.post("/auth/login", json={
            "email": "sam@example.com",
            "password": "wrongpassword",
        })
    # Succeed once — this should reset the counter
    ok = client.post("/auth/login", json={
        "email": "sam@example.com",
        "password": "secret123",
    })
    assert ok.status_code == 200
    # After reset, one more failure should NOT trigger 429
    response = client.post("/auth/login", json={
        "email": "sam@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_rate_limit_does_not_affect_a_different_email():
    """Rate limiting one email should not block logins for a different email."""
    # Trigger the limit for ghost@example.com
    for _ in range(5):
        client.post("/auth/login", json={
            "email": "ghost2@example.com",
            "password": "wrong",
        })
    # A completely different email should still return 401 (not 429)
    response = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "wrong",
    })
    assert response.status_code == 401


# --- Security headers ---

def test_health_endpoint_returns_security_headers():
    """GET /health should include X-Content-Type-Options, X-Frame-Options, Referrer-Policy."""
    response = client.get("/health")
    assert response.status_code == 200
    # Check the three security headers added by the middleware
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"


# --- CORS ---

def test_cors_allows_the_configured_origin():
    """A request from the configured CORS origin should include Access-Control-Allow-Origin."""
    response = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    # The allowed origin should appear in the CORS response header
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_does_not_allow_an_unconfigured_origin():
    """A request from an unconfigured origin should not get Access-Control-Allow-Origin back."""
    response = client.options(
        "/auth/login",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    # The unconfigured origin must not be reflected
    allow_origin = response.headers.get("access-control-allow-origin", "")
    assert "evil.example.com" not in allow_origin


# --- Production safety check ---

def test_config_raises_in_production_with_default_key():
    """check_production_safety() should raise RuntimeError in production with the default key."""
    from backend.app.platform.config import check_production_safety
    # Temporarily set ENVIRONMENT to production and use the default key
    original_env = os.environ.get("ENVIRONMENT")
    original_key = os.environ.get("SECRET_KEY")
    try:
        os.environ["ENVIRONMENT"] = "production"
        # Ensure SECRET_KEY is not set so get_secret_key() returns the default
        os.environ.pop("SECRET_KEY", None)
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            check_production_safety()
    finally:
        # Restore original environment after the test
        if original_env is None:
            os.environ.pop("ENVIRONMENT", None)
        else:
            os.environ["ENVIRONMENT"] = original_env
        if original_key is not None:
            os.environ["SECRET_KEY"] = original_key
