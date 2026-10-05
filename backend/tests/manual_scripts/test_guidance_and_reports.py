"""Automated test script for disposal guidance and waste reports APIs.

Verifies:
1. Waste identification returns structured disposal guidance
2. Guidance is persisted in database
3. User report history (GET /api/waste/reports)
4. Single report retrieval (GET /api/waste/reports/{id})
5. Cross-user access rejection (403 Forbidden)
6. Cross-user deletion rejection (403 Forbidden)
7. Owner report deletion & disk image cleanup (DELETE /api/waste/reports/{id})
8. Admin access to report
"""
import io
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.models.user import User
from app.models.waste_report import WasteReport
from app.seed_admin import seed_admin

client = TestClient(app)
settings = get_settings()

TINY_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00"
    b"\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
)


def get_token_for(email: str, password: str, name: str = "Test User") -> str:
    # Register if not exists
    client.post("/api/auth/register", json={"name": name, "email": email, "password": password})
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


def run_tests():
    print("=" * 65)
    print("RUNNING DISPOSAL GUIDANCE & WASTE REPORTS TESTS")
    print("=" * 65)

    init_db()
    seed_admin()

    # Create two users: User A and User B
    token_a = get_token_for("user_a@example.com", "PasswordA123!", "User Alpha")
    token_b = get_token_for("user_b@example.com", "PasswordB123!", "User Beta")
    admin_token = client.post(
        "/api/auth/login",
        json={"email": "admin@ecocycle.com", "password": "Admin@Secure123!"},
    ).json()["access_token"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # 1. User A identifies a plastic bottle
    file_payload = {
        "file": ("plastic_bottle.png", io.BytesIO(TINY_PNG_BYTES), "image/png"),
    }
    identify_res = client.post("/api/waste/identify", headers=headers_a, files=file_payload)
    assert identify_res.status_code == 201, f"Identify failed: {identify_res.text}"
    data = identify_res.json()
    report_a_id = data["id"]
    guidance = data.get("guidance")

    # 2. Verify guidance is returned
    assert guidance is not None, "Guidance missing from identify response"
    assert "disposal_method" in guidance
    assert len(guidance["do"]) > 0
    assert len(guidance["dont"]) > 0
    assert "recyclable" in guidance
    assert "collection_recommended" in guidance
    print(f"[1] PASSED: Guidance returned for {data['waste_type']}: {guidance['disposal_method'][:50]}...")

    # 3. Verify guidance is stored in database
    db = SessionLocal()
    try:
        db_report = db.query(WasteReport).filter(WasteReport.id == report_a_id).first()
        assert db_report is not None
        assert db_report.disposal_guidance is not None
        assert "disposal_method" in db_report.disposal_guidance
        print(f"[2] PASSED: Guidance persisted in SQLite for report #{report_a_id}")
    finally:
        db.close()

    # 4. User A identifies a second item (e-waste)
    file_payload2 = {
        "file": ("phone_ewaste.png", io.BytesIO(TINY_PNG_BYTES), "image/png"),
    }
    identify_res2 = client.post("/api/waste/identify", headers=headers_a, files=file_payload2)
    assert identify_res2.status_code == 201
    report_a_id_2 = identify_res2.json()["id"]

    # 5. User A gets reports history (GET /api/waste/reports)
    history_res = client.get("/api/waste/reports", headers=headers_a)
    assert history_res.status_code == 200
    reports_a = history_res.json()
    assert len(reports_a) >= 2
    # Verify guidance is deserialized in history
    assert reports_a[0]["guidance"] is not None
    print(f"[3] PASSED: User A retrieved history ({len(reports_a)} reports) with deserialized guidance")

    # 6. User B gets reports history (should NOT include User A's reports)
    history_b_res = client.get("/api/waste/reports", headers=headers_b)
    assert history_b_res.status_code == 200
    b_report_ids = [r["id"] for r in history_b_res.json()]
    assert report_a_id not in b_report_ids
    assert report_a_id_2 not in b_report_ids
    print("[4] PASSED: User B history does not leak User A reports")

    # 7. User A gets single report
    single_res = client.get(f"/api/waste/reports/{report_a_id}", headers=headers_a)
    assert single_res.status_code == 200
    assert single_res.json()["id"] == report_a_id
    assert single_res.json()["guidance"]["disposal_method"] is not None
    print(f"[5] PASSED: User A retrieved single report #{report_a_id}")

    # 8. User B attempts to access User A's report -> 403 Forbidden
    cross_res = client.get(f"/api/waste/reports/{report_a_id}", headers=headers_b)
    assert cross_res.status_code == 403, f"Expected 403, got {cross_res.status_code}"
    print("[6] PASSED: User B denied access (403 Forbidden) to User A's report")

    # 9. Admin can access User A's report
    admin_access_res = client.get(f"/api/waste/reports/{report_a_id}", headers=headers_admin)
    assert admin_access_res.status_code == 200
    print(f"[7] PASSED: Admin successfully accessed report #{report_a_id}")

    # 10. User B attempts to delete User A's report -> 403 Forbidden
    del_forbidden = client.delete(f"/api/waste/reports/{report_a_id}", headers=headers_b)
    assert del_forbidden.status_code == 403
    print("[8] PASSED: User B denied deletion (403 Forbidden) of User A's report")

    # 11. User A deletes own report -> verify 200 OK and file cleanup
    image_rel_path = data["image_path"]
    filename = Path(image_rel_path).name
    disk_file = settings.upload_path / filename
    assert disk_file.exists(), "Image file should exist on disk before deletion"

    del_res = client.delete(f"/api/waste/reports/{report_a_id}", headers=headers_a)
    assert del_res.status_code == 200
    assert del_res.json()["id"] == report_a_id
    assert not disk_file.exists(), "Image file should be unlinked from disk after report deletion"
    print(f"[9] PASSED: Report #{report_a_id} deleted and image file unlinked from disk")

    # 12. Fetching deleted report returns 404
    get_deleted = client.get(f"/api/waste/reports/{report_a_id}", headers=headers_a)
    assert get_deleted.status_code == 404
    print("[10] PASSED: Accessing deleted report returns 404 Not Found")

    # 13. Unauthenticated request to /api/waste/reports -> 401 Unauthorized
    unauth_res = client.get("/api/waste/reports")
    assert unauth_res.status_code == 401
    print("[11] PASSED: Unauthenticated access rejected with 401 Unauthorized")

    print("=" * 65)
    print("ALL 11 GUIDANCE & REPORT TESTS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
