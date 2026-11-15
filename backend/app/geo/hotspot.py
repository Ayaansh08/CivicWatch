"""
Hotspot detection module for CivicWatch.
Contains pure function algorithms to group complaints into spatial clusters
using a fixed-size square grid.
"""

import math


def find_hotspots(complaints, cell_size=0.01, min_count=3):
    """
    Identify density hotspots from a list of complaints using a grid-based clustering approach.

    This is a pure function with no database, file, or network access.

    Takes:
        complaints (list of dict): List of complaint dicts, each having 'lat' and 'lon' keys.
        cell_size (float): The width and height of each grid cell in degrees (default 0.01).
        min_count (int): Minimum number of complaints required to qualify as a hotspot (default 3).

    Returns:
        list of dict: Hotspots sorted by complaint count in descending order.
                      Each hotspot dict has keys: 'count', 'center_lat', 'center_lon'.
    """
    # Step 1: Initialize an empty dictionary to store complaint counts per cell
    cell_counts = {}

    # Step 2: Iterate through each complaint and assign it to a grid cell
    for complaint in complaints:
        # Extract latitude and longitude from the complaint dictionary
        lat = complaint["lat"]
        lon = complaint["lon"]

        # Calculate grid cell index along latitude using math.floor
        lat_index = math.floor(lat / cell_size)

        # Calculate grid cell index along longitude using math.floor
        lon_index = math.floor(lon / cell_size)

        # Use the (lat_index, lon_index) tuple as the dictionary key
        cell_key = (lat_index, lon_index)

        # Increment complaint count for this grid cell
        cell_counts[cell_key] = cell_counts.get(cell_key, 0) + 1

    # Step 3: Filter cells that meet or exceed the minimum count threshold
    hotspots = []
    for (lat_index, lon_index), count in cell_counts.items():
        # Only keep cells where complaint count is greater than or equal to min_count
        if count >= min_count:
            # Step 4: Compute the geographic center of the grid cell
            center_lat = round((lat_index + 0.5) * cell_size, 6)
            center_lon = round((lon_index + 0.5) * cell_size, 6)

            # Build hotspot summary dictionary
            hotspot = {
                "count": count,
                "center_lat": center_lat,
                "center_lon": center_lon,
            }
            hotspots.append(hotspot)

    # Step 5: Sort the hotspots by count in descending order (highest density first)
    hotspots.sort(key=lambda item: item["count"], reverse=True)

    # Step 6: Return the final list of hotspot dictionaries
    return hotspots
