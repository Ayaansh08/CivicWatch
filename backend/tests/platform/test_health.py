"""Tests for the /health endpoint."""
from fastapi.testclient import TestClient
from backend.app.main import app

# Create a test client that talks to the FastAPI app without a real server
client = TestClient(app)


def test_health_endpoint_returns_200():
    """Health endpoint should respond with HTTP 200."""
    # Send a GET request to /health
    response = client.get("/health")
    # Check the status code is 200 OK
    assert response.status_code == 200


def test_health_endpoint_returns_status_ok():
    """Health endpoint should return the JSON body {"status": "ok"}."""
    # Send a GET request to /health
    response = client.get("/health")
    # Check the response body matches exactly
    assert response.json() == {"status": "ok"}
