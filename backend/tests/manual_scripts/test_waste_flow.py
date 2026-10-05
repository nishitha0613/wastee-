"""Automated test script for waste image upload, validation, classification, and report persistence.

Verifies:
1. Login & JWT acquisition
2. Valid image upload & classification (POST /api/waste/identify)
3. Persisted WasteReport record in database
4. Serving uploaded image via GET /uploads/<filename>
5. Invalid file type rejection (400 Bad Request)
6. Non-image file disguised as image rejection (400 Bad Request)
7. Oversized file rejection (> 5MB, 413 Payload Too Large)
8. Unauthenticated access rejection (401 Unauthorized)
"""
import io
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db
from app.models.waste_report import WasteReport, WasteType
from app.seed_admin import seed_admin

client = TestClient(app)

# 1x1 valid PNG image bytes
TINY_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00"
    b"\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
)

# 1x1 valid JPEG image bytes
TINY_JPEG_BYTES = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08"
    b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00"
    b"\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00"
    b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x80\xff\xd9"
)


def run_tests():
    print("=" * 65)
    print("RUNNING WASTE IDENTIFICATION & UPLOAD FLOW TESTS")
    print("=" * 65)

    # Ensure tables and initial admin
    init_db()
    seed_admin()

    # 1. Login to get JWT
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "admin@ecocycle.com", "password": "Admin@Secure123!"},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("[1] PASSED: Authenticated successfully and acquired Bearer token")

    # 2. Upload valid PNG image
    files = {
        "file": ("plastic_bottle.png", io.BytesIO(TINY_PNG_BYTES), "image/png"),
    }
    upload_resp = client.post(
        "/api/waste/identify",
        headers=auth_headers,
        files=files,
    )
    assert upload_resp.status_code == 201, f"Upload failed ({upload_resp.status_code}): {upload_resp.text}"
    data = upload_resp.json()
    assert "id" in data
    assert data["waste_type"] in [e.value for e in WasteType]
    assert data["confidence"] > 0.0
    assert data["image_path"].startswith("/uploads/")
    report_id = data["id"]
    image_rel_path = data["image_path"]
    print(
        f"[2] PASSED: Image uploaded & classified -> ID: {report_id}, "
        f"Type: {data['waste_type']}, Confidence: {data['confidence']}, Path: {image_rel_path}"
    )

    # 3. Verify WasteReport in database
    db = SessionLocal()
    try:
        report = db.query(WasteReport).filter(WasteReport.id == report_id).first()
        assert report is not None
        assert report.image_path == image_rel_path
        assert report.waste_type == data["waste_type"]
        print(f"[3] PASSED: WasteReport record #{report.id} verified in SQLite database")
    finally:
        db.close()

    # 4. Verify static serving of uploaded image
    static_resp = client.get(image_rel_path)
    assert static_resp.status_code == 200, f"Failed to fetch static image: {static_resp.status_code}"
    assert len(static_resp.content) == len(TINY_PNG_BYTES)
    print(f"[4] PASSED: Static image successfully retrieved from {image_rel_path}")

    # 5. Test invalid file extension / unsupported MIME type
    bad_file = {
        "file": ("document.txt", io.BytesIO(b"Hello waste management"), "text/plain"),
    }
    bad_resp = client.post(
        "/api/waste/identify",
        headers=auth_headers,
        files=bad_file,
    )
    assert bad_resp.status_code == 400, f"Expected 400, got {bad_resp.status_code}: {bad_resp.text}"
    print("[5] PASSED: Unsupported extension/mime rejected with 400 Bad Request")

    # 6. Test spoofed image (text content with .png extension)
    spoofed_file = {
        "file": ("fake_image.png", io.BytesIO(b"Not a real image file content"), "image/png"),
    }
    spoof_resp = client.post(
        "/api/waste/identify",
        headers=auth_headers,
        files=spoofed_file,
    )
    assert spoof_resp.status_code == 400, f"Expected 400 for spoofed image, got {spoof_resp.status_code}"
    assert "does not match a valid image" in spoof_resp.json()["detail"]
    print("[6] PASSED: Spoofed fake image correctly detected and rejected with 400 Bad Request")

    # 7. Test oversized file (> 5 MB)
    large_bytes = b"\x89PNG\r\n\x1a\n" + b"0" * (6 * 1024 * 1024)  # 6 MB
    large_file = {
        "file": ("huge_image.png", io.BytesIO(large_bytes), "image/png"),
    }
    large_resp = client.post(
        "/api/waste/identify",
        headers=auth_headers,
        files=large_file,
    )
    assert large_resp.status_code == 413, f"Expected 413, got {large_resp.status_code}: {large_resp.text}"
    print("[7] PASSED: Oversized file (>5MB) rejected with 413 Payload Too Large")

    # 8. Test unauthenticated request
    unauth_file = {
        "file": ("sample.png", io.BytesIO(TINY_PNG_BYTES), "image/png"),
    }
    unauth_resp = client.post(
        "/api/waste/identify",
        files=unauth_file,
    )
    assert unauth_resp.status_code == 401, f"Expected 401, got {unauth_resp.status_code}"
    print("[8] PASSED: Unauthenticated request rejected with 401 Unauthorized")

    print("=" * 65)
    print("ALL 8 WASTE IDENTIFICATION & UPLOAD TESTS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
