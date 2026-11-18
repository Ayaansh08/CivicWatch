"""Tests for the generic status-update endpoint (CW-305)."""
import pytest


@pytest.fixture
def in_progress_complaint(officer_client, submitted_complaint, test_department):
    """Walk a complaint from Submitted all the way to In Progress."""
    cid = submitted_complaint.id
    # Move through the full workflow step by step
    officer_client.post(f"/authority/complaints/{cid}/review")
    officer_client.post(
        f"/authority/complaints/{cid}/assign",
        json={"department_id": test_department.id, "priority": "Medium"},
    )
    officer_client.post(
        f"/authority/complaints/{cid}/status", json={"status": "In Progress"}
    )
    # Return the original submitted_complaint — its id is still valid
    return submitted_complaint


def test_valid_status_update_moves_complaint(officer_client, in_progress_complaint):
    """Moving In Progress -> Resolved through the status endpoint returns 200."""
    response = officer_client.post(
        f"/authority/complaints/{in_progress_complaint.id}/status",
        json={"status": "Resolved"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Resolved"


def test_invalid_status_transition_returns_400(officer_client, submitted_complaint):
    """Jumping Submitted -> Resolved directly returns 400."""
    response = officer_client.post(
        f"/authority/complaints/{submitted_complaint.id}/status",
        json={"status": "Resolved"},
    )
    assert response.status_code == 400
