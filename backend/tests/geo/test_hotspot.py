"""
Unit tests for the grid-based hotspot detection algorithm.
Tests empty input, single cluster meeting threshold, cluster below threshold,
multiple clusters sorted by density, and dictionary structure of output.
"""

import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path so app modules can be imported
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import find_hotspots function
from app.geo.hotspot import find_hotspots


def test_find_hotspots_returns_empty_list_for_empty_complaints():
    """An empty complaint list must return an empty list of hotspots."""
    # Empty list of complaints
    complaints = []
    # Run hotspot algorithm
    hotspots = find_hotspots(complaints, cell_size=0.01, min_count=3)
    # Result must be empty list
    assert hotspots == []


def test_find_hotspots_returns_one_hotspot_when_three_complaints_are_in_same_cell():
    """Three complaints falling into the same cell produce one hotspot of count 3."""
    # Three complaints all located within the same 0.01-degree grid cell
    complaints = [
        {"lat": 28.631, "lon": 77.361},
        {"lat": 28.632, "lon": 77.362},
        {"lat": 28.634, "lon": 77.364},
    ]
    # Run hotspot algorithm with min_count of 3
    hotspots = find_hotspots(complaints, cell_size=0.01, min_count=3)
    # Exactly one hotspot should be identified
    assert len(hotspots) == 1
    # Count of complaints in this hotspot must be 3
    assert hotspots[0]["count"] == 3


def test_find_hotspots_returns_no_hotspots_when_complaint_count_is_below_minimum():
    """Two complaints in one cell should produce no hotspot when min_count is 3."""
    # Two complaints in the same grid cell
    complaints = [
        {"lat": 28.631, "lon": 77.361},
        {"lat": 28.632, "lon": 77.362},
    ]
    # min_count requires at least 3 complaints
    hotspots = find_hotspots(complaints, cell_size=0.01, min_count=3)
    # Below threshold, so no hotspot is reported
    assert hotspots == []


def test_find_hotspots_returns_two_separate_clusters_sorted_by_count_descending():
    """Two distinct clusters are returned sorted with the highest count first."""
    # Cluster A has 4 complaints, Cluster B has 3 complaints
    cluster_a = [
        {"lat": 28.631, "lon": 77.361},
        {"lat": 28.632, "lon": 77.362},
        {"lat": 28.633, "lon": 77.363},
        {"lat": 28.634, "lon": 77.364},
    ]
    cluster_b = [
        {"lat": 28.701, "lon": 77.451},
        {"lat": 28.702, "lon": 77.452},
        {"lat": 28.703, "lon": 77.453},
    ]
    complaints = cluster_a + cluster_b
    # Run hotspot algorithm with min_count = 3
    hotspots = find_hotspots(complaints, cell_size=0.01, min_count=3)
    # Should find exactly 2 hotspots
    assert len(hotspots) == 2
    # First hotspot must have higher count (4), second must have lower count (3)
    assert hotspots[0]["count"] == 4
    assert hotspots[1]["count"] == 3


def test_find_hotspots_each_hotspot_has_count_center_lat_and_center_lon():
    """Each hotspot dictionary must contain count, center_lat, and center_lon keys."""
    # Three complaints in one cell
    complaints = [
        {"lat": 28.631, "lon": 77.361},
        {"lat": 28.632, "lon": 77.362},
        {"lat": 28.633, "lon": 77.363},
    ]
    # Run hotspot algorithm
    hotspots = find_hotspots(complaints, cell_size=0.01, min_count=3)
    # Ensure one hotspot returned
    assert len(hotspots) == 1
    # Check that expected keys exist and match required structure
    hotspot = hotspots[0]
    assert "count" in hotspot
    assert "center_lat" in hotspot
    assert "center_lon" in hotspot
    assert set(hotspot.keys()) == {"count", "center_lat", "center_lon"}
