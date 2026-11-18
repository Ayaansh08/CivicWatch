"""
Unit and integration tests for complaint density calculation and heatmap endpoint.
"""
from backend.app.geo.density import build_density


def test_build_density_groups_points_into_cells():
    """Points in the same 0.002 grid cell are grouped together into one count."""
    # Two points inside the same 0.002 cell [28.620 - 28.622, 77.360 - 77.362]
    points = [
        {"lat": 28.6201, "lon": 77.3601},
        {"lat": 28.6205, "lon": 77.3608},
        {"lat": 28.6300, "lon": 77.3700},
    ]

    # Calculate density
    cells = build_density(points, cell_size=0.002)

    # Must produce 2 cells, first with count 2, second with count 1
    assert len(cells) == 2
    assert cells[0]["count"] == 2
    assert cells[1]["count"] == 1


def test_build_density_with_empty_list_gives_empty_list():
    """An empty input point list produces an empty density result."""
    assert build_density([]) == []


def test_build_density_results_are_sorted_by_count_descending():
    """Cells with highest complaint counts must appear first."""
    # 3 points in cell A, 1 point in cell B
    points = [
        {"lat": 28.6201, "lon": 77.3601},
        {"lat": 28.6202, "lon": 77.3602},
        {"lat": 28.6203, "lon": 77.3603},
        {"lat": 28.6300, "lon": 77.3700},
    ]

    cells = build_density(points, cell_size=0.002)

    # Highest count is first
    assert cells[0]["count"] == 3
    assert cells[1]["count"] == 1


def test_heatmap_endpoint_returns_cells_for_complaints_in_box(
    officer_client, insert_complaint
):
    """GET /geo/heatmap returns density cells for complaints inside the box."""
    # Insert 2 complaints in the same cell inside box
    insert_complaint(28.6201, 77.3601, title="Box Point 1")
    insert_complaint(28.6205, 77.3605, title="Box Point 2")

    # Fetch heatmap
    response = officer_client.get(
        "/geo/heatmap?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=77.38"
    )

    # Should return 200 with 1 cell having count 2
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["count"] == 2
    assert "lat" in data[0]
    assert "lon" in data[0]


def test_heatmap_endpoint_ignores_complaints_outside_box(
    officer_client, insert_complaint
):
    """Complaints located outside the bounding box are not counted in the heatmap."""
    # Insert one inside, one outside
    insert_complaint(28.62, 77.36, title="Inside Box")
    insert_complaint(28.80, 77.50, title="Outside Box")

    # Fetch heatmap
    response = officer_client.get(
        "/geo/heatmap?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=77.38"
    )

    # Only inside point counted
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["count"] == 1


def test_heatmap_endpoint_applies_category_and_status_filters(
    officer_client, insert_complaint, test_category
):
    """GET /geo/heatmap respects category_id and status filter parameters."""
    # Matching complaint
    insert_complaint(
        28.62, 77.36, title="Match", category_id=test_category.id, status="In Progress"
    )
    # Non-matching complaint
    insert_complaint(
        28.62, 77.36, title="No Match", category_id=test_category.id, status="Resolved"
    )

    # Fetch heatmap with status filter
    url = (
        f"/geo/heatmap?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=77.38"
        f"&category_id={test_category.id}&status=In Progress"
    )
    response = officer_client.get(url)

    # Only 1 matching complaint counted
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["count"] == 1


def test_heatmap_endpoint_returns_403_for_citizen_user(authenticated_client):
    """GET /geo/heatmap must return 403 Forbidden when called by a citizen."""
    # Citizen user attempts to access heatmap
    response = authenticated_client.get(
        "/geo/heatmap?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=77.38"
    )

    # Forbidden
    assert response.status_code == 403
    assert "You do not have permission to do this" in response.json()["detail"]


def test_heatmap_endpoint_without_token_returns_401(plain_client):
    """GET /geo/heatmap must return 401 Unauthorized when no token is supplied."""
    # Unauthenticated request
    response = plain_client.get(
        "/geo/heatmap?min_lat=28.60&min_lon=77.34&max_lat=28.64&max_lon=77.38"
    )

    # Unauthorized
    assert response.status_code == 401


def test_heatmap_endpoint_with_bad_box_returns_400(officer_client):
    """Bounding box where min_lat >= max_lat must return 400 Bad Request."""
    # Inverted latitude bounds
    response = officer_client.get(
        "/geo/heatmap?min_lat=28.70&min_lon=77.34&max_lat=28.60&max_lon=77.38"
    )

    # Bad request
    assert response.status_code == 400
    assert "min_lat must be less than max_lat" in response.json()["detail"]
