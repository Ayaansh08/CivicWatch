"""
Pydantic response schemas for geospatial endpoints.
Defines output format for complaints retrieved through nearby and bounding-box queries,
as well as density heatmap cells.
"""
from typing import Optional
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
