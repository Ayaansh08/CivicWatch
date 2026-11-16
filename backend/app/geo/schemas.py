"""
Pydantic response schemas for geospatial endpoints.
Defines output format for complaints retrieved through nearby and bounding-box queries.
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
