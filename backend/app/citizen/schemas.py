"""Request and response schemas for citizen complaints."""
import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StatusHistoryResponse(BaseModel):
    """Schema for a complaint status history entry."""

    id: int
    complaint_id: int
    status: str
    note: Optional[str] = None
    changed_by: Optional[int] = None
    changed_at: datetime.datetime


class ComplaintCreate(BaseModel):
    """Validate the data submitted when a citizen creates a complaint."""

    title: str = Field(min_length=5)
    description: str
    category_id: int
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class FeedbackCreate(BaseModel):
    """Schema for submitting feedback on a resolved complaint."""

    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class ReopenRequest(BaseModel):
    """Schema for requesting a resolved complaint to be reopened."""

    reason: str = Field(min_length=5)


class ComplaintResponse(BaseModel):
    """Define the complaint details returned by the API."""

    id: int
    title: str
    description: Optional[str]
    category_id: int
    category_name: str
    status: str
    priority: str
    latitude: Optional[float]
    longitude: Optional[float]
    photo_path: Optional[str] = None
    rating: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    user_id: int
