"""
Pure status-transition logic for complaints (CW-301).

This module has NO database, NO FastAPI, and NO file access.
It only checks whether a complaint can move from one status to another.
"""


class InvalidTransition(ValueError):
    """Raised when a complaint tries to move to a status that is not allowed."""
    pass


# Each key is a current status, and its value is the list of statuses it can move to.
# "Resolved" and "Rejected" are final — they have no outgoing transitions.
ALLOWED_TRANSITIONS = {
    "Submitted": ["Under Review", "Rejected"],
    "Under Review": ["Assigned", "Rejected"],
    "Assigned": ["In Progress"],
    "In Progress": ["Resolved"],
    "Resolved": [],
    "Rejected": [],
}


def _validate_status_name(status):
    """Raise ValueError if the status name is not one of the known statuses."""
    # Check that the status exists in the transition map
    if status not in ALLOWED_TRANSITIONS:
        raise ValueError(f"Unknown status: '{status}'")


def can_transition(current, new):
    """Return True if a complaint can move from current to new, False otherwise."""
    # Make sure both status names are valid before checking the rule
    _validate_status_name(current)
    _validate_status_name(new)
    # Look up the list of allowed next statuses and check if new is in it
    return new in ALLOWED_TRANSITIONS[current]


def get_allowed_transitions(current):
    """Return a list of statuses that a complaint can move to from current."""
    # Make sure the status name is valid
    _validate_status_name(current)
    # Return a copy of the allowed list so callers cannot accidentally modify it
    return list(ALLOWED_TRANSITIONS[current])


def validate_transition(current, new):
    """Do nothing if the move is valid; raise InvalidTransition if not."""
    # Check the transition and raise a clear error if it is not allowed
    if not can_transition(current, new):
        raise InvalidTransition(
            f"Cannot move complaint from '{current}' to '{new}'"
        )


# NOTE: The review API (CW-303, Sprint 2) will call validate_transition
# and turn InvalidTransition into an HTTP 400 response.
