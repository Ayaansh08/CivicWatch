"""
Admin-only management routes for departments, officers, and user roles.
Every route on this router requires the 'admin' role via require_role("admin").
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.platform.admin_schemas import (
    DepartmentCreate,
    DepartmentOut,
    OfficerCreate,
    RoleUpdate,
    UserOut,
)
from backend.app.platform.database import get_db
from backend.app.platform.deps import require_role
from backend.app.platform.models import Complaint, Department, User
from backend.app.platform.pagination import paginate, pagination_params
from backend.app.platform.security import hash_password

# Protect all routes under /admin so only admins can access them
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role("admin"))],
)


@router.post(
    "/departments",
    response_model=DepartmentOut,
    status_code=201,
    summary="Create a department",
    description="Create a new city department. Returns 400 if the name already exists.",
)
def create_department(
    payload: DepartmentCreate, db: Session = Depends(get_db)
):
    """Create a new city department."""
    # Reject duplicate department names
    existing = (
        db.query(Department).filter(Department.name == payload.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department name already exists",
        )
    # Save and return the new department
    department = Department(name=payload.name)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.get(
    "/departments",
    summary="List departments",
    description="Return a paginated list of all city departments.",
)
def list_departments(
    db: Session = Depends(get_db),
    params: dict = Depends(pagination_params),
):
    """Return a paginated list of all city departments."""
    # Build a base query sorted by id, then apply pagination
    query = db.query(Department).order_by(Department.id)
    return paginate(query, params["page"], params["size"])


@router.put(
    "/departments/{department_id}",
    response_model=DepartmentOut,
    summary="Rename a department",
    description="Rename an existing department. Returns 404 if not found, 400 on duplicate name.",
)
def rename_department(
    department_id: int,
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
):
    """Rename an existing city department by its id."""
    # Look up the target department
    department = (
        db.query(Department).filter(Department.id == department_id).first()
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    # Prevent renaming to a name already used by another department
    duplicate = (
        db.query(Department)
        .filter(Department.name == payload.name, Department.id != department_id)
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department name already exists",
        )
    # Update and save the department name
    department.name = payload.name
    db.commit()
    db.refresh(department)
    return department


@router.delete(
    "/departments/{department_id}",
    status_code=204,
    summary="Delete a department",
    description="Delete a department if no complaints are assigned to it.",
)
def delete_department(department_id: int, db: Session = Depends(get_db)):
    """Delete a department if no complaints are assigned to it."""
    # Look up the target department
    department = (
        db.query(Department).filter(Department.id == department_id).first()
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    # Refuse deletion if any complaint references this department
    assigned_complaint = (
        db.query(Complaint)
        .filter(Complaint.department_id == department_id)
        .first()
    )
    if assigned_complaint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete department with assigned complaints",
        )
    # Delete the unused department
    db.delete(department)
    db.commit()
    return None


@router.post(
    "/officers",
    response_model=UserOut,
    status_code=201,
    summary="Create an officer",
    description="Create a new user account with the officer role. Returns 400 on duplicate email.",
)
def create_officer(payload: OfficerCreate, db: Session = Depends(get_db)):
    """Create a new user account with the 'officer' role."""
    # Reject duplicate email addresses
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    # Hash the password and store the new officer user
    officer = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="officer",
    )
    db.add(officer)
    db.commit()
    db.refresh(officer)
    return officer


@router.get(
    "/officers",
    summary="List officers",
    description="Return a paginated list of all users with the officer role.",
)
def list_officers(
    db: Session = Depends(get_db),
    params: dict = Depends(pagination_params),
):
    """Return a paginated list of users whose role is 'officer'."""
    # Filter to officers only, sorted by id, then apply pagination
    query = (
        db.query(User)
        .filter(User.role == "officer")
        .order_by(User.id)
    )
    return paginate(query, params["page"], params["size"])


@router.patch(
    "/users/{user_id}/role",
    response_model=UserOut,
    summary="Change a user's role",
    description="Change a user's role to citizen, officer, or admin. An admin cannot change their own role.",
)
def update_user_role(
    user_id: int,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Change another user's role to citizen, officer, or admin."""
    # Prevent an admin from changing their own role and locking themselves out
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot change their own role",
        )
    # Look up the target user in the database
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    # Save and return the updated role
    target_user.role = payload.role
    db.commit()
    db.refresh(target_user)
    return target_user
