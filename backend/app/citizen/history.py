"""Helper function to record complaint status history."""
from sqlalchemy.orm import Session
from backend.app.citizen.models import StatusHistory


def add_history(
    db: Session,
    complaint_id: int,
    status: str,
    note: str = None,
    changed_by: int = None,
):
    """
    Record a new entry in the complaint status history.
    Other modules call this when they change a status.
    """
    # Create the history record
    history_entry = StatusHistory(
        complaint_id=complaint_id,
        status=status,
        note=note,
        changed_by=changed_by,
    )

    # Save to database
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)

    return history_entry
