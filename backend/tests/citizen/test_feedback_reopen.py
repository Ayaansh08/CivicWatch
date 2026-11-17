"""Tests for complaint feedback and reopen endpoints."""
from backend.app.platform.models import Complaint
from backend.app.citizen.history import add_history


def test_submit_feedback_for_resolved_complaint(
    authenticated_client, test_category, test_user, db_session
):
    """Submitting feedback for a Resolved complaint returns success message."""
    c = Complaint(
        title="Pothole fixed issue",
        description="Pothole was repaired",
        category_id=test_category.id,
        user_id=test_user.id,
        status="Resolved",
        priority="Medium"
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    res = authenticated_client.post(f"/complaints/{c.id}/feedback", json={
        "rating": 5,
        "comment": "Great work!"
    })
    assert res.status_code == 200
    assert res.json()["message"] == "Thank you for your feedback"
    assert res.json()["rating"] == 5


def test_submit_feedback_for_unresolved_complaint_returns_400(
    authenticated_client, test_category, test_user, db_session
):
    """Submitting feedback for complaint not yet Resolved returns 400."""
    c = Complaint(
        title="Pending repair issue",
        description="Not resolved yet",
        category_id=test_category.id,
        user_id=test_user.id,
        status="In Progress",
        priority="Medium"
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    res = authenticated_client.post(f"/complaints/{c.id}/feedback", json={"rating": 4})
    assert res.status_code == 400


def test_duplicate_feedback_returns_400(
    authenticated_client, test_category, test_user, db_session
):
    """Submitting feedback twice for the same complaint returns 400."""
    c = Complaint(
        title="Cleaned park bench",
        description="Bench painted",
        category_id=test_category.id,
        user_id=test_user.id,
        status="Resolved",
        priority="Low"
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    res1 = authenticated_client.post(f"/complaints/{c.id}/feedback", json={"rating": 5})
    assert res1.status_code == 200

    res2 = authenticated_client.post(f"/complaints/{c.id}/feedback", json={"rating": 4})
    assert res2.status_code == 400


def test_reopen_resolved_complaint_sets_under_review_and_history(
    authenticated_client, test_category, test_user, db_session
):
    """Reopening a resolved complaint sets status to Under Review and adds history with reason."""
    c = Complaint(
        title="Streetlight repair verification",
        description="Light went off again",
        category_id=test_category.id,
        user_id=test_user.id,
        status="Resolved",
        priority="Medium"
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    add_history(db_session, complaint_id=c.id, status="Resolved")

    reopen_res = authenticated_client.post(f"/complaints/{c.id}/reopen", json={
        "reason": "Light flickers and goes off"
    })
    assert reopen_res.status_code == 200
    assert reopen_res.json()["status"] == "Under Review"

    hist_res = authenticated_client.get(f"/complaints/{c.id}/history")
    history = hist_res.json()
    assert len(history) == 2
    assert history[-1]["status"] == "Under Review"
    assert "Reopened by citizen: Light flickers and goes off" in history[-1]["note"]


def test_reopen_unresolved_complaint_returns_400(
    authenticated_client, test_category, test_user, db_session
):
    """Reopening a complaint that is not Resolved returns 400."""
    c = Complaint(
        title="Open ongoing complaint",
        description="Still being worked on",
        category_id=test_category.id,
        user_id=test_user.id,
        status="Submitted",
        priority="Medium"
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    res = authenticated_client.post(f"/complaints/{c.id}/reopen", json={"reason": "Why so slow"})
    assert res.status_code == 400


def test_feedback_and_reopen_by_other_user_returns_403(
    make_authenticated_client, other_user, test_category, test_user, db_session
):
    """Another citizen cannot rate or reopen someone else's complaint."""
    c = Complaint(
        title="User1 resolved complaint",
        description="Resolved for user1",
        category_id=test_category.id,
        user_id=test_user.id,
        status="Resolved",
        priority="Low"
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    client2 = make_authenticated_client(other_user)
    fb_res = client2.post(f"/complaints/{c.id}/feedback", json={"rating": 3})
    assert fb_res.status_code == 403

    reopen_res = client2.post(f"/complaints/{c.id}/reopen", json={"reason": "Not resolved"})
    assert reopen_res.status_code == 403
