"""Tests for My Complaints and status history endpoints."""
from backend.app.citizen.history import add_history


def test_add_history_stores_fields(test_category, test_user, db_session):
    """Calling add_history should save all fields accurately."""
    from backend.app.platform.models import Complaint
    c = Complaint(
        title="Pothole in sector 15",
        description="Road broken",
        category_id=test_category.id,
        user_id=test_user.id,
        status="Submitted",
        priority="Medium"
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    hist = add_history(
        db_session,
        complaint_id=c.id,
        status="Under Review",
        note="Initial inspection",
        changed_by=test_user.id,
    )
    assert hist.id is not None
    assert hist.status == "Under Review"
    assert hist.note == "Initial inspection"
    assert hist.changed_by == test_user.id


def test_first_history_row_is_submitted(authenticated_client, test_category):
    """Creating a complaint via POST /complaints automatically records Submitted history."""
    res = authenticated_client.post("/complaints", json={
        "title": "Streetlight broken",
        "description": "Dark area at night.",
        "category_id": test_category.id,
    })
    assert res.status_code == 201
    complaint_id = res.json()["id"]

    hist_res = authenticated_client.get(f"/complaints/{complaint_id}/history")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) == 1
    assert history[0]["status"] == "Submitted"


def test_mine_returns_only_own_complaints_newest_first(
    make_authenticated_client, test_category, test_user, other_user
):
    """GET /complaints/mine should return only the current citizen's reports, newest first."""
    client1 = make_authenticated_client(test_user)
    # User 1 creates complaint 1
    client1.post("/complaints", json={
        "title": "First complaint",
        "description": "Description 1",
        "category_id": test_category.id,
    })
    # User 1 creates complaint 2
    client1.post("/complaints", json={
        "title": "Second complaint",
        "description": "Description 2",
        "category_id": test_category.id,
    })

    # User 2 creates complaint 3
    client2 = make_authenticated_client(other_user)
    client2.post("/complaints", json={
        "title": "Other user complaint",
        "description": "Description 3",
        "category_id": test_category.id,
    })

    # User 1 fetches mine
    client1 = make_authenticated_client(test_user)
    mine_res = client1.get("/complaints/mine")
    assert mine_res.status_code == 200
    items = mine_res.json()
    titles = [item["title"] for item in items]
    assert "Other user complaint" not in titles
    assert len(titles) == 2
    assert titles[0] == "Second complaint"
    assert titles[1] == "First complaint"


def test_history_returned_in_chronological_order(authenticated_client, test_category, db_session):
    """GET /complaints/{id}/history returns entries ordered chronologically."""
    res = authenticated_client.post("/complaints", json={
        "title": "Water leak problem",
        "description": "Water overflowing on street.",
        "category_id": test_category.id,
    })
    complaint_id = res.json()["id"]

    # Add second history row
    add_history(
        db_session, complaint_id=complaint_id, status="Under Review", note="Reviewing by officer"
    )
    add_history(
        db_session, complaint_id=complaint_id, status="In Progress", note="Work started"
    )

    hist_res = authenticated_client.get(f"/complaints/{complaint_id}/history")
    assert hist_res.status_code == 200
    statuses = [h["status"] for h in hist_res.json()]
    assert statuses == ["Submitted", "Under Review", "In Progress"]


def test_history_of_other_user_returns_403(
    authenticated_client, other_authenticated_client, test_category
):
    """Accessing another user's complaint history should return 403."""
    res = authenticated_client.post("/complaints", json={
        "title": "Private issue",
        "description": "Owner only issue.",
        "category_id": test_category.id,
    })
    complaint_id = res.json()["id"]

    client2 = other_authenticated_client()
    hist_res = client2.get(f"/complaints/{complaint_id}/history")
    assert hist_res.status_code == 403


def test_history_missing_complaint_returns_404(authenticated_client):
    """Requesting history for non-existent complaint returns 404."""
    hist_res = authenticated_client.get("/complaints/99999/history")
    assert hist_res.status_code == 404
