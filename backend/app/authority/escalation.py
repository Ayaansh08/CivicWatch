"""
Pure escalation logic for overdue complaints (CW-306).

No database, no FastAPI — just plain functions.
"""
import datetime

# Priority levels in ascending order of severity
PRIORITY_ORDER = ["Low", "Medium", "High", "Critical"]

# Default threshold: complaints older than this many hours are overdue
OVERDUE_HOURS = 48


def escalate_priority(priority):
    """Move the priority one level up. Critical stays Critical."""
    # Find the current level in the priority list
    index = PRIORITY_ORDER.index(priority)
    # Move up one level if not already at the top
    if index < len(PRIORITY_ORDER) - 1:
        return PRIORITY_ORDER[index + 1]
    # Already Critical — no change
    return priority


def find_overdue(complaints, now, hours=OVERDUE_HOURS):
    """Return complaints whose status is not final and whose updated_at is older than hours."""
    # Calculate the cutoff time
    cutoff = now - datetime.timedelta(hours=hours)
    result = []
    for complaint in complaints:
        # Skip resolved or rejected complaints — they are final
        if complaint.status in ("Resolved", "Rejected"):
            continue
        # Check if the complaint's last update is older than the cutoff
        if complaint.updated_at and complaint.updated_at < cutoff:
            result.append(complaint)
    return result
