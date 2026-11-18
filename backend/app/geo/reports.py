"""
Pure functions for generating geospatial analytics reports and summaries.
Calculates totals, category distributions, status counts, geographic area groupings,
and average complaint resolution times.
"""
import math
from typing import List, Dict, Any, Optional
from collections import Counter


def count_by_status(complaints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Count complaints by their status lifecycle value.
    Returns list of dicts with 'status' and 'count' keys.
    """
    counts = Counter(c.get("status") or "Unknown" for c in complaints)
    return [{"status": status, "count": count} for status, count in counts.items()]


def count_by_category(complaints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Count complaints by category name.
    Returns list of dicts with 'category' and 'count' keys, sorted by count descending.
    """
    counts = Counter(c.get("category") or "General" for c in complaints)
    results = [{"category": cat, "count": count} for cat, count in counts.items()]
    results.sort(key=lambda x: x["count"], reverse=True)
    return results


def group_by_area(
    complaints: List[Dict[str, Any]], cell_size: float = 0.01, top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Group complaints into geographic grid cells of 0.01 degrees and label each cell
    by its lower-left corner rounded to 2 decimal places. Returns top N cells by count.
    """
    cell_counts = Counter()
    for c in complaints:
        lat = c.get("latitude")
        lon = c.get("longitude")
        # Ignore complaints without valid geographic coordinates
        if lat is not None and lon is not None:
            lat_idx = math.floor(lat / cell_size)
            lon_idx = math.floor(lon / cell_size)
            lower_lat = round(lat_idx * cell_size, 2)
            lower_lon = round(lon_idx * cell_size, 2)
            area_label = f"{lower_lat:.2f},{lower_lon:.2f}"
            cell_counts[area_label] += 1

    top_cells = cell_counts.most_common(top_n)
    return [{"area": area, "count": count} for area, count in top_cells]


def calculate_avg_resolution_hours(complaints: List[Dict[str, Any]]) -> Optional[float]:
    """
    Calculate average resolution time in hours for resolved complaints.
    Returns rounded to 1 decimal place, or None if no complaints are resolved.
    """
    resolution_times = []
    for c in complaints:
        # Only evaluate complaints marked Resolved with both timestamps available
        if c.get("status") == "Resolved":
            created_at = c.get("created_at")
            updated_at = c.get("updated_at")
            if created_at and updated_at:
                diff_hours = (updated_at - created_at).total_seconds() / 3600.0
                if diff_hours >= 0:
                    resolution_times.append(diff_hours)

    if not resolution_times:
        return None

    avg_hours = sum(resolution_times) / len(resolution_times)
    return round(avg_hours, 1)


def build_summary_report(complaints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate all analytics metrics into a single summary report dictionary.
    """
    return {
        "total": len(complaints),
        "by_status": count_by_status(complaints),
        "by_category": count_by_category(complaints),
        "by_area": group_by_area(complaints),
        "avg_resolution_hours": calculate_avg_resolution_hours(complaints),
    }
