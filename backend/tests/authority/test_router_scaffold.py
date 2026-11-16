"""Tests for the authority module scaffold (CW-302)."""
from fastapi.testclient import TestClient
from backend.app.main import app

# Create a test client that talks to the FastAPI app without a real server
client = TestClient(app)


def test_authority_ping_returns_ok():
    """GET /authority/ping should return 200 and the authority module JSON."""
    # Send a GET request to the authority ping endpoint
    response = client.get("/authority/ping")
    # Check the status code is 200 OK
    assert response.status_code == 200
    # Check the response body matches exactly
    assert response.json() == {"module": "authority", "status": "ok"}
