"""
Pydantic response schemas for geospatial endpoints.
Defines output format for complaints retrieved through nearby and bounding-box queries,
density heatmap cells, hotspot zones, and analytics reports.
"""
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class GeoComplaintOut(BaseModel):
    """
    Schema for a complaint returned by geospatial queries.
    Contains basic complaint info, coordinates, and optional distance.
    """
    id: int
    title: str
    category_name: str
    status: str
    priority: str
    latitude: float
    longitude: float
    distance_km: Optional[float] = None

    # Enable ORM attribute mapping compatibility
    model_config = ConfigDict(from_attributes=True)


class DensityCellOut(BaseModel):
    """
    Schema for a density grid cell returned by the heatmap endpoint.
    Contains center coordinates and aggregated complaint count.
    """
    lat: float
    lon: float
    count: int

    model_config = ConfigDict(from_attributes=True)


class HotspotOut(BaseModel):
    """
    Schema for a spatial density hotspot cluster.
    Contains center coordinates, complaint count, and the most common category.
    """
    count: int
    center_lat: float
    center_lon: float
    category: str

    model_config = ConfigDict(from_attributes=True)


class StatusCount(BaseModel):
    """Complaint count grouped by lifecycle status."""
    status: str
    count: int


class CategoryCount(BaseModel):
    """Complaint count grouped by category."""
    category: str
    count: int


class AreaCount(BaseModel):
    """Complaint count grouped by geographic grid area."""
    area: str
    count: int


class ReportsSummaryOut(BaseModel):
    """
    Overall system analytics summary report.
    Includes totals, distributions by status, category, top geographic areas,
    and average resolution duration in hours.
    """
    total: int
    by_status: List[StatusCount]
    by_category: List[CategoryCount]
    by_area: List[AreaCount]
    avg_resolution_hours: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
