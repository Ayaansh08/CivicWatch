"""Tests for the authority status-transition workflow (CW-301)."""
import pytest

from backend.app.authority.workflow import (
    can_transition,
    get_allowed_transitions,
    validate_transition,
    InvalidTransition,
)


# --- can_transition: allowed moves ---

def test_submitted_to_under_review_is_allowed():
    """A new complaint can move from Submitted to Under Review."""
    assert can_transition("Submitted", "Under Review") is True


def test_under_review_to_assigned_is_allowed():
    """An officer can assign a complaint that is Under Review."""
    assert can_transition("Under Review", "Assigned") is True


def test_assigned_to_in_progress_is_allowed():
    """Work begins when an Assigned complaint moves to In Progress."""
    assert can_transition("Assigned", "In Progress") is True


def test_in_progress_to_resolved_is_allowed():
    """A complaint In Progress can be marked Resolved."""
    assert can_transition("In Progress", "Resolved") is True


def test_submitted_to_rejected_is_allowed():
    """A complaint can be Rejected straight from Submitted."""
    assert can_transition("Submitted", "Rejected") is True


def test_under_review_to_rejected_is_allowed():
    """A complaint Under Review can also be Rejected."""
    assert can_transition("Under Review", "Rejected") is True


# --- can_transition: disallowed moves ---

def test_submitted_to_resolved_is_not_allowed():
    """Skipping steps: Submitted cannot jump directly to Resolved."""
    assert can_transition("Submitted", "Resolved") is False


def test_submitted_to_assigned_is_not_allowed():
    """Submitted cannot skip Under Review and jump to Assigned."""
    assert can_transition("Submitted", "Assigned") is False


def test_in_progress_to_submitted_going_backwards_is_not_allowed():
    """Going backwards from In Progress to Submitted is forbidden."""
    assert can_transition("In Progress", "Submitted") is False


def test_resolved_has_no_allowed_transitions():
    """Resolved is a final state with no outgoing transitions."""
    assert get_allowed_transitions("Resolved") == []


def test_rejected_has_no_allowed_transitions():
    """Rejected is a final state with no outgoing transitions."""
    assert get_allowed_transitions("Rejected") == []


def test_a_status_cannot_move_to_itself():
    """A complaint cannot transition to the same status it is already in."""
    assert can_transition("Submitted", "Submitted") is False


# --- get_allowed_transitions ---

def test_get_allowed_transitions_for_submitted():
    """Submitted has exactly two outgoing transitions."""
    assert get_allowed_transitions("Submitted") == ["Under Review", "Rejected"]


# --- validate_transition ---

def test_validate_transition_raises_invalid_transition_for_bad_move():
    """validate_transition raises InvalidTransition for a disallowed move."""
    with pytest.raises(InvalidTransition) as exc_info:
        validate_transition("Submitted", "Resolved")
    # The error message should mention both status names
    assert "Submitted" in str(exc_info.value)
    assert "Resolved" in str(exc_info.value)


# --- unknown status ---

def test_unknown_status_raises_value_error():
    """An unknown status like 'Pending' should raise a plain ValueError."""
    with pytest.raises(ValueError):
        can_transition("Pending", "Under Review")


# --- full happy path ---

def test_full_happy_path_submitted_to_resolved():
    """Walk the entire happy path step by step: Submitted -> Resolved."""
    # Each step in the happy path must be a valid transition
    path = [
        ("Submitted", "Under Review"),
        ("Under Review", "Assigned"),
        ("Assigned", "In Progress"),
        ("In Progress", "Resolved"),
    ]
    for current, new in path:
        assert can_transition(current, new) is True, (
            f"Expected {current} -> {new} to be allowed"
        )
