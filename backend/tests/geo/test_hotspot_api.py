"""
Integration and unit tests for the GET /geo/hotspots endpoint and hotspot detection API.
"""


def test_hotspot_found_for_three_complaints_in_one_cell(
    officer_client, insert_complaint, test_category
):
    """A cluster of 3 complaints in the same cell meets min_count=3 threshold."""
    # Insert 3 complaints within the same 0.01 grid cell (~1 km)
    insert_complaint(28.621, 77.361, title="H1", category_id=test_category.id)
    insert_complaint(28.622, 77.362, title="H2", category_id=test_category.id)
    insert_complaint(28.623, 77.363, title="H3", category_id=test_category.id)

    # Call /geo/hotspots with min_count=3
    response = officer_client.get("/geo/hotspots?cell_size=0.01&min_count=3")

    # Should detect 1 hotspot with count 3
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["count"] == 3


def test_no_hotspot_found_for_two_complaints_when_min_count_is_three(
    officer_client, insert_complaint, test_category
):
    """A cluster of only 2 complaints does not meet min_count=3 threshold."""
    # Insert 2 complaints
    insert_complaint(28.621, 77.361, title="H1", category_id=test_category.id)
    insert_complaint(28.622, 77.362, title="H2", category_id=test_category.id)

    # Call /geo/hotspots with min_count=3
    response = officer_client.get("/geo/hotspots?cell_size=0.01&min_count=3")

    # Should return empty list
    assert response.status_code == 200
    assert response.json() == []


def test_hotspots_are_sorted_by_count_descending(
    officer_client, insert_complaint, test_category
):
    """Hotspots must be returned in descending order of complaint density."""
    # Cell A has 4 complaints
    for i in range(4):
        insert_complaint(
            28.621 + i * 0.001, 77.361, title=f"A{i}", category_id=test_category.id
        )

    # Cell B has 3 complaints
    for i in range(3):
        insert_complaint(
            28.751 + i * 0.001, 77.451, title=f"B{i}", category_id=test_category.id
        )

    response = officer_client.get("/geo/hotspots?cell_size=0.01&min_count=3")

    # Cell A (count 4) must appear before Cell B (count 3)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["count"] == 4
    assert data[1]["count"] == 3


def test_most_common_category_is_correct(
    officer_client, insert_complaint, test_category, second_category
):
    """The hotspot's category field reflects the most frequent category in that cell."""
    # 2 Potholes (test_category) and 1 Garbage (second_category) in the same cell
    insert_complaint(28.621, 77.361, title="Pothole 1", category_id=test_category.id)
    insert_complaint(28.622, 77.362, title="Pothole 2", category_id=test_category.id)
    insert_complaint(28.623, 77.363, title="Garbage 1", category_id=second_category.id)

    response = officer_client.get("/geo/hotspots?cell_size=0.01&min_count=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == test_category.name


def test_hotspots_parameter_validation_returns_422(officer_client):
    """Invalid cell_size or min_count parameters must return 422."""
    # cell_size too large (> 0.1)
    res1 = officer_client.get("/geo/hotspots?cell_size=0.5&min_count=3")
    assert res1.status_code == 422

    # cell_size too small (< 0.001)
    res2 = officer_client.get("/geo/hotspots?cell_size=0.0001&min_count=3")
    assert res2.status_code == 422

    # min_count < 2
    res3 = officer_client.get("/geo/hotspots?cell_size=0.01&min_count=1")
    assert res3.status_code == 422


def test_hotspots_endpoint_returns_403_for_citizen(authenticated_client):
    """GET /geo/hotspots must return 403 Forbidden when accessed by a citizen."""
    response = authenticated_client.get("/geo/hotspots?cell_size=0.01&min_count=3")
    assert response.status_code == 403
    assert "You do not have permission to do this" in response.json()["detail"]


def test_hotspots_endpoint_without_token_returns_401(plain_client):
    """GET /geo/hotspots must return 401 Unauthorized without auth token."""
    response = plain_client.get("/geo/hotspots?cell_size=0.01&min_count=3")
    assert response.status_code == 401
