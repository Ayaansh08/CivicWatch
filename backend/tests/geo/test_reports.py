"""
Tests for geospatial analytics and summary reports endpoints and calculations.
"""
from datetime import datetime, timedelta


def test_reports_counts_per_status_and_category(
    officer_client, insert_complaint, test_category, second_category
):
    """Report summary returns correct breakdown by status and category."""
    # Insert 2 Submitted Potholes and 1 In Progress Garbage
    insert_complaint(
        28.62, 77.36, title="P1", category_id=test_category.id, status="Submitted"
    )
    insert_complaint(
        28.63, 77.37, title="P2", category_id=test_category.id, status="Submitted"
    )
    insert_complaint(
        28.64, 77.38, title="G1", category_id=second_category.id, status="In Progress"
    )

    response = officer_client.get("/geo/reports/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3

    # Check status distribution
    status_map = {item["status"]: item["count"] for item in data["by_status"]}
    assert status_map.get("Submitted") == 2
    assert status_map.get("In Progress") == 1

    # Check category distribution
    category_map = {item["category"]: item["count"] for item in data["by_category"]}
    assert category_map.get(test_category.name) == 2
    assert category_map.get(second_category.name) == 1


def test_reports_area_grouping(officer_client, insert_complaint, test_category):
    """Complaints are grouped into 0.01 grid cells labeled by lower-left corner."""
    # 2 complaints in cell starting at 28.62, 77.36
    insert_complaint(28.621, 77.361, title="A1", category_id=test_category.id)
    insert_complaint(28.625, 77.365, title="A2", category_id=test_category.id)

    response = officer_client.get("/geo/reports/summary")

    assert response.status_code == 200
    data = response.json()
    areas = data["by_area"]
    assert len(areas) >= 1
    assert areas[0]["area"] == "28.62,77.36"
    assert areas[0]["count"] == 2


def test_reports_average_resolution_time_for_resolved_complaints(
    officer_client, insert_complaint, test_category
):
    """Average resolution time is computed in hours for resolved complaints."""
    start_time = datetime(2026, 11, 1, 10, 0, 0)
    end_time = start_time + timedelta(hours=12)

    insert_complaint(
        28.62,
        77.36,
        title="Resolved Pothole",
        category_id=test_category.id,
        status="Resolved",
        created_at=start_time,
        updated_at=end_time,
    )

    response = officer_client.get("/geo/reports/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["avg_resolution_hours"] == 12.0


def test_reports_average_resolution_time_is_null_when_none_resolved(
    officer_client, insert_complaint
):
    """avg_resolution_hours is null when no complaints have reached Resolved status."""
    insert_complaint(28.62, 77.36, title="Pending Issue", status="Submitted")

    response = officer_client.get("/geo/reports/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["avg_resolution_hours"] is None


def test_reports_empty_database_gives_zeros(officer_client):
    """An empty database returns zeros, empty arrays, and null resolution time."""
    response = officer_client.get("/geo/reports/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["by_status"] == []
    assert data["by_category"] == []
    assert data["by_area"] == []
    assert data["avg_resolution_hours"] is None


def test_reports_citizen_returns_403(authenticated_client):
    """Citizen user access to /geo/reports/summary returns 403 Forbidden."""
    response = authenticated_client.get("/geo/reports/summary")

    assert response.status_code == 403
    assert "You do not have permission to do this" in response.json()["detail"]


def test_reports_without_token_returns_401(plain_client):
    """Unauthenticated access to /geo/reports/summary returns 401 Unauthorized."""
    response = plain_client.get("/geo/reports/summary")

    assert response.status_code == 401
