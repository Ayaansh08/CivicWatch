"""Tests for the Review API endpoints (CW-303)."""
from backend.app.citizen.models import StatusHistory


def test_citizen_cannot_review_complaint(citizen_client, submitted_complaint):
    """A citizen user gets 403 when calling the review endpoint."""
    response = citizen_client.post(f"/authority/complaints/{submitted_complaint.id}/review")
    assert response.status_code == 403


def test_no_token_returns_401(plain_client, submitted_complaint):
    """A request with no token gets 401 from the review endpoint."""
    response = plain_client.post(f"/authority/complaints/{submitted_complaint.id}/review")
    assert response.status_code == 401


def test_officer_can_list_complaints(officer_client, submitted_complaint):
    """An officer can list complaints and sees the submitted one."""
    response = officer_client.get("/authority/complaints")
    assert response.status_code == 200
    ids = [c["id"] for c in response.json()]
    assert submitted_complaint.id in ids


def test_review_moves_complaint_to_under_review(officer_client, submitted_complaint):
    """Reviewing a Submitted complaint changes its status to Under Review."""
    response = officer_client.post(
        f"/authority/complaints/{submitted_complaint.id}/review"
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Under Review"


def test_review_writes_a_history_row(officer_client, submitted_complaint, db_session):
    """Reviewing a complaint creates a StatusHistory entry."""
    officer_client.post(f"/authority/complaints/{submitted_complaint.id}/review")
    # Expire cached state so we see the committed rows from the API request
    db_session.expire_all()
    history = db_session.query(StatusHistory).filter(
        StatusHistory.complaint_id == submitted_complaint.id
    ).all()
    assert len(history) == 1
    assert history[0].status == "Under Review"


def test_reviewing_already_under_review_returns_400(officer_client, submitted_complaint):
    """Reviewing a complaint that is already Under Review returns 400."""
    # First review — valid
    officer_client.post(f"/authority/complaints/{submitted_complaint.id}/review")
    # Second review — invalid transition
    response = officer_client.post(
        f"/authority/complaints/{submitted_complaint.id}/review"
    )
    assert response.status_code == 400


def test_review_missing_complaint_returns_404(officer_client):
    """Reviewing a complaint that does not exist returns 404."""
    response = officer_client.post("/authority/complaints/99999/review")
    assert response.status_code == 404
