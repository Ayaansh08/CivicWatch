"""
Pure functions for density grid calculations.
Groups geographic coordinate points into equal-size grid cells.
"""
import math
from typing import List, Dict, Any

# Import the standard heatmap cell size constant
from backend.app.geo.constants import HEATMAP_CELL_SIZE


def build_density(points: List[Dict[str, Any]], cell_size: float = HEATMAP_CELL_SIZE) -> List[Dict[str, Any]]:
    """
    Group points into grid cells of size cell_size degrees and calculate cell counts.
    Returns cells sorted by count in descending order.
    Each cell dictionary contains 'lat' and 'lon' (center coordinates) and 'count'.
    """
    # Return empty list if no points provided
    if not points:
        return []

    # Map grid cell coordinates to complaint counts
    cell_counts = {}

    # Iterate through points and map each to a grid cell index
    for pt in points:
        # Support both 'lat'/'lon' and 'latitude'/'longitude' keys
        lat = pt["lat"] if "lat" in pt else pt["latitude"]
        lon = pt["lon"] if "lon" in pt else pt["longitude"]

        # Calculate cell indices using math.floor
        lat_idx = math.floor(lat / cell_size)
        lon_idx = math.floor(lon / cell_size)
        cell_key = (lat_idx, lon_idx)

        # Increment count for this cell
        cell_counts[cell_key] = cell_counts.get(cell_key, 0) + 1

    # Convert aggregated cell counts into center coordinate results
    results = []
    for (lat_idx, lon_idx), count in cell_counts.items():
        # Compute cell center coordinates rounded to 6 decimal places
        center_lat = round((lat_idx + 0.5) * cell_size, 6)
        center_lon = round((lon_idx + 0.5) * cell_size, 6)
        results.append({
            "lat": center_lat,
            "lon": center_lon,
            "count": count,
        })

    # Sort results by count descending (highest density first)
    results.sort(key=lambda item: item["count"], reverse=True)
    return results
