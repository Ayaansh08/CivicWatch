"""Tests for creating complaints and listing complaint categories."""


def test_valid_complaint_is_created_for_logged_in_user(
    authenticated_client, test_user, test_category
):
    """A valid complaint should be saved with default status and priority."""
    payload = {
        "title": "Large pothole",
        "description": "There is a large pothole near the main road.",
        "category_id": test_category.id,
        "latitude": 28.6,
        "longitude": 77.2,
    }

    response = authenticated_client.post("/complaints", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Submitted"
    assert data["priority"] == "Medium"
    assert data["user_id"] == test_user.id


def test_short_title_returns_422(authenticated_client, test_category):
    """A title shorter than five characters should be rejected."""
    payload = {
        "title": "Road",
        "description": "A detailed complaint description.",
        "category_id": test_category.id,
    }

    response = authenticated_client.post("/complaints", json=payload)

    assert response.status_code == 422


def test_missing_description_returns_422(authenticated_client, test_category):
    """A complaint without a description should be rejected."""
    payload = {
        "title": "Broken streetlight",
        "category_id": test_category.id,
    }

    response = authenticated_client.post("/complaints", json=payload)

    assert response.status_code == 422


def test_latitude_outside_valid_range_returns_422(
    authenticated_client, test_category
):
    """Latitude greater than 90 should be rejected."""
    payload = {
        "title": "Road damage",
        "description": "The road is damaged.",
        "category_id": test_category.id,
        "latitude": 120,
        "longitude": 77.2,
    }

    response = authenticated_client.post("/complaints", json=payload)

    assert response.status_code == 422


def test_longitude_outside_valid_range_returns_422(
    authenticated_client, test_category
):
    """Longitude greater than 180 should be rejected."""
    payload = {
        "title": "Road damage",
        "description": "The road is damaged.",
        "category_id": test_category.id,
        "latitude": 28.6,
        "longitude": 200,
    }

    response = authenticated_client.post("/complaints", json=payload)

    assert response.status_code == 422


def test_unknown_category_returns_400(authenticated_client):
    """A complaint using an unknown category should return 400."""
    payload = {
        "title": "Road damage",
        "description": "The road is damaged.",
        "category_id": 9999,
    }

    response = authenticated_client.post("/complaints", json=payload)

    assert response.status_code == 400


def test_creating_complaint_without_token_returns_401(
    plain_client, test_category
):
    """A complaint request without authentication should return 401."""
    payload = {
        "title": "Road damage",
        "description": "The road is damaged.",
        "category_id": test_category.id,
    }

    response = plain_client.post("/complaints", json=payload)

    assert response.status_code == 401


def test_categories_endpoint_returns_category_names(
    authenticated_client, test_category
):
    """The categories endpoint should return available category names."""
    response = authenticated_client.get("/complaints/categories")

    assert response.status_code == 200
    assert test_category.name in str(response.json())
