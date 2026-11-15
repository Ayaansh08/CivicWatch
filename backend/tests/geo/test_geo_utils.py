"""
Unit tests for geospatial utility functions.
Tests haversine distance calculation, bounding box generation,
point-in-bounding-box check, and coordinate validation.
"""

import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path so app modules can be imported
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import functions from geo_utils
from app.geo.geo_utils import (
    haversine_distance_km,
    bounding_box,
    is_within_bbox,
)


# --- Tests for haversine_distance_km ---

def test_haversine_distance_between_same_point_is_zero():
    """Haversine distance between a point and itself should be 0 km."""
    # Delhi coordinates
    lat = 28.6139
    lon = 77.2090
    # Calculate distance from the point to itself
    distance = haversine_distance_km(lat, lon, lat, lon)
    # The distance must be 0
    assert distance == 0.0


def test_haversine_distance_delhi_to_noida_is_about_twenty_km():
    """Haversine distance between Delhi and Noida should be roughly 20 km."""
    # Coordinates of Delhi and Noida
    delhi_lat, delhi_lon = 28.6139, 77.2090
    noida_lat, noida_lon = 28.5355, 77.3910
    # Calculate distance between Delhi and Noida
    distance = haversine_distance_km(delhi_lat, delhi_lon, noida_lat, noida_lon)
    # Distance should be about 20 km within a 2 km tolerance
    assert distance == pytest.approx(20.0, abs=2.0)


def test_haversine_distance_order_of_points_does_not_change_result():
    """Haversine distance from A to B should equal distance from B to A."""
    # Two test locations
    point_a = (28.6139, 77.2090)
    point_b = (28.5355, 77.3910)
    # Compute distance in both directions
    distance_ab = haversine_distance_km(point_a[0], point_a[1], point_b[0], point_b[1])
    distance_ba = haversine_distance_km(point_b[0], point_b[1], point_a[0], point_a[1])
    # Distances must be equal
    assert distance_ab == distance_ba


# --- Tests for bounding_box ---

def test_bounding_box_returns_four_tuple():
    """Bounding box returns a tuple of (min_lat, min_lon, max_lat, max_lon)."""
    # Create bounding box of 5 km around Delhi
    bbox = bounding_box(28.6139, 77.2090, 5.0)
    # Ensure it returns a tuple with exactly 4 elements
    assert isinstance(bbox, tuple)
    assert len(bbox) == 4


def test_bounding_box_min_coordinates_are_below_max_coordinates():
    """Bounding box min_lat < max_lat and min_lon < max_lon."""
    # Generate bounding box
    min_lat, min_lon, max_lat, max_lon = bounding_box(28.6139, 77.2090, 10.0)
    # Verify min is strictly less than max for both latitude and longitude
    assert min_lat < max_lat
    assert min_lon < max_lon


def test_bounding_box_centre_point_lies_inside_the_box():
    """The center point used to create the bounding box must lie inside it."""
    # Define center point
    center_lat = 28.6139
    center_lon = 77.2090
    # Generate 5 km bounding box
    min_lat, min_lon, max_lat, max_lon = bounding_box(center_lat, center_lon, 5.0)
    # Center point must be inside the bounding limits
    assert min_lat <= center_lat <= max_lat
    assert min_lon <= center_lon <= max_lon


def test_bounding_box_bigger_radius_gives_bigger_box():
    """A larger radius must produce a strictly larger bounding box."""
    # Create a small box and a larger box around the same point
    small_box = bounding_box(28.6139, 77.2090, 5.0)
    large_box = bounding_box(28.6139, 77.2090, 15.0)
    # Compare latitude span
    small_lat_span = small_box[2] - small_box[0]
    large_lat_span = large_box[2] - large_box[0]
    # Large box span must be greater than small box span
    assert large_lat_span > small_lat_span


# --- Tests for is_within_bbox ---

def test_is_within_bbox_returns_true_for_point_inside():
    """is_within_bbox returns True when the point is strictly inside."""
    # Define a bounding box
    bbox = (28.0, 77.0, 29.0, 78.0)
    # Point inside the box
    assert is_within_bbox(28.5, 77.5, bbox) is True


def test_is_within_bbox_returns_false_for_point_outside():
    """is_within_bbox returns False when the point is outside."""
    # Define a bounding box
    bbox = (28.0, 77.0, 29.0, 78.0)
    # Point outside the box
    assert is_within_bbox(30.0, 77.5, bbox) is False


def test_is_within_bbox_returns_true_for_point_on_the_edge():
    """is_within_bbox returns True when the point is exactly on the bounding edge."""
    # Define a bounding box
    bbox = (28.0, 77.0, 29.0, 78.0)
    # Points lying exactly on edges
    assert is_within_bbox(28.0, 77.5, bbox) is True
    assert is_within_bbox(29.0, 77.5, bbox) is True
    assert is_within_bbox(28.5, 77.0, bbox) is True
    assert is_within_bbox(28.5, 78.0, bbox) is True


# --- Tests for invalid input (ValueError) ---

def test_haversine_distance_raises_value_error_for_invalid_latitude():
    """haversine_distance_km raises ValueError when latitude is outside -90 to 90."""
    # Latitude above 90 degrees
    with pytest.raises(ValueError):
        haversine_distance_km(95.0, 77.0, 28.0, 77.0)


def test_haversine_distance_raises_value_error_for_invalid_longitude():
    """haversine_distance_km raises ValueError when longitude is outside -180 to 180."""
    # Longitude above 180 degrees
    with pytest.raises(ValueError):
        haversine_distance_km(28.0, 185.0, 28.0, 77.0)


def test_bounding_box_raises_value_error_for_invalid_latitude():
    """bounding_box raises ValueError when center latitude is outside -90 to 90."""
    # Latitude below -90 degrees
    with pytest.raises(ValueError):
        bounding_box(-95.0, 77.0, 5.0)


def test_bounding_box_raises_value_error_for_invalid_longitude():
    """bounding_box raises ValueError when center longitude is outside -180 to 180."""
    # Longitude below -180 degrees
    with pytest.raises(ValueError):
        bounding_box(28.0, -185.0, 5.0)


def test_is_within_bbox_raises_value_error_for_invalid_coordinates():
    """is_within_bbox raises ValueError when point coordinates are out of valid range."""
    bbox = (28.0, 77.0, 29.0, 78.0)
    # Invalid latitude
    with pytest.raises(ValueError):
        is_within_bbox(95.0, 77.5, bbox)
    # Invalid longitude
    with pytest.raises(ValueError):
        is_within_bbox(28.5, 200.0, bbox)
