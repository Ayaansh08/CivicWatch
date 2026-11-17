"""Tests for the Assign and Departments endpoints (CW-304)."""
import pytest
from backend.app.citizen.models import StatusHistory


def test_valid_assign_sets_department_and_priority(
        officer_client, under_review_complaint, test_department):
    """Assigning with valid data sets department_id, priority, and status to Assigned."""
    response = officer_client.post(
        f"/authority/complaints/{under_review_complaint.id}/assign",
        json={"department_id": test_department.id, "priority": "High"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Assigned"
    assert data["priority"] == "High"
    assert data["department_id"] == test_department.id


def test_invalid_priority_returns_422(
        officer_client, under_review_complaint, test_department):
    """Assigning with an unrecognised priority returns 422."""
    response = officer_client.post(
        f"/authority/complaints/{under_review_complaint.id}/assign",
        json={"department_id": test_department.id, "priority": "Urgent"},
    )
    assert response.status_code == 422


def test_unknown_department_returns_404(officer_client, under_review_complaint):
    """Assigning to a non-existent department returns 404."""
    response = officer_client.post(
        f"/authority/complaints/{under_review_complaint.id}/assign",
        json={"department_id": 99999, "priority": "Medium"},
    )
    assert response.status_code == 404


def test_assigning_submitted_complaint_returns_400(
        officer_client, submitted_complaint, test_department):
    """Assigning a Submitted complaint (skipping Under Review) returns 400."""
    response = officer_client.post(
        f"/authority/complaints/{submitted_complaint.id}/assign",
        json={"department_id": test_department.id, "priority": "Medium"},
    )
    assert response.status_code == 400


def test_citizen_cannot_assign(citizen_client, submitted_complaint, test_department):
    """A citizen gets 403 when trying to assign a complaint."""
    # Citizens cannot assign regardless of the complaint's current status
    response = citizen_client.post(
        f"/authority/complaints/{submitted_complaint.id}/assign",
        json={"department_id": test_department.id, "priority": "Medium"},
    )
    assert response.status_code == 403


def test_assign_writes_a_history_row(
        officer_client, under_review_complaint, test_department, db_session):
    """Assigning a complaint creates a history entry with an informative note."""
    officer_client.post(
        f"/authority/complaints/{under_review_complaint.id}/assign",
        json={"department_id": test_department.id, "priority": "High"},
    )
    db_session.expire_all()
    history = db_session.query(StatusHistory).filter(
        StatusHistory.complaint_id == under_review_complaint.id,
        StatusHistory.status == "Assigned",
    ).first()
    assert history is not None
    assert "Roads Department" in history.note
    assert "High" in history.note
