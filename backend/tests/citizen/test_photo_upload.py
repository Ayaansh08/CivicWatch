"""Tests for complaint photo upload endpoint."""
import io
from backend.app.citizen import router as citizen_router
from backend.app.platform.models import User, Complaint


def test_upload_valid_png_returns_200_and_sets_photo_path(
    authenticated_client, test_user, test_category, tmp_path, monkeypatch
):
    """Uploading a valid PNG should return 200 and update photo_path."""
    monkeypatch.setattr(citizen_router, "UPLOAD_DIR", str(tmp_path))

    # Create a complaint first
    res = authenticated_client.post("/complaints", json={
        "title": "Broken pipe on road",
        "description": "Water overflowing everywhere.",
        "category_id": test_category.id,
    })
    assert res.status_code == 201
    complaint_id = res.json()["id"]

    # Upload valid PNG
    file_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
    upload_res = authenticated_client.post(f"/complaints/{complaint_id}/photo", files=files)

    assert upload_res.status_code == 200
    data = upload_res.json()
    assert data["photo_path"] is not None
    assert data["photo_path"].startswith("/uploads/")
    assert data["photo_path"].endswith(".png")


def test_upload_txt_file_returns_400(
    authenticated_client, test_category, tmp_path, monkeypatch
):
    """Uploading a .txt file should return 400."""
    monkeypatch.setattr(citizen_router, "UPLOAD_DIR", str(tmp_path))

    res = authenticated_client.post("/complaints", json={
        "title": "Broken pipe on road",
        "description": "Water overflowing everywhere.",
        "category_id": test_category.id,
    })
    complaint_id = res.json()["id"]

    files = {"file": ("test.txt", io.BytesIO(b"hello text"), "text/plain")}
    upload_res = authenticated_client.post(f"/complaints/{complaint_id}/photo", files=files)
    assert upload_res.status_code == 400


def test_upload_file_over_2mb_returns_400(
    authenticated_client, test_category, tmp_path, monkeypatch
):
    """Uploading a file exceeding 2 MB should return 400."""
    monkeypatch.setattr(citizen_router, "UPLOAD_DIR", str(tmp_path))

    res = authenticated_client.post("/complaints", json={
        "title": "Broken pipe on road",
        "description": "Water overflowing everywhere.",
        "category_id": test_category.id,
    })
    complaint_id = res.json()["id"]

    large_content = b"a" * (2 * 1024 * 1024 + 10)
    files = {"file": ("large.png", io.BytesIO(large_content), "image/png")}
    upload_res = authenticated_client.post(f"/complaints/{complaint_id}/photo", files=files)
    assert upload_res.status_code == 400


def test_upload_by_other_user_returns_403(
    authenticated_client, other_authenticated_client, test_category, tmp_path, monkeypatch
):
    """Uploading a photo to another user's complaint should return 403."""
    monkeypatch.setattr(citizen_router, "UPLOAD_DIR", str(tmp_path))

    # User 1 creates complaint
    res = authenticated_client.post("/complaints", json={
        "title": "Broken pipe on road",
        "description": "Water overflowing everywhere.",
        "category_id": test_category.id,
    })
    complaint_id = res.json()["id"]

    # Other user attempts upload
    files = {"file": ("test.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")}
    client2 = other_authenticated_client()
    upload_res = client2.post(f"/complaints/{complaint_id}/photo", files=files)
    assert upload_res.status_code == 403


def test_upload_missing_complaint_returns_404(
    authenticated_client, tmp_path, monkeypatch
):
    """Uploading to a non-existent complaint id should return 404."""
    monkeypatch.setattr(citizen_router, "UPLOAD_DIR", str(tmp_path))

    files = {"file": ("test.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")}
    upload_res = authenticated_client.post("/complaints/99999/photo", files=files)
    assert upload_res.status_code == 404
