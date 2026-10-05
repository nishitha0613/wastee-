"""Automated test script for waste collection request system.

Verifies:
1. User login and waste identification
2. Creating collection request referencing WasteReport (deriving waste_type)
3. Initial status validation (status == "submitted")
4. Retrieval of user collection requests list (newest first)
5. Retrieval of single collection request
6. Cross-user collection request access rejection (403 Forbidden)
7. Rejection of collection request referencing another user's report (403 Forbidden)
8. Rejection of duplicate collection request for same report (400 Bad Request)
9. Successful cancellation of a submitted request (DELETE /api/collection-requests/{id})
10. Rejection of cancellation when status has transitioned (e.g. accepted/scheduled)
"""
import io
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db
from app.models.collection_request import CollectionRequest, CollectionStatus
from app.models.waste_report import WasteReport
from app.seed_admin import seed_admin

client = TestClient(app)

TINY_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00"
    b"\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
)


def get_token_for(email: str, password: str, name: str = "Test User") -> str:
    client.post("/api/auth/register", json={"name": name, "email": email, "password": password})
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


def run_tests():
    print("=" * 65)
    print("RUNNING COLLECTION REQUEST SYSTEM TESTS")
    print("=" * 65)

    init_db()
    seed_admin()

    # Authenticate two users
    token_a = get_token_for("user_alpha@example.com", "PasswordAlpha123!", "Alpha User")
    token_b = get_token_for("user_beta@example.com", "PasswordBeta123!", "Beta User")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. User Alpha identifies waste (e-waste)
    file_payload = {
        "file": ("laptop_battery_ewaste.png", io.BytesIO(TINY_PNG_BYTES), "image/png"),
    }
    id_res = client.post("/api/waste/identify", headers=headers_a, files=file_payload)
    assert id_res.status_code == 201
    report_a_id = id_res.json()["id"]
    detected_type = id_res.json()["waste_type"]
    print(f"[1] PASSED: User Alpha created WasteReport #{report_a_id} ({detected_type})")

    # 2. User Alpha creates collection request referencing report (without manually providing waste_type)
    req_payload = {
        "waste_report_id": report_a_id,
        "quantity": "2 items",
        "location": "Flat 401, Green Heights, 12th Main Indiranagar, Bangalore",
        "additional_notes": "Call before arrival, gate code 9988",
    }
    create_res = client.post("/api/collection-requests", headers=headers_a, json=req_payload)
    assert create_res.status_code == 201, f"Create collection failed: {create_res.text}"
    req_data = create_res.json()
    req_id = req_data["id"]

    # 3. Verify fields & initial status
    assert req_data["waste_report_id"] == report_a_id
    assert req_data["waste_type"] == detected_type, "waste_type should be derived from WasteReport"
    assert req_data["status"] == "submitted", "Initial status must be 'submitted'"
    assert req_data["location"] == req_payload["location"]
    print(f"[2] PASSED: Collection request #{req_id} created with derived type '{req_data['waste_type']}' and status 'submitted'")

    # 4. User Beta tries to request collection using User Alpha's report -> 403 Forbidden
    beta_cross_payload = {
        "waste_report_id": report_a_id,
        "location": "Some other place",
    }
    cross_report_res = client.post("/api/collection-requests", headers=headers_b, json=beta_cross_payload)
    assert cross_report_res.status_code == 403, f"Expected 403, got {cross_report_res.status_code}"
    print("[3] PASSED: User Beta forbidden (403) from referencing User Alpha's waste report")

    # 5. User Alpha tries to create another request for the same report -> 400 Bad Request
    dup_res = client.post("/api/collection-requests", headers=headers_a, json=req_payload)
    assert dup_res.status_code == 400, f"Expected 400 for duplicate request, got {dup_res.status_code}"
    print("[4] PASSED: Duplicate collection request for the same report rejected with 400 Bad Request")

    # 6. User Alpha gets request history (GET /api/collection-requests)
    list_res = client.get("/api/collection-requests", headers=headers_a)
    assert list_res.status_code == 200
    user_requests = list_res.json()
    assert len(user_requests) >= 1
    assert user_requests[0]["id"] == req_id
    print(f"[5] PASSED: User Alpha retrieved request history ({len(user_requests)} requests)")

    # 7. User Beta gets request history -> should NOT include User Alpha's request
    list_b_res = client.get("/api/collection-requests", headers=headers_b)
    assert list_b_res.status_code == 200
    b_ids = [r["id"] for r in list_b_res.json()]
    assert req_id not in b_ids
    print("[6] PASSED: User Beta history does not leak User Alpha's request")

    # 8. User Alpha gets single request
    single_res = client.get(f"/api/collection-requests/{req_id}", headers=headers_a)
    assert single_res.status_code == 200
    assert single_res.json()["id"] == req_id
    print(f"[7] PASSED: User Alpha fetched individual request #{req_id}")

    # 9. User Beta attempts to view User Alpha's request -> 403 Forbidden
    beta_view_res = client.get(f"/api/collection-requests/{req_id}", headers=headers_b)
    assert beta_view_res.status_code == 403, f"Expected 403, got {beta_view_res.status_code}"
    print("[8] PASSED: User Beta denied access (403 Forbidden) to User Alpha's request")

    # 10. User Alpha creates another collection request to test status transition rule
    file_payload2 = {
        "file": ("plastic_tray.png", io.BytesIO(TINY_PNG_BYTES), "image/png"),
    }
    id_res2 = client.post("/api/waste/identify", headers=headers_a, files=file_payload2)
    report_a_id_2 = id_res2.json()["id"]

    req_payload2 = {
        "waste_report_id": report_a_id_2,
        "quantity": "5 containers",
        "location": "MG Road Office, Suite 200",
    }
    create_res2 = client.post("/api/collection-requests", headers=headers_a, json=req_payload2)
    req_id_2 = create_res2.json()["id"]

    # Transition req_id_2 to "scheduled" directly in DB (simulating admin action)
    db = SessionLocal()
    try:
        db_req = db.query(CollectionRequest).filter(CollectionRequest.id == req_id_2).first()
        db_req.status = CollectionStatus.SCHEDULED.value
        db.commit()
    finally:
        db.close()

    # 11. User Alpha tries to cancel the scheduled request -> 400 Bad Request
    del_scheduled_res = client.delete(f"/api/collection-requests/{req_id_2}", headers=headers_a)
    assert del_scheduled_res.status_code == 400, f"Expected 400, got {del_scheduled_res.status_code}"
    assert "Only requests in 'submitted' status can be cancelled" in del_scheduled_res.json()["detail"]
    print("[9] PASSED: Cancellation correctly rejected (400 Bad Request) for request in 'scheduled' status")

    # 12. User Alpha cancels the first request which is still in 'submitted' status -> 200 OK
    del_submitted_res = client.delete(f"/api/collection-requests/{req_id}", headers=headers_a)
    assert del_submitted_res.status_code == 200
    assert del_submitted_res.json()["id"] == req_id
    print(f"[10] PASSED: User Alpha successfully cancelled submitted request #{req_id}")

    # 13. Getting the cancelled request returns 404
    get_deleted_res = client.get(f"/api/collection-requests/{req_id}", headers=headers_a)
    assert get_deleted_res.status_code == 404
    print("[11] PASSED: Cancelled request is no longer accessible (404 Not Found)")

    print("=" * 65)
    print("ALL 11 COLLECTION REQUEST SYSTEM TESTS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
