"""
Unit and integration tests for geo API endpoints.
Tests /geo/complaints/nearby and /geo/complaints/bbox for spatial filtering,
sorting, field schemas, boundary conditions, validation, and authentication.
"""


def test_nearby_returns_complaint_two_km_away_when_radius_is_five_km(
    authenticated_client, insert_complaint
):
    """Complaints within the specified radius should be returned."""
    # Insert a complaint ~2 km away from Noida center (28.62, 77.36)
    insert_complaint(28.638, 77.360, title="Near pothole")

    # Query with radius 5 km
    response = authenticated_client.get(
        "/geo/complaints/nearby?lat=28.62&lon=77.36&radius_km=5"
    )

    # Check status and response content
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Near pothole"


def test_nearby_does_not_return_complaint_thirty_km_away_when_radius_is_five_km(
    authenticated_client, insert_complaint
):
    """Complaints beyond the specified radius should be excluded."""
    # Insert a complaint ~30 km away
    insert_complaint(28.890, 77.360, title="Far pothole")

    # Query with radius 5 km
    response = authenticated_client.get(
        "/geo/complaints/nearby?lat=28.62&lon=77.36&radius_km=5"
    )

    # Far complaint must not be returned
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_nearby_results_are_sorted_nearest_first(
    authenticated_client, insert_complaint
):
    """Nearby results must be sorted with closest distance first."""
    # Insert complaint 4 km away, then 1 km away
    insert_complaint(28.656, 77.360, title="4 km away")
    insert_complaint(28.629, 77.360, title="1 km away")

    # Query within 10 km
    response = authenticated_client.get(
        "/geo/complaints/nearby?lat=28.62&lon=77.36&radius_km=10"
    )

    # Closest item must come first
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "1 km away"
    assert data[1]["title"] == "4 km away"
    assert data[0]["distance_km"] <= data[1]["distance_km"]


def test_nearby_item_has_all_expected_fields(
    authenticated_client, insert_complaint, test_category
):
    """Each nearby complaint item must contain all required geo and complaint fields."""
    # Insert a single complaint
    insert_complaint(28.638, 77.360, title="Detail Check")

    # Fetch nearby complaint
    response = authenticated_client.get(
        "/geo/complaints/nearby?lat=28.62&lon=77.36&radius_km=5"
    )

    # Assert all keys are present
    assert response.status_code == 200
    item = response.json()[0]
    expected_fields = [
        "id",
        "title",
        "category_name",
        "status",
        "priority",
        "latitude",
        "longitude",
        "distance_km",
    ]
    for field in expected_fields:
        assert field in item
    assert item["category_name"] == test_category.name
    assert isinstance(item["distance_km"], float)


def test_nearby_with_no_complaints_returns_empty_list(authenticated_client):
    """Querying nearby with no complaints in the database returns an empty list."""
    # Query without any complaints in database
    response = authenticated_client.get(
        "/geo/complaints/nearby?lat=28.62&lon=77.36&radius_km=5"
    )

    # Should return empty array with 200
    assert response.status_code == 200
    assert response.json() == []


def test_nearby_with_latitude_outside_range_returns_422(authenticated_client):
    """Latitude greater than 90 must trigger 422 validation error."""
    # Send latitude 120
    response = authenticated_client.get(
        "/geo/complaints/nearby?lat=120&lon=77.36&radius_km=5"
    )

    # Validation should reject invalid latitude
    assert response.status_code == 422


def test_nearby_with_radius_zero_returns_422(authenticated_client):
    """Radius of 0 km must trigger 422 validation error."""
    # Send radius_km 0
    response = authenticated_client.get(
        "/geo/complaints/nearby?lat=28.62&lon=77.36&radius_km=0"
    )

    # Validation should require radius > 0
    assert response.status_code == 422


def test_nearby_with_missing_parameter_returns_422(authenticated_client):
    """Omitting required query parameters must trigger 422 validation error."""
    # Send request without radius_km
    response = authenticated_client.get("/geo/complaints/nearby?lat=28.62&lon=77.36")

    # Missing parameter causes 422
    assert response.status_code == 422


def test_bbox_returns_only_complaints_inside_the_box(
    authenticated_client, insert_complaint
):
    """Bounding box query must return points inside and exclude points outside."""
    # Inside box [28.60, 77.34, 28.64, 77.38]
    insert_complaint(28.62, 77.36, title="Inside Box")
    # Outside box
    insert_complaint(28.70, 77.50, title="Outside Box")

    # Query bounding box
    response = authenticated_client.get(
        "/geo/complaints/bbox?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=77.38"
    )

    # Only inside complaint should be returned
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Inside Box"


def test_bbox_includes_complaint_exactly_on_the_box_edge(
    authenticated_client, insert_complaint
):
    """A complaint placed exactly on the bounding box edge must be included."""
    # Complaint exactly on the northern edge (lat 28.64)
    insert_complaint(28.64, 77.36, title="Edge Complaint")

    # Query box with max_lat 28.64
    response = authenticated_client.get(
        "/geo/complaints/bbox?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=77.38"
    )

    # Edge complaint is included
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Edge Complaint"


def test_bbox_with_min_lat_greater_than_max_lat_returns_400(
    authenticated_client,
):
    """Bounding box with min_lat greater than max_lat must return 400 Bad Request."""
    # Invalid box where min_lat (28.70) > max_lat (28.60)
    response = authenticated_client.get(
        "/geo/complaints/bbox?min_lat=28.70&min_lon=77.34&max_lat=28.60&max_lon=77.38"
    )

    # Should return 400 with descriptive error
    assert response.status_code == 400
    assert "min_lat must be less than max_lat" in response.json()["detail"]


def test_bbox_with_longitude_outside_range_returns_422(authenticated_client):
    """Longitude greater than 180 must trigger 422 validation error."""
    # Send longitude 200
    response = authenticated_client.get(
        "/geo/complaints/bbox?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=200"
    )

    # Validation rejects invalid longitude
    assert response.status_code == 422


def test_bbox_with_no_complaints_returns_empty_list(authenticated_client):
    """Bounding box query with no complaints returns an empty list."""
    # Query empty database
    response = authenticated_client.get(
        "/geo/complaints/bbox?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=77.38"
    )

    # Returns 200 and empty list
    assert response.status_code == 200
    assert response.json() == []


def test_nearby_endpoint_without_token_returns_401(plain_client):
    """GET /geo/complaints/nearby requires authentication and returns 401 without token."""
    # Call endpoint without auth header
    response = plain_client.get(
        "/geo/complaints/nearby?lat=28.62&lon=77.36&radius_km=5"
    )

    # Unauthenticated request returns 401
    assert response.status_code == 401


def test_bbox_endpoint_without_token_returns_401(plain_client):
    """GET /geo/complaints/bbox requires authentication and returns 401 without token."""
    # Call endpoint without auth header
    response = plain_client.get(
        "/geo/complaints/bbox?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=77.38"
    )

    # Unauthenticated request returns 401
    assert response.status_code == 401
