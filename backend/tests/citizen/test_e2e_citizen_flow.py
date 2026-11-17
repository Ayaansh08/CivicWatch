"""End-to-end acceptance tests for the citizen workflow."""
import io
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.citizen.history import add_history
from backend.app.platform.models import Category, Complaint


@pytest.fixture
def real_auth_client(setup_test_db):
    """Client with no get_current_user override, using real JWT tokens."""
    return TestClient(app)


def test_citizen_end_to_end_journey(real_auth_client, db_session):
    """
    E2E journey for a citizen:
    1. Register citizen user
    2. Login and retrieve JWT Bearer token
    3. Seed category and fetch categories
    4. Submit a new complaint
    5. Upload a small PNG photo
    6. Check /complaints/mine shows 1 complaint with status 'Submitted'
    7. Check history has 1 entry ('Submitted')
    8. Simulate officer resolving complaint in DB and adding history
    9. Submit 5-star rating feedback
    10. Reopen complaint with reason
    11. Verify history sequence: Submitted -> Resolved -> Under Review
    """
    # 1. Register citizen user
    reg_res = real_auth_client.post("/auth/register", json={
        "name": "Citizen Ayan",
        "email": "ayan.citizen@example.com",
        "password": "strongPassword123",
    })
    assert reg_res.status_code == 201

    # 2. Login
    login_res = real_auth_client.post("/auth/login", json={
        "email": "ayan.citizen@example.com",
        "password": "strongPassword123",
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Seed category and get categories
    cat = Category(name="Roads & Transport")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    cat_id = cat.id

    cat_res = real_auth_client.get("/complaints/categories", headers=headers)
    assert cat_res.status_code == 200
    assert any(c["id"] == cat_id for c in cat_res.json())

    # 4. Submit complaint
    comp_res = real_auth_client.post("/complaints", headers=headers, json={
        "title": "Severe pothole at chowk",
        "description": "Risk of accidents for two-wheelers.",
        "category_id": cat_id,
        "latitude": 28.5355,
        "longitude": 77.3910,
    })
    assert comp_res.status_code == 201
    complaint_id = comp_res.json()["id"]

    # 5. Upload small PNG
    png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    files = {"file": ("pothole.png", io.BytesIO(png_data), "image/png")}
    upload_res = real_auth_client.post(
        f"/complaints/{complaint_id}/photo", headers=headers, files=files
    )
    assert upload_res.status_code == 200
    assert upload_res.json()["photo_path"].startswith("/uploads/")

    # 6. Mine shows 1 complaint
    mine_res = real_auth_client.get("/complaints/mine", headers=headers)
    assert mine_res.status_code == 200
    my_complaints = mine_res.json()
    assert len(my_complaints) == 1
    assert my_complaints[0]["title"] == "Severe pothole at chowk"
    assert my_complaints[0]["status"] == "Submitted"

    # 7. History has 1 row
    hist_res = real_auth_client.get(f"/complaints/{complaint_id}/history", headers=headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) == 1
    assert history[0]["status"] == "Submitted"

    # 8. Simulate authority resolving complaint
    comp = db_session.query(Complaint).filter(Complaint.id == complaint_id).first()
    comp.status = "Resolved"
    db_session.commit()
    add_history(
        db_session,
        complaint_id=complaint_id,
        status="Resolved",
        note="Pothole filled with asphalt",
    )

    # 9. Rate feedback
    fb_res = real_auth_client.post(f"/complaints/{complaint_id}/feedback", headers=headers, json={
        "rating": 5,
        "comment": "Quick and clean repair work"
    })
    assert fb_res.status_code == 200

    # 10. Reopen
    reopen_res = real_auth_client.post(f"/complaints/{complaint_id}/reopen", headers=headers, json={
        "reason": "Asphalt washed away by heavy rain next morning"
    })
    assert reopen_res.status_code == 200
    assert reopen_res.json()["status"] == "Under Review"

    # 11. Verify history order
    final_hist_res = real_auth_client.get(f"/complaints/{complaint_id}/history", headers=headers)
    assert final_hist_res.status_code == 200
    statuses = [h["status"] for h in final_hist_res.json()]
    assert statuses == ["Submitted", "Resolved", "Under Review"]


def test_second_user_isolation(real_auth_client, db_session):
    """A second registered user sees empty list and is blocked from user 1's complaint."""
    # User 1 registers and logs in
    real_auth_client.post("/auth/register", json={
        "name": "User One",
        "email": "user1@example.com",
        "password": "password123",
    })
    token1 = real_auth_client.post("/auth/login", json={
        "email": "user1@example.com",
        "password": "password123",
    }).json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Seed category
    cat = Category(name="Sanitation")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    cat_id = cat.id

    # User 1 creates complaint
    comp = real_auth_client.post("/complaints", headers=headers1, json={
        "title": "Garbage dump unattended",
        "description": "Foul smell in sector 22.",
        "category_id": cat_id,
    }).json()

    # User 2 registers and logs in
    real_auth_client.post("/auth/register", json={
        "name": "User Two",
        "email": "user2@example.com",
        "password": "password456",
    })
    token2 = real_auth_client.post("/auth/login", json={
        "email": "user2@example.com",
        "password": "password456",
    }).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 2 /mine is empty
    mine_res = real_auth_client.get("/complaints/mine", headers=headers2)
    assert mine_res.status_code == 200
    assert mine_res.json() == []

    # User 2 accessing User 1 history gets 403
    hist_res = real_auth_client.get(f"/complaints/{comp['id']}/history", headers=headers2)
    assert hist_res.status_code == 403
