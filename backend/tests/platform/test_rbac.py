"""
Tests for role-based access control (require_role dependency).

Builds a small test-only FastAPI app with two protected routes so RBAC
can be tested independently of teammates' routers.
"""
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.app.platform.deps import get_current_user, require_role
from backend.app.platform.models import User


def make_user(role: str) -> User:
    """Create an in-memory User ORM object with the given role."""
    # Match the User ORM type returned by the real get_current_user dependency
    return User(
        id=1,
        name=f"Test {role}",
        email=f"{role}@civicwatch.com",
        password_hash="hashed-secret",
        role=role,
    )


def build_test_app() -> FastAPI:
    """Create a tiny FastAPI app with officer-only and admin-only test routes."""
    test_app = FastAPI()

    @test_app.get("/officer-area")
    def officer_area(user: User = Depends(require_role("officer", "admin"))):
        """Route accessible to officers and admins."""
        return {"message": "officer access granted", "role": user.role}

    @test_app.get("/admin-area")
    def admin_area(user: User = Depends(require_role("admin"))):
        """Route accessible only to admins."""
        return {"message": "admin access granted", "role": user.role}

    return test_app


def make_client_for_role(role: str) -> TestClient:
    """Return a TestClient whose get_current_user override returns a user with the given role."""
    test_app = build_test_app()
    # Override get_current_user to return a fake ORM User with the chosen role
    test_app.dependency_overrides[get_current_user] = lambda: make_user(role)
    return TestClient(test_app)


def test_citizen_calling_officer_area_gets_403():
    """A citizen should be denied access to /officer-area with HTTP 403."""
    client = make_client_for_role("citizen")
    response = client.get("/officer-area")
    assert response.status_code == 403


def test_officer_calling_officer_area_gets_200():
    """An officer should be allowed to access /officer-area with HTTP 200."""
    client = make_client_for_role("officer")
    response = client.get("/officer-area")
    assert response.status_code == 200


def test_admin_calling_officer_area_gets_200():
    """An admin should be allowed to access /officer-area with HTTP 200."""
    client = make_client_for_role("admin")
    response = client.get("/officer-area")
    assert response.status_code == 200


def test_officer_calling_admin_area_gets_403():
    """An officer should be denied access to /admin-area with HTTP 403."""
    client = make_client_for_role("officer")
    response = client.get("/admin-area")
    assert response.status_code == 403


def test_admin_calling_admin_area_gets_200():
    """An admin should be allowed to access /admin-area with HTTP 200."""
    client = make_client_for_role("admin")
    response = client.get("/admin-area")
    assert response.status_code == 200


def test_request_with_no_token_to_admin_area_gets_401():
    """Calling /admin-area without a Bearer token should fail with HTTP 401."""
    # Use the real get_current_user dependency with no override
    test_app = build_test_app()
    client = TestClient(test_app)
    response = client.get("/admin-area")
    assert response.status_code == 401


def test_user_with_unknown_role_gets_403():
    """A user whose role is unknown should be rejected with HTTP 403."""
    client = make_client_for_role("guest")
    response = client.get("/officer-area")
    assert response.status_code == 403


def test_forbidden_response_contains_clear_message():
    """A 403 response should include a clear detail message explaining the denial."""
    client = make_client_for_role("citizen")
    response = client.get("/admin-area")
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to do this"
