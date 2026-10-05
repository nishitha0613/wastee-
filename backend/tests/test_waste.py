"""
Waste Identification, Upload, & Report Test Suite
Covers:
- Valid image upload & automatic WasteReport creation
- File type validation (extension & MIME)
- Upload size limit enforcement (> 5 MB)
- Header magic byte & corrupted image rejection
- Waste classification & low-confidence handling
- Waste report retrieval & isolation
"""

import io
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.waste_report import WasteReport
from tests.conftest import make_test_image


def test_valid_image_upload_and_identification(client: TestClient, normal_user):
    """Verify valid image upload classifies waste, attaches guidance, and persists WasteReport."""
    img_bytes = make_test_image(format="JPEG", color=(46, 139, 87), size=(150, 150))
    files = {"file": ("apple_core.jpg", img_bytes, "image/jpeg")}

    response = client.post("/api/waste/identify", files=files, headers=normal_user["headers"])
    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert "waste_type" in data
    assert data["waste_type"] in ["Organic", "Plastic", "Paper", "Glass", "Metal", "E-Waste", "Hazardous", "Other"]
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert "guidance" in data
    assert data["guidance"] is not None
    assert "disposal_method" in data["guidance"]
    assert "image_path" in data


def test_invalid_file_extension(client: TestClient, normal_user):
    """Verify upload with unsupported extension is rejected with 400 Bad Request."""
    files = {"file": ("malicious.exe", b"fake binary payload", "application/octet-stream")}
    response = client.post("/api/waste/identify", files=files, headers=normal_user["headers"])
    assert response.status_code == 400
    assert "unsupported file extension" in response.json()["detail"].lower()


def test_invalid_mime_type(client: TestClient, normal_user):
    """Verify upload with invalid MIME type is rejected with 400 Bad Request."""
    files = {"file": ("document.png", b"fake data", "application/pdf")}
    response = client.post("/api/waste/identify", files=files, headers=normal_user["headers"])
    assert response.status_code == 400
    assert "unsupported mime type" in response.json()["detail"].lower()


def test_oversized_image_upload(client: TestClient, normal_user):
    """Verify image exceeding MAX_UPLOAD_SIZE is rejected with 413 Content Too Large."""
    # 6 MB payload (limit is 5 MB)
    oversized = b"\xff\xd8\xff" + (b"\x00" * (6 * 1024 * 1024))
    files = {"file": ("huge_image.jpg", oversized, "image/jpeg")}

    response = client.post("/api/waste/identify", files=files, headers=normal_user["headers"])
    assert response.status_code == 413
    assert "exceeds the limit" in response.json()["detail"].lower()


def test_corrupted_image_upload(client: TestClient, normal_user):
    """Verify image with valid headers but corrupted body is rejected with 400 Bad Request."""
    # JPEG magic bytes followed by truncated/garbage data
    corrupted_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 40
    files = {"file": ("corrupt.jpg", corrupted_bytes, "image/jpeg")}

    response = client.post("/api/waste/identify", files=files, headers=normal_user["headers"])
    assert response.status_code == 400
    assert "corrupted" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()


def test_disguised_text_file_rejected(client: TestClient, normal_user):
    """Verify non-image text file renamed to .png is rejected via magic byte checks."""
    text_content = b"This is just a text file disguised as PNG"
    files = {"file": ("fake.png", text_content, "image/png")}

    response = client.post("/api/waste/identify", files=files, headers=normal_user["headers"])
    assert response.status_code == 400
    assert "does not match a valid image format" in response.json()["detail"].lower()


def test_low_confidence_classification(client: TestClient, normal_user):
    """Verify solid/blank image triggers low confidence classification and routes to 'Other'."""
    # Completely uniform/solid white image (variance = 0)
    blank_bytes = make_test_image(format="JPEG", color=(255, 255, 255), size=(100, 100))
    files = {"file": ("blank_white.jpg", blank_bytes, "image/jpeg")}

    response = client.post("/api/waste/identify", files=files, headers=normal_user["headers"])
    assert response.status_code == 201
    data = response.json()

    assert data["waste_type"] == "Other"
    assert data["is_low_confidence"] is True
    assert data["message"] is not None


def test_get_user_waste_reports(client: TestClient, db_session: Session, normal_user):
    """Verify user can retrieve their waste report history."""
    report1 = WasteReport(
        user_id=normal_user["user"].id,
        image_path="/uploads/test1.jpg",
        waste_type="Paper",
        confidence=0.91,
        disposal_guidance="{}",
    )
    report2 = WasteReport(
        user_id=normal_user["user"].id,
        image_path="/uploads/test2.jpg",
        waste_type="Plastic",
        confidence=0.87,
        disposal_guidance="{}",
    )
    db_session.add_all([report1, report2])
    db_session.commit()

    response = client.get("/api/waste/reports", headers=normal_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] == 2
    reports = data["items"]
    assert len(reports) == 2
    report_ids = [r["id"] for r in reports]
    assert report1.id in report_ids
    assert report2.id in report_ids


def test_unauthorized_report_access(
    client: TestClient, db_session: Session, normal_user, second_user
):
    """Verify user cannot access another user's report by ID."""
    report = WasteReport(
        user_id=normal_user["user"].id,
        image_path="/uploads/test.jpg",
        waste_type="Hazardous",
        confidence=0.95,
        disposal_guidance="{}",
    )
    db_session.add(report)
    db_session.commit()

    response = client.get(f"/api/waste/reports/{report.id}", headers=second_user["headers"])
    assert response.status_code == 403


def test_invalid_report_id_handling(client: TestClient, normal_user):
    """Verify non-existent and negative report IDs are handled cleanly."""
    # Non-existent report -> 404
    r_404 = client.get("/api/waste/reports/999999", headers=normal_user["headers"])
    assert r_404.status_code == 404

    # Negative report ID -> 400
    r_400 = client.get("/api/waste/reports/-1", headers=normal_user["headers"])
    assert r_400.status_code == 400
