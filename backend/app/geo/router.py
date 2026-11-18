"""
FastAPI route handlers for geospatial queries on complaints.
Provides /geo/complaints/nearby and /geo/complaints/bbox endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.platform.database import get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User
from backend.app.geo.schemas import GeoComplaintOut
from backend.app.geo.queries import query_nearby_complaints, query_bbox_complaints

# Create APIRouter with /geo prefix and tag
router = APIRouter(prefix="/geo", tags=["geo"])

# Valid complaint status values according to the system workflow
VALID_STATUSES = {
    "Submitted",
    "Under Review",
    "Assigned",
    "In Progress",
    "Resolved",
    "Rejected",
}


@router.get(
    "/complaints/nearby",
    response_model=List[GeoComplaintOut],
    summary="Get complaints near coordinates",
)
def get_nearby_complaints_endpoint(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude in degrees (-90 to 90)"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude in degrees (-180 to 180)"),
    radius_km: float = Query(
        ..., gt=0.0, le=100.0, description="Search radius in kilometers (0 to 100)"
    ),
    db: Session = Depends(get_db),
    # Authentication required for all users
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve complaints located within radius_km of (lat, lon), ordered nearest first.
    """
    # Execute query using the dispatcher (PostGIS on Postgres, Python Haversine fallback on SQLite)
    return query_nearby_complaints(db, lat=lat, lon=lon, radius_km=radius_km)


@router.get(
    "/complaints/bbox",
    response_model=List[GeoComplaintOut],
    summary="Get complaints within bounding box",
)
def get_bbox_complaints_endpoint(
    min_lat: float = Query(..., ge=-90.0, le=90.0, description="Minimum latitude (-90 to 90)"),
    min_lon: float = Query(..., ge=-180.0, le=180.0, description="Minimum longitude (-180 to 180)"),
    max_lat: float = Query(..., ge=-90.0, le=90.0, description="Maximum latitude (-90 to 90)"),
    max_lon: float = Query(..., ge=-180.0, le=180.0, description="Maximum longitude (-180 to 180)"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    status_param: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    # Authentication required for all users
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve complaints whose coordinates fall inside the specified geographic bounding box.
    Supports optional category and status filtering.
    """
    # Validate that min values are strictly less than max values
    if min_lat >= max_lat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_lat must be less than max_lat",
        )
    if min_lon >= max_lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_lon must be less than max_lon",
        )

    # Validate status parameter against allowed complaint statuses
    if status_param is not None and status_param not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status: {status_param}",
        )

    # Execute query using the dispatcher (PostGIS on Postgres, SQL bounds on SQLite)
    return query_bbox_complaints(
        db,
        min_lat=min_lat,
        min_lon=min_lon,
        max_lat=max_lat,
        max_lon=max_lon,
        category_id=category_id,
        status=status_param,
    )
