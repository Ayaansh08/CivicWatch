"""Tests for escalation logic and endpoint (CW-306)."""
import datetime
from types import SimpleNamespace
from backend.app.authority.escalation import escalate_priority, find_overdue


# --- Pure function tests ---

def test_escalate_low_to_medium():
    """Low priority escalates to Medium."""
    assert escalate_priority("Low") == "Medium"


def test_escalate_medium_to_high():
    """Medium priority escalates to High."""
    assert escalate_priority("Medium") == "High"


def test_escalate_high_to_critical():
    """High priority escalates to Critical."""
    assert escalate_priority("High") == "Critical"


def test_critical_stays_critical():
    """Critical priority cannot be escalated further."""
    assert escalate_priority("Critical") == "Critical"


def test_resolved_complaint_is_not_overdue():
    """A Resolved complaint is never considered overdue."""
    now = datetime.datetime(2026, 1, 3)
    complaint = SimpleNamespace(
        status="Resolved",
        updated_at=datetime.datetime(2026, 1, 1),
    )
    assert find_overdue([complaint], now) == []


def test_fresh_complaint_is_not_overdue():
    """A complaint updated less than 48 hours ago is not overdue."""
    now = datetime.datetime(2026, 1, 3, 12, 0)
    complaint = SimpleNamespace(
        status="Submitted",
        updated_at=datetime.datetime(2026, 1, 3, 0, 0),
    )
    assert find_overdue([complaint], now) == []


def test_old_complaint_is_overdue():
    """A complaint updated more than 48 hours ago is overdue."""
    now = datetime.datetime(2026, 1, 5)
    complaint = SimpleNamespace(
        status="Submitted",
        updated_at=datetime.datetime(2026, 1, 1),
    )
    result = find_overdue([complaint], now)
    assert len(result) == 1


def test_boundary_exactly_48_hours_is_not_overdue():
    """A complaint updated exactly 48 hours ago is NOT overdue (must be strictly older)."""
    now = datetime.datetime(2026, 1, 3, 0, 0)
    complaint = SimpleNamespace(
        status="Submitted",
        updated_at=datetime.datetime(2026, 1, 1, 0, 0),
    )
    # exactly 48h: updated_at == cutoff, so NOT overdue (< is strict)
    assert find_overdue([complaint], now) == []


# --- Endpoint tests ---

def test_escalate_endpoint_escalates_old_complaint(officer_client, submitted_complaint, db_session):
    """The escalate endpoint raises priority of an overdue complaint."""
    from backend.app.platform.models import Complaint
    # Manually set updated_at to 3 days ago to make it overdue
    c = db_session.query(Complaint).filter(Complaint.id == submitted_complaint.id).first()
    c.updated_at = datetime.datetime.utcnow() - datetime.timedelta(days=3)
    db_session.commit()
    # Call the escalate endpoint
    response = officer_client.post("/authority/escalate")
    assert response.status_code == 200
    data = response.json()
    assert data["escalated_count"] >= 1
    assert submitted_complaint.id in data["escalated_ids"]


def test_citizen_cannot_escalate(citizen_client):
    """A citizen gets 403 when calling the escalate endpoint."""
    response = citizen_client.post("/authority/escalate")
    assert response.status_code == 403
