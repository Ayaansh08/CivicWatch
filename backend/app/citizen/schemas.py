"""Request and response schemas for citizen complaints."""
from pydantic import BaseModel, Field


class ComplaintCreate(BaseModel):
    """Validate the data submitted when a citizen creates a complaint."""

    title: str = Field(min_length=5)
    description: str
    category_id: int
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ComplaintResponse(BaseModel):
    """Define the complaint details returned by the API."""

    id: int
    title: str
    description: str | None
    category_id: int
    category_name: str
    status: str
    priority: str
    latitude: float | None
    longitude: float | None
    photo_path: str | None = None
    user_id: int
