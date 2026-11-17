"""
Authority API router (CW-302, CW-303, CW-304, CW-305).

Endpoints for listing, reviewing, assigning and updating complaints.
"""
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.platform.database import get_db
from backend.app.platform.models import User, Complaint, Category, Department
from backend.app.platform.deps import get_current_user
from backend.app.authority.permissions import require_officer
from backend.app.authority.workflow import validate_transition, InvalidTransition
from backend.app.citizen.history import add_history

# Authority router — all endpoints start with /authority
router = APIRouter(prefix="/authority", tags=["authority"])

# Valid priority levels for complaints
VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}


# --- Request body schemas ---

class AssignBody(BaseModel):
    """Body for POST /authority/complaints/{id}/assign."""
    department_id: int
    priority: str


class StatusBody(BaseModel):
    """Body for POST /authority/complaints/{id}/status."""
    status: str
    note: Optional[str] = None


# --- Helper: look up a complaint or raise 404 ---

def get_complaint_or_404(complaint_id: int, db: Session) -> Complaint:
    """Return the complaint with the given id, or raise HTTP 404."""
    # Query the complaints table by primary key
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


# --- Helper: apply a status change and record history ---

def change_status(db: Session, complaint: Complaint, new_status: str,
                  user: User, note: str = None):
    """Validate the transition, update the complaint, and write a history row."""
    # validate_transition raises InvalidTransition if the move is not allowed
    try:
        validate_transition(complaint.status, new_status)
    except InvalidTransition as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    # Apply the status change and timestamp
    complaint.status = new_status
    complaint.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    # Record the change in history
    add_history(db, complaint.id, new_status, note=note, changed_by=user.id)


# --- Endpoints ---

@router.get("/ping")
def ping():
    """Health check for the authority module."""
    # Role check (officer or admin only) is added in Sprint 2 by the platform RBAC (CW-208)
    return {"module": "authority", "status": "ok"}


@router.get("/complaints")
def list_complaints(
    status: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    sort: Optional[str] = Query("newest"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """
    List all complaints for officers.

    Supports optional ?status= and ?category_id= filters and sort=priority|age|newest.
    Returns at most 200 complaints.
    """
    # Validate sort parameter
    valid_sorts = {"newest", "priority", "age"}
    if sort not in valid_sorts:
        raise HTTPException(status_code=422, detail=f"sort must be one of {valid_sorts}")

    # Build the base query joining Category and Department for display names
    query = db.query(Complaint, Category, Department).join(
        Category, Complaint.category_id == Category.id
    ).outerjoin(
        Department, Complaint.department_id == Department.id
    )

    # Apply optional status filter
    if status:
        query = query.filter(Complaint.status == status)
    # Apply optional category filter
    if category_id:
        query = query.filter(Complaint.category_id == category_id)

    # Apply sort order
    if sort == "priority":
        # Critical first — use a CASE-like ordering via Python after fetch (simple approach)
        pass
    elif sort == "age":
        query = query.order_by(Complaint.created_at.asc())
    else:
        # Default: newest first
        query = query.order_by(Complaint.created_at.desc())

    # Fetch up to 200 results
    rows = query.limit(200).all()

    # Priority sort order map (Critical=0 is highest)
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}

    # Build response list
    result = []
    for complaint, category, department in rows:
        result.append({
            "id": complaint.id,
            "title": complaint.title,
            "category_name": category.name,
            "department_name": department.name if department else None,
            "status": complaint.status,
            "priority": complaint.priority,
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
            "updated_at": complaint.updated_at.isoformat() if complaint.updated_at else None,
        })

    # Sort by priority in Python if requested (avoids complex SQL CASE)
    if sort == "priority":
        result.sort(key=lambda c: priority_order.get(c["priority"], 99))

    return result


@router.post("/complaints/{complaint_id}/review")
def review_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """Move a complaint from Submitted to Under Review (CW-303)."""
    # Fetch complaint or 404
    complaint = get_complaint_or_404(complaint_id, db)
    # Apply transition (raises 400 if invalid)
    change_status(db, complaint, "Under Review", current_user,
                  note="Complaint taken under review")
    return {"id": complaint.id, "status": complaint.status}


@router.get("/departments")
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """Return all departments (CW-304)."""
    # Fetch all department rows
    departments = db.query(Department).all()
    return [{"id": d.id, "name": d.name} for d in departments]


@router.post("/complaints/{complaint_id}/assign")
def assign_complaint(
    complaint_id: int,
    body: AssignBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """Assign a complaint to a department and set priority (CW-304)."""
    # Validate priority value
    if body.priority not in VALID_PRIORITIES:
        raise HTTPException(
            status_code=422,
            detail=f"priority must be one of {sorted(VALID_PRIORITIES)}",
        )
    # Fetch complaint or 404
    complaint = get_complaint_or_404(complaint_id, db)
    # Check department exists
    department = db.query(Department).filter(Department.id == body.department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    # Apply transition Under Review -> Assigned (raises 400 if wrong status)
    change_status(db, complaint, "Assigned", current_user,
                  note=f"Assigned to {department.name}, priority {body.priority}")
    # Set department and priority
    complaint.department_id = body.department_id
    complaint.priority = body.priority
    complaint.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    return {"id": complaint.id, "status": complaint.status,
            "department_id": complaint.department_id, "priority": complaint.priority}


@router.post("/complaints/{complaint_id}/status")
def update_status(
    complaint_id: int,
    body: StatusBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """Move a complaint to any allowed next status (CW-305)."""
    # Fetch complaint or 404
    complaint = get_complaint_or_404(complaint_id, db)
    # Apply transition (raises 400 if invalid)
    change_status(db, complaint, body.status, current_user, note=body.note)
    return {"id": complaint.id, "status": complaint.status}


@router.post("/escalate")
def escalate_overdue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    """Auto-escalate priority for complaints overdue by 48+ hours (CW-306)."""
    from backend.app.authority.escalation import escalate_priority, find_overdue
    # Fetch all non-final complaints
    complaints = db.query(Complaint).filter(
        Complaint.status.notin_(["Resolved", "Rejected"])
    ).all()
    now = datetime.datetime.utcnow()
    # Find the ones that are overdue
    overdue = find_overdue(complaints, now)
    escalated_ids = []
    for complaint in overdue:
        old_priority = complaint.priority
        new_priority = escalate_priority(old_priority)
        if new_priority == old_priority:
            # Already Critical — skip
            continue
        # Apply new priority and touch updated_at so it won't be escalated again today
        complaint.priority = new_priority
        complaint.updated_at = now
        db.commit()
        add_history(
            db, complaint.id, complaint.status,
            note=f"Auto-escalated from {old_priority} to {new_priority}",
            changed_by=current_user.id,
        )
        escalated_ids.append(complaint.id)
    return {"escalated_count": len(escalated_ids), "escalated_ids": escalated_ids}
