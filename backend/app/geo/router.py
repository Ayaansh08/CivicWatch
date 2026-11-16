"""
FastAPI route handlers for geospatial queries on complaints.
Provides /geo/complaints/nearby and /geo/complaints/bbox endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.platform.database import get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User
from backend.app.geo.schemas import GeoComplaintOut
from backend.app.geo.queries import query_nearby_complaints, query_bbox_complaints

# Create APIRouter with /geo prefix and tag
router = APIRouter(prefix="/geo", tags=["geo"])


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
    # NOTE: Role-based restrictions will come later from teammate Gaurav's RBAC
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
    db: Session = Depends(get_db),
    # Authentication required for all users
    # NOTE: Role-based restrictions will come later from teammate Gaurav's RBAC
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve complaints whose coordinates fall inside the specified geographic bounding box.
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

    # Execute query using the dispatcher (PostGIS on Postgres, SQL bounds on SQLite)
    return query_bbox_complaints(
        db, min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon
    )
