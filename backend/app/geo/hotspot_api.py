"""
Hotspot API helper functions.
Integrates pure find_hotspots algorithm with database queries and category analysis.
"""
import math
from typing import List, Dict, Any, Optional
from collections import Counter
from sqlalchemy.orm import Session

from backend.app.platform.models import Complaint, Category
from backend.app.geo.hotspot import find_hotspots
# Import named constants to avoid magic numbers
from backend.app.geo.constants import MAX_RESULTS, DEFAULT_CELL_SIZE


def get_hotspots_with_categories(
    db: Session,
    cell_size: float = DEFAULT_CELL_SIZE,
    min_count: int = 3,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = MAX_RESULTS,
) -> List[Dict[str, Any]]:
    """
    Retrieve complaints matching filters, compute spatial hotspots using find_hotspots,
    and determine the most common category for each detected hotspot zone.
    """
    # 1. Build database query joining Complaint and Category
    query = (
        db.query(
            Complaint.latitude,
            Complaint.longitude,
            Category.name.label("category_name"),
        )
        .outerjoin(Category, Complaint.category_id == Category.id)
        .filter(Complaint.latitude.isnot(None), Complaint.longitude.isnot(None))
    )

    # 2. Apply optional category and status filters
    if category_id is not None:
        query = query.filter(Complaint.category_id == category_id)
    if status is not None:
        query = query.filter(Complaint.status == status)

    # 3. Fetch complaint records with limit
    rows = query.limit(limit).all()

    # 4. Format complaint dicts for find_hotspots algorithm
    complaints = []
    cell_categories: Dict[tuple, List[str]] = {}

    for row in rows:
        lat = row.latitude
        lon = row.longitude
        cat_name = row.category_name or "General"

        complaints.append({"lat": lat, "lon": lon})

        # Track category by grid cell coordinate
        lat_idx = math.floor(lat / cell_size)
        lon_idx = math.floor(lon / cell_size)
        cell_key = (lat_idx, lon_idx)

        if cell_key not in cell_categories:
            cell_categories[cell_key] = []
        cell_categories[cell_key].append(cat_name)

    # 5. Call pure find_hotspots algorithm (do not modify hotspot.py)
    base_hotspots = find_hotspots(complaints, cell_size=cell_size, min_count=min_count)

    # 6. Attach most common category to each detected hotspot
    enriched_hotspots = []
    for h in base_hotspots:
        # Recover cell index from center coordinates
        lat_idx = math.floor(h["center_lat"] / cell_size)
        lon_idx = math.floor(h["center_lon"] / cell_size)
        cell_key = (lat_idx, lon_idx)

        # Determine most common category in this grid cell
        categories_in_cell = cell_categories.get(cell_key, [])
        if categories_in_cell:
            top_category = Counter(categories_in_cell).most_common(1)[0][0]
        else:
            top_category = "General"

        enriched_hotspots.append({
            "count": h["count"],
            "center_lat": h["center_lat"],
            "center_lon": h["center_lon"],
            "category": top_category,
        })

    return enriched_hotspots
