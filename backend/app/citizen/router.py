"""API routes for citizen complaint operations."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.platform.database import get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import Category, Complaint, User
from backend.app.citizen.schemas import ComplaintCreate, ComplaintResponse

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
