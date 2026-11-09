"""
Geospatial utility functions for CivicWatch.
Contains helper functions for distance calculation using the Haversine formula,
bounding box calculation, point-in-box verification, and coordinate validation.
"""

import math


def validate_coordinates(lat, lon):
    """
    Validate that latitude is between -90 and 90, and longitude is between -180 and 180.

    Takes:
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.

    Returns:
        None. Raises ValueError if coordinates are outside valid bounds.
    """
    # Check that latitude is within the valid range of -90 to 90 degrees
    if lat < -90.0 or lat > 90.0:
        raise ValueError(f"Latitude must be between -90 and 90 degrees. Got {lat}.")

    # Check that longitude is within the valid range of -180 to 180 degrees
    if lon < -180.0 or lon > 180.0:
        raise ValueError(f"Longitude must be between -180 and 180 degrees. Got {lon}.")


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.

    Takes:
        lat1 (float): Latitude of the first point in degrees.
        lon1 (float): Longitude of the first point in degrees.
        lat2 (float): Latitude of the second point in degrees.
        lon2 (float): Longitude of the second point in degrees.

    Returns:
        float: Distance between the two points in kilometers.
    """
    # Validate the first point coordinates
    validate_coordinates(lat1, lon1)

    # Validate the second point coordinates
    validate_coordinates(lat2, lon2)

    # If both points are identical, the distance is exactly zero
    if lat1 == lat2 and lon1 == lon2:
        return 0.0

    # Mean radius of the Earth in kilometers
    earth_radius_km = 6371.0

    # Convert the latitude difference from degrees to radians
    dlat = math.radians(lat2 - lat1)

    # Convert the longitude difference from degrees to radians
    dlon = math.radians(lon2 - lon1)

    # Convert the starting latitude from degrees to radians
    phi1 = math.radians(lat1)

    # Convert the ending latitude from degrees to radians
    phi2 = math.radians(lat2)

    # Calculate the square of half the chord length between the points
    a = (math.sin(dlat / 2.0) ** 2) + math.cos(phi1) * math.cos(phi2) * (math.sin(dlon / 2.0) ** 2)

    # Ensure value of a stays strictly within 0 and 1 to prevent math domain error
    a = min(1.0, max(0.0, a))

    # Calculate the angular distance in radians using the arctangent function
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    # Multiply angular distance by Earth's radius to get the final distance in kilometers
    distance_km = earth_radius_km * c

    return distance_km


def bounding_box(lat, lon, radius_km):
    """
    Compute a square bounding box around a center point for a given radius.

    Takes:
        lat (float): Center latitude in degrees.
        lon (float): Center longitude in degrees.
        radius_km (float): Search radius in kilometers.

    Returns:
        tuple: (min_lat, min_lon, max_lat, max_lon)
    """
    # Validate the center coordinates
    validate_coordinates(lat, lon)

    # Approximate kilometers in one degree of latitude
    km_per_lat_degree = 111.0

    # Calculate latitude change in degrees for the given radius
    delta_lat = radius_km / km_per_lat_degree

    # Calculate longitude change in degrees, adjusting for latitude distortion
    cos_lat = math.cos(math.radians(lat))
    # Avoid division by zero near the Earth poles
    if abs(cos_lat) < 1e-6:
        delta_lon = 180.0
    else:
        delta_lon = radius_km / (km_per_lat_degree * cos_lat)

    # Compute minimum and maximum latitude boundaries
    min_lat = lat - delta_lat
    max_lat = lat + delta_lat

    # Compute minimum and maximum longitude boundaries
    min_lon = lon - delta_lon
    max_lon = lon + delta_lon

    return (min_lat, min_lon, max_lat, max_lon)


def is_within_bbox(lat, lon, bbox):
    """
    Check whether a coordinate point lies inside or on the boundary of a bounding box.

    Takes:
        lat (float): Point latitude in degrees.
        lon (float): Point longitude in degrees.
        bbox (tuple): Bounding box as (min_lat, min_lon, max_lat, max_lon).

    Returns:
        bool: True if the point is inside or on the edge of the box, False otherwise.
    """
    # Validate the point coordinates
    validate_coordinates(lat, lon)

    # Unpack the bounding box coordinates
    min_lat, min_lon, max_lat, max_lon = bbox

    # Check if latitude is within bounds (inclusive for edges)
    lat_in_range = min_lat <= lat <= max_lat

    # Check if longitude is within bounds (inclusive for edges)
    lon_in_range = min_lon <= lon <= max_lon

    # Point is within bounding box if both latitude and longitude are within range
    return lat_in_range and lon_in_range
