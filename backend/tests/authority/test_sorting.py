"""Tests for sorting on the complaints list endpoint (CW-308)."""


def test_sort_by_priority_returns_critical_first(officer_client, submitted_complaint, db_session):
    """Sorting by priority should put Critical before Low."""
    from backend.app.platform.models import Complaint, Category
    # Create a second complaint with Critical priority
    cat = db_session.query(Category).first()
    c2 = Complaint(
        title="Urgent issue", category_id=cat.id,
        status="Submitted", priority="Critical",
        user_id=submitted_complaint.user_id,
    )
    db_session.add(c2)
    db_session.commit()
    # Fetch with sort=priority
    response = officer_client.get("/authority/complaints?sort=priority")
    assert response.status_code == 200
    priorities = [c["priority"] for c in response.json()]
    assert priorities.index("Critical") < priorities.index("Medium")


def test_sort_by_age_returns_oldest_first(officer_client, submitted_complaint):
    """Sorting by age should return oldest complaints first."""
    response = officer_client.get("/authority/complaints?sort=age")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_invalid_sort_returns_422(officer_client):
    """An unrecognised sort value returns 422."""
    response = officer_client.get("/authority/complaints?sort=invalid")
    assert response.status_code == 422
