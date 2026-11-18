"""
Geospatial query functions for complaints.

Provides two implementations:
(a) Fallback version for non-PostgreSQL databases (e.g. SQLite during automated testing),
    filtering via bounding-box coordinate ranges and computing exact Haversine distance in Python.
(b) PostGIS version for PostgreSQL in production, utilizing native spatial functions
    (ST_DWithin, ST_Distance, and the && envelope operator) backed by GiST indexes.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.platform.models import Complaint, Category
from backend.app.geo.geo_utils import bounding_box, haversine_distance_km


def get_nearby_complaints_fallback(
    db: Session, lat: float, lon: float, radius_km: float, limit: int = 500
) -> List[Dict[str, Any]]:
    """
    Find nearby complaints using SQLite/standard SQL and Python distance math.
    Pre-filters rows using a bounding box, then calculates exact Haversine distance.
    """
    # 1. Compute a rectangular bounding box around the center point for coarse filtering in SQL
    min_lat, min_lon, max_lat, max_lon = bounding_box(lat, lon, radius_km)

    # 2. Query complaints within bounding box and join category to get category name
    query = (
        db.query(Complaint, Category.name.label("category_name"))
        .join(Category, Complaint.category_id == Category.id)
        .filter(
            Complaint.latitude.between(min_lat, max_lat),
            Complaint.longitude.between(min_lon, max_lon),
        )
    )

    # 3. Compute exact great-circle distance for each candidate in Python
    results = []
    for complaint, category_name in query.all():
        dist = haversine_distance_km(lat, lon, complaint.latitude, complaint.longitude)
        # Keep only complaints strictly within the circular search radius
        if dist <= radius_km:
            results.append({
                "id": complaint.id,
                "title": complaint.title,
                "category_name": category_name,
                "status": complaint.status,
                "priority": complaint.priority,
                "latitude": complaint.latitude,
                "longitude": complaint.longitude,
                "distance_km": round(dist, 2),
            })

    # 4. Sort results by distance ascending (nearest first) and apply limit
    results.sort(key=lambda item: item["distance_km"])
    return results[:limit]


def get_bbox_complaints_fallback(
    db: Session,
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    """
    Find complaints inside a bounding box using standard SQL comparisons.
    Supports optional filtering by category_id and status.
    """
    # 1. Query complaints within the min/max latitude and longitude range
    query = (
        db.query(Complaint, Category.name.label("category_name"))
        .join(Category, Complaint.category_id == Category.id)
        .filter(
            Complaint.latitude >= min_lat,
            Complaint.latitude <= max_lat,
            Complaint.longitude >= min_lon,
            Complaint.longitude <= max_lon,
        )
    )

    # 2. Apply optional category filter if provided
    if category_id is not None:
        query = query.filter(Complaint.category_id == category_id)

    # 3. Apply optional status filter if provided
    if status is not None:
        query = query.filter(Complaint.status == status)

    # 4. Limit the query results
    query = query.limit(limit)

    # 5. Build the result dictionaries matching the expected response schema
    results = []
    for complaint, category_name in query.all():
        results.append({
            "id": complaint.id,
            "title": complaint.title,
            "category_name": category_name,
            "status": complaint.status,
            "priority": complaint.priority,
            "latitude": complaint.latitude,
            "longitude": complaint.longitude,
            "distance_km": None,
        })
    return results


def get_nearby_complaints_postgis(
    db: Session, lat: float, lon: float, radius_km: float, limit: int = 500
) -> List[Dict[str, Any]]:
    """
    Find nearby complaints using PostGIS spatial geography indexing in PostgreSQL.
    Uses ST_DWithin on location::geography for meter-accurate search, ordered by ST_Distance.
    """
    # 1. Convert radius from kilometers to meters for PostGIS geography calculations
    radius_m = radius_km * 1000.0

    # 2. Construct raw SQL using ST_DWithin and ST_Distance (note: longitude comes first)
    sql = text(
        """
        SELECT
            c.id,
            c.title,
            cat.name AS category_name,
            c.status,
            c.priority,
            c.latitude,
            c.longitude,
            ROUND(
                (ST_Distance(
                    c.location::geography,
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                ) / 1000.0)::numeric, 2
            )::float AS distance_km
        FROM complaints c
        JOIN categories cat ON c.category_id = cat.id
        WHERE c.location IS NOT NULL
          AND ST_DWithin(
              c.location::geography,
              ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
              :radius_m
          )
        ORDER BY distance_km ASC
        LIMIT :limit;
        """
    )

    # 3. Execute query and map rows to dictionaries
    result = db.execute(sql, {"lat": lat, "lon": lon, "radius_m": radius_m, "limit": limit})
    return [dict(row) for row in result.mappings().all()]


def get_bbox_complaints_postgis(
    db: Session,
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    """
    Find complaints inside a bounding box using PostGIS spatial indexing.
    Supports optional filtering by category_id and status.
    """
    # 1. Build dynamic filter conditions for optional parameters
    extra_filters = []
    params = {
        "min_lon": min_lon,
        "min_lat": min_lat,
        "max_lon": max_lon,
        "max_lat": max_lat,
        "limit": limit,
    }
    if category_id is not None:
        extra_filters.append("AND c.category_id = :category_id")
        params["category_id"] = category_id
    if status is not None:
        extra_filters.append("AND c.status = :status")
        params["status"] = status

    filter_clause = " ".join(extra_filters)

    # 2. Construct raw SQL query with envelope operator and optional filters
    sql = text(
        f"""
        SELECT
            c.id,
            c.title,
            cat.name AS category_name,
            c.status,
            c.priority,
            c.latitude,
            c.longitude,
            NULL::float AS distance_km
        FROM complaints c
        JOIN categories cat ON c.category_id = cat.id
        WHERE c.location IS NOT NULL
          AND c.location && ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
          {filter_clause}
        LIMIT :limit;
        """
    )

    # 3. Execute query and map rows to dictionaries
    result = db.execute(sql, params)
    return [dict(row) for row in result.mappings().all()]


def query_nearby_complaints(
    db: Session, lat: float, lon: float, radius_km: float, limit: int = 500
) -> List[Dict[str, Any]]:
    """
    Dispatch nearby query to PostGIS when connected to PostgreSQL, or fallback for SQLite.
    """
    # Detect dialect name to choose between PostGIS and Python fallback
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        return get_nearby_complaints_postgis(db, lat, lon, radius_km, limit)
    return get_nearby_complaints_fallback(db, lat, lon, radius_km, limit)


def query_bbox_complaints(
    db: Session,
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    """
    Dispatch bounding-box query to PostGIS when connected to PostgreSQL, or fallback for SQLite.
    """
    # Detect dialect name to choose between PostGIS and Python fallback
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        return get_bbox_complaints_postgis(
            db,
            min_lat,
            min_lon,
            max_lat,
            max_lon,
            category_id=category_id,
            status=status,
            limit=limit,
        )
    return get_bbox_complaints_fallback(
        db,
        min_lat,
        min_lon,
        max_lat,
        max_lon,
        category_id=category_id,
        status=status,
        limit=limit,
    )
