"""
FastAPI route handlers for geospatial queries on complaints.
Provides /geo/complaints/nearby, /geo/complaints/bbox, /geo/heatmap,
/geo/hotspots, and /geo/reports/summary endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.platform.database import get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User, Complaint, Category
from backend.app.geo.schemas import (
    GeoComplaintOut,
    DensityCellOut,
    HotspotOut,
    ReportsSummaryOut,
)
from backend.app.geo.queries import query_nearby_complaints, query_bbox_complaints
from backend.app.geo.permissions import require_officer
from backend.app.geo.density import build_density
from backend.app.geo.hotspot_api import get_hotspots_with_categories
from backend.app.geo.reports import build_summary_report
from backend.app.geo.constants import MAX_RESULTS, HEATMAP_CELL_SIZE

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


@router.get(
    "/heatmap",
    response_model=List[DensityCellOut],
    summary="Get complaint density heatmap cells",
)
def get_heatmap_endpoint(
    min_lat: float = Query(..., ge=-90.0, le=90.0, description="Minimum latitude (-90 to 90)"),
    min_lon: float = Query(..., ge=-180.0, le=180.0, description="Minimum longitude (-180 to 180)"),
    max_lat: float = Query(..., ge=-90.0, le=90.0, description="Maximum latitude (-90 to 90)"),
    max_lon: float = Query(..., ge=-180.0, le=180.0, description="Maximum longitude (-180 to 180)"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    status_param: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    # Restricted to officer and admin users
    current_user: User = Depends(require_officer),
):
    """
    Retrieve aggregated density cells for complaints within the bounding box.
    Restricted to authority officers and system administrators.
    """
    # Validate bounding box coordinates order
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

    # Validate status parameter
    if status_param is not None and status_param not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status: {status_param}",
        )

    # Build query on complaints within bounding box
    query = db.query(Complaint.latitude, Complaint.longitude).filter(
        Complaint.latitude >= min_lat,
        Complaint.latitude <= max_lat,
        Complaint.longitude >= min_lon,
        Complaint.longitude <= max_lon,
    )

    # Apply optional category filter
    if category_id is not None:
        query = query.filter(Complaint.category_id == category_id)

    # Apply optional status filter
    if status_param is not None:
        query = query.filter(Complaint.status == status_param)

    # Execute query with safety limit
    rows = query.limit(MAX_RESULTS).all()

    # Format points list for density function
    points = [{"lat": r[0], "lon": r[1]} for r in rows]

    # Group points into density cells using the configured heatmap cell size
    return build_density(points, cell_size=HEATMAP_CELL_SIZE)


@router.get(
    "/hotspots",
    response_model=List[HotspotOut],
    summary="Get spatial complaint hotspots",
)
def get_hotspots_endpoint(
    cell_size: float = Query(
        0.01,
        ge=0.001,
        le=0.1,
        description="Grid cell size in degrees (0.001 to 0.1)",
    ),
    min_count: int = Query(
        3,
        ge=2,
        description="Minimum complaint count threshold (at least 2)",
    ),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    status_param: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    # Restricted to officer and admin users
    current_user: User = Depends(require_officer),
):
    """
    Identify spatial complaint hotspots with dominant category tags.
    Restricted to authority officers and system administrators.
    """
    # Explicit parameter boundary checks returning 422
    if cell_size < 0.001 or cell_size > 0.1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="cell_size must be between 0.001 and 0.1",
        )
    if min_count < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_count must be at least 2",
        )

    # Validate status parameter
    if status_param is not None and status_param not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status: {status_param}",
        )

    # Calculate hotspots with most common category per cell
    return get_hotspots_with_categories(
        db,
        cell_size=cell_size,
        min_count=min_count,
        category_id=category_id,
        status=status_param,
        limit=MAX_RESULTS,
    )


@router.get(
    "/reports/summary",
    response_model=ReportsSummaryOut,
    summary="Get overall analytics and geospatial summary",
)
def get_reports_summary_endpoint(
    db: Session = Depends(get_db),
    # Restricted to officer and admin users
    current_user: User = Depends(require_officer),
):
    """
    Generate analytics summary containing status breakdown, category distribution,
    top geographic areas, and average resolution time.
    """
    # Fetch complaints with category names and timestamps
    rows = (
        db.query(
            Complaint.status,
            Complaint.latitude,
            Complaint.longitude,
            Complaint.created_at,
            Complaint.updated_at,
            Category.name.label("category_name"),
        )
        .outerjoin(Category, Complaint.category_id == Category.id)
        .limit(MAX_RESULTS)
        .all()
    )

    # Format rows into plain dictionaries for pure calculation functions
    complaints = [
        {
            "status": r.status,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
            "category": r.category_name or "General",
        }
        for r in rows
    ]

    # Calculate summary using pure reporting module
    return build_summary_report(complaints)
