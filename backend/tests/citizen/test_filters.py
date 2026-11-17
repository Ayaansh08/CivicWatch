"""Tests for filtering My Complaints by status and category."""
from backend.app.platform.models import Complaint, Category


def test_mine_filter_by_status(authenticated_client, test_user, test_category, db_session):
    """GET /complaints/mine?status=Resolved returns only resolved complaints."""
    c1 = Complaint(
        title="Submitted issue",
        description="Just created",
        category_id=test_category.id,
        user_id=test_user.id,
        status="Submitted",
        priority="Medium"
    )
    c2 = Complaint(
        title="Resolved issue",
        description="Already fixed",
        category_id=test_category.id,
        user_id=test_user.id,
        status="Resolved",
        priority="Low"
    )
    db_session.add_all([c1, c2])
    db_session.commit()

    res = authenticated_client.get("/complaints/mine?status=Resolved")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["title"] == "Resolved issue"
    assert items[0]["status"] == "Resolved"


def test_mine_invalid_status_returns_422(authenticated_client):
    """Passing an invalid status query parameter returns 422."""
    res = authenticated_client.get("/complaints/mine?status=InvalidStatus")
    assert res.status_code == 422


def test_mine_filter_by_category(authenticated_client, test_user, test_category, db_session):
    """GET /complaints/mine?category_id=X filters complaints by category."""
    cat2 = Category(name="Electricity")
    db_session.add(cat2)
    db_session.commit()
    db_session.refresh(cat2)

    c1 = Complaint(
        title="Road pothole",
        description="Hole on street",
        category_id=test_category.id,
        user_id=test_user.id,
        status="Submitted",
        priority="Medium"
    )
    c2 = Complaint(
        title="Power blackout",
        description="No power in sector 4",
        category_id=cat2.id,
        user_id=test_user.id,
        status="Submitted",
        priority="High"
    )
    db_session.add_all([c1, c2])
    db_session.commit()

    res = authenticated_client.get(f"/complaints/mine?category_id={cat2.id}")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["title"] == "Power blackout"
    assert items[0]["category_name"] == "Electricity"
