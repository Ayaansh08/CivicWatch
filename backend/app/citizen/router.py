"""API routes for citizen complaint operations."""
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.app.platform.database import get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import Category, Complaint, User
from backend.app.citizen.models import StatusHistory, Feedback
from backend.app.citizen.history import add_history
from backend.app.citizen.schemas import (
    ComplaintCreate,
    ComplaintResponse,
    StatusHistoryResponse,
)

# Directory where uploaded complaint photos are stored
UPLOAD_DIR = "backend/uploads"

router = APIRouter(prefix="/complaints", tags=["Citizen Complaints"])


@router.post("", response_model=ComplaintResponse, status_code=201)
def create_complaint(
    complaint_data: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a complaint for the currently authenticated citizen."""

    # Check whether the selected category exists.
    category = db.query(Category).filter(
        Category.id == complaint_data.category_id
    ).first()

    if category is None:
        raise HTTPException(status_code=400, detail="Category not found")

    # Prepare the complaint using the logged-in user's ID.
    new_complaint = Complaint(
        title=complaint_data.title,
        description=complaint_data.description,
        category_id=complaint_data.category_id,
        latitude=complaint_data.latitude,
        longitude=complaint_data.longitude,
        user_id=current_user.id,
        status="Submitted",
        priority="Medium",
    )

    # Save the complaint in the database.
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    # Record the initial Submitted status in history
    add_history(db, complaint_id=new_complaint.id, status="Submitted")

    # Return the saved complaint with its category name.
    return {
        "id": new_complaint.id,
        "title": new_complaint.title,
        "description": new_complaint.description,
        "category_id": new_complaint.category_id,
        "category_name": category.name,
        "status": new_complaint.status,
        "priority": new_complaint.priority,
        "latitude": new_complaint.latitude,
        "longitude": new_complaint.longitude,
        "photo_path": new_complaint.photo_path,
        "rating": None,
        "created_at": new_complaint.created_at,
        "user_id": new_complaint.user_id,
    }


@router.get("/categories")
def get_complaint_categories(db: Session = Depends(get_db)):
    """Return all available complaint categories."""

    # Fetch the categories from the database.
    categories = db.query(Category).all()

    # Return category IDs and names.
    return [
        {"id": category.id, "name": category.name}
        for category in categories
    ]


@router.get("/mine", response_model=list[ComplaintResponse])
def get_my_complaints(
    status: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all complaints submitted by the logged-in citizen, newest first."""
    query = db.query(Complaint).filter(Complaint.user_id == current_user.id)

    # Validate and filter by status if provided
    valid_statuses = [
        "Submitted", "Under Review", "Assigned", "In Progress", "Resolved", "Rejected"
    ]
    if status is not None:
        if status not in valid_statuses:
            raise HTTPException(status_code=422, detail="Invalid status filter")
        query = query.filter(Complaint.status == status)

    # Filter by category if provided
    if category_id is not None:
        query = query.filter(Complaint.category_id == category_id)

    # Sort newest first
    complaints = query.order_by(Complaint.created_at.desc()).all()

    # Build response with category_name and rating
    results = []
    for c in complaints:
        cat = db.query(Category).filter(Category.id == c.category_id).first()
        fb = db.query(Feedback).filter(Feedback.complaint_id == c.id).first()
        results.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "category_id": c.category_id,
            "category_name": cat.name if cat else "",
            "status": c.status,
            "priority": c.priority,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "photo_path": c.photo_path,
            "rating": fb.rating if fb else None,
            "created_at": c.created_at,
            "user_id": c.user_id,
        })
    return results


@router.get("/{complaint_id}/history", response_model=list[StatusHistoryResponse])
def get_complaint_history(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve status history for a complaint owned by the citizen in chronological order."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if complaint.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view history for this complaint"
        )

    history = (
        db.query(StatusHistory)
        .filter(StatusHistory.complaint_id == complaint_id)
        .order_by(StatusHistory.changed_at.asc())
        .all()
    )
    return history


@router.post("/{complaint_id}/photo", response_model=ComplaintResponse)
def upload_complaint_photo(
    complaint_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a photo for a complaint owned by the current citizen."""
    # Look up the complaint in the database
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Check ownership
    if complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this complaint")

    # Validate file extension
    filename = file.filename or ""
    _, ext = os.path.splitext(filename.lower())
    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed")

    # Validate content type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid image content type")

    # Read file content and check size (max 2 MB = 2 * 1024 * 1024 bytes)
    content = file.file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 2 MB")

    # Save to UPLOAD_DIR with unique uuid
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # Update complaint photo path
    photo_url = f"/uploads/{saved_filename}"
    complaint.photo_path = photo_url
    db.commit()
    db.refresh(complaint)

    # Get category name
    category = db.query(Category).filter(Category.id == complaint.category_id).first()
    category_name = category.name if category else ""

    return {
        "id": complaint.id,
        "title": complaint.title,
        "description": complaint.description,
        "category_id": complaint.category_id,
        "category_name": category_name,
        "status": complaint.status,
        "priority": complaint.priority,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "photo_path": complaint.photo_path,
        "user_id": complaint.user_id,
    }
