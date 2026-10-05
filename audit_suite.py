#!/usr/bin/env python3
"""
Comprehensive Final Audit Test Suite:
Executes:
  - Part 6: Complete User Test Flow
  - Part 7: Complete Admin Test Flow
  - Part 8: 13 Negative Security & Integrity Tests
Against the running FastAPI server.
"""

import sys
import json
import time
import io
import httpx
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def run_audit():
    client = httpx.Client(timeout=15.0)
    log(f"Connecting to live backend at {BASE_URL}...")

    # Verify Health
    res = client.get(f"{BASE_URL}/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    log("Health endpoint OK (GET /api/health)", "AUDIT-PASS")

    # =========================================================================
    # PART 6 — COMPLETE USER TEST
    # =========================================================================
    log("\n--- EXECUTING PART 6: COMPLETE USER TEST FLOW ---")
    timestamp = int(time.time() * 1000)
    user_email = f"user_{timestamp}@audit-ecocycle.org"
    user_password = "UserSecurePass123!"
    user_name = f"Audit Citizen {timestamp}"

    # 1. Register
    res = client.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": user_name, "email": user_email, "password": user_password},
    )
    assert res.status_code == 201, f"Registration failed: {res.text}"
    reg_data = res.json()
    assert reg_data["email"] == user_email
    user_id = reg_data["id"]
    log(f"User Registered: ID={user_id}, Email={user_email}", "AUDIT-PASS")

    # 2. Login
    res = client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": user_email, "password": user_password},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    user_token = res.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    log("User Logged in & received JWT", "AUDIT-PASS")

    # 3. Upload Waste & AI Identification
    img = Image.new("RGB", (256, 256), color=(45, 130, 240))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")

    files = {"file": ("plastic_water_bottle.jpg", img_byte_arr.getvalue(), "image/jpeg")}
    res = client.post(f"{BASE_URL}/api/waste/identify", files=files, headers=user_headers)
    assert res.status_code in [200, 201], f"Waste identification failed: {res.text}"
    waste_ident = res.json()
    waste_report_id = waste_ident["id"]
    waste_type = waste_ident["waste_type"]
    confidence = waste_ident["confidence"]
    guidance = waste_ident["guidance"]
    assert "disposal_method" in guidance
    assert "do" in guidance and len(guidance["do"]) > 0
    assert "dont" in guidance and len(guidance["dont"]) > 0
    log(f"Waste Uploaded & Identified: ID={waste_report_id}, Type='{waste_type}', Confidence={confidence}", "AUDIT-PASS")
    log(f"Disposal Guidance displayed: Method='{guidance['disposal_method']}'", "AUDIT-PASS")

    # 4. Request Collection
    res = client.post(
        f"{BASE_URL}/api/collection-requests",
        headers=user_headers,
        json={
            "waste_report_id": waste_report_id,
            "quantity": "Medium (2 bags)",
            "location": "Audit Sector 4, Civic Center Lane",
            "additional_notes": "Recyclable plastic containers cleaned and bagged",
        },
    )
    assert res.status_code == 201, f"Create collection request failed: {res.text}"
    col_req = res.json()
    request_id = col_req["id"]
    assert col_req["status"] == "submitted"
    log(f"Collection Requested: Request ID={request_id}, Status='{col_req['status']}'", "AUDIT-PASS")

    # 5. View Request in citizen dashboard
    res = client.get(f"{BASE_URL}/api/collection-requests/{request_id}", headers=user_headers)
    assert res.status_code == 200
    assert res.json()["id"] == request_id
    log(f"Viewed Request: ID={request_id}", "AUDIT-PASS")

    # =========================================================================
    # PART 7 — COMPLETE ADMIN TEST
    # =========================================================================
    log("\n--- EXECUTING PART 7: COMPLETE ADMIN TEST FLOW ---")
    # 1. Admin Login
    res = client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@ecocycle.com", "password": "Admin@Secure123!"},
    )
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    log("Admin Logged In successfully", "AUDIT-PASS")

    # 2. View Requests & Search/Filter
    res = client.get(
        f"{BASE_URL}/api/admin/collection-requests?status=submitted&search=Civic Center Lane",
        headers=admin_headers,
    )
    assert res.status_code == 200
    filtered_items = res.json()["items"]
    assert any(item["id"] == request_id for item in filtered_items)
    log(f"Admin Filtered & Searched Requests: found request #{request_id}", "AUDIT-PASS")

    # 3. Accept
    res = client.patch(f"{BASE_URL}/api/admin/collection-requests/{request_id}/accept", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "accepted"
    log(f"Admin Accepted Request #{request_id}", "AUDIT-PASS")

    # 4. Schedule
    scheduled_time = "2026-10-12T09:30:00Z"
    res = client.patch(
        f"{BASE_URL}/api/admin/collection-requests/{request_id}/schedule",
        headers=admin_headers,
        json={"scheduled_date": scheduled_time},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "scheduled"
    assert res.json()["scheduled_date"] is not None
    log(f"Admin Scheduled Request #{request_id} for {scheduled_time}", "AUDIT-PASS")

    # 5. Collect
    res = client.patch(f"{BASE_URL}/api/admin/collection-requests/{request_id}/collect", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "collected"
    log(f"Admin Marked Collected: Request #{request_id}", "AUDIT-PASS")

    # 6. Complete
    res = client.patch(f"{BASE_URL}/api/admin/collection-requests/{request_id}/complete", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "completed"
    assert res.json()["completed_at"] is not None
    log(f"Admin Marked Completed: Request #{request_id}", "AUDIT-PASS")

    # 7. View Analytics
    res = client.get(f"{BASE_URL}/api/admin/collection-requests/stats", headers=admin_headers)
    assert res.status_code == 200
    stats = res.json()
    assert "completed" in stats and stats["completed"] >= 1
    log(f"Admin Analytics Verified: {stats}", "AUDIT-PASS")

    # 8. User views updated status (Receive Notification & Verification)
    res = client.get(f"{BASE_URL}/api/collection-requests/{request_id}", headers=user_headers)
    assert res.status_code == 200
    final_req = res.json()
    assert final_req["status"] == "completed"
    assert final_req["completed_at"] is not None
    log(f"Citizen Verified Updated Final Status: '{final_req['status']}' at {final_req['completed_at']}", "AUDIT-PASS")

    # =========================================================================
    # PART 8 — NEGATIVE TESTING (13 Specific Tests)
    # =========================================================================
    log("\n--- EXECUTING PART 8: 13 NEGATIVE TESTS ---")

    # 1. Incorrect password
    res = client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": user_email, "password": "WrongPassword999!"},
    )
    assert res.status_code == 401, f"Expected 401 for wrong password, got {res.status_code}"
    log("1. Incorrect password rejected with 401 Unauthorized", "AUDIT-PASS")

    # 2. Invalid JWT
    res = client.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.signature"},
    )
    assert res.status_code == 401, f"Expected 401 for invalid JWT, got {res.status_code}"
    log("2. Invalid JWT rejected with 401 Unauthorized", "AUDIT-PASS")

    # 3. Unauthenticated API access
    res = client.get(f"{BASE_URL}/api/auth/me")
    assert res.status_code == 401, f"Expected 401 for missing auth token, got {res.status_code}"
    log("3. Unauthenticated API access rejected with 401 Unauthorized", "AUDIT-PASS")

    # 4. Normal user accessing admin APIs
    res = client.get(f"{BASE_URL}/api/admin/collection-requests", headers=user_headers)
    assert res.status_code == 403, f"Expected 403 for citizen accessing admin route, got {res.status_code}"
    log("4. Normal user blocked from admin APIs with 403 Forbidden", "AUDIT-PASS")

    # Create a secondary citizen to test IDOR isolation
    user2_email = f"user2_{timestamp}@audit-ecocycle.org"
    res = client.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": "Second Citizen", "email": user2_email, "password": user_password},
    )
    assert res.status_code == 201
    res = client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": user2_email, "password": user_password},
    )
    assert res.status_code == 200
    user2_token = res.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # 5. User accessing another user's report (IDOR)
    res = client.get(f"{BASE_URL}/api/waste/reports/{waste_report_id}", headers=user2_headers)
    assert res.status_code == 403, f"Expected 403 for IDOR report access, got {res.status_code}"
    log("5. Cross-user report access blocked with 403 Forbidden (IDOR Guard)", "AUDIT-PASS")

    # 6. User accessing another user's collection request (IDOR)
    res = client.get(f"{BASE_URL}/api/collection-requests/{request_id}", headers=user2_headers)
    assert res.status_code == 403, f"Expected 403 for IDOR collection request access, got {res.status_code}"
    log("6. Cross-user collection request access blocked with 403 Forbidden (IDOR Guard)", "AUDIT-PASS")

    # 7. Invalid image (corrupted / plain text)
    files = {"file": ("malicious.png", b"NOT AN IMAGE FILE AT ALL", "image/png")}
    res = client.post(f"{BASE_URL}/api/waste/identify", files=files, headers=user_headers)
    assert res.status_code == 400, f"Expected 400 for corrupted image, got {res.status_code}"
    log("7. Invalid/corrupted image rejected with 400 Bad Request", "AUDIT-PASS")

    # 8. Oversized image (> 5MB)
    big_file = b"X" * (6 * 1024 * 1024)
    files = {"file": ("giant.jpg", big_file, "image/jpeg")}
    res = client.post(f"{BASE_URL}/api/waste/identify", files=files, headers=user_headers)
    assert res.status_code in [400, 413], f"Expected 400/413 for oversized image, got {res.status_code}"
    log(f"8. Oversized image rejected with {res.status_code}", "AUDIT-PASS")

    # 9. Invalid IDs (negative / 0 / non-existent)
    res = client.get(f"{BASE_URL}/api/waste/reports/0", headers=user_headers)
    assert res.status_code in [400, 422], f"Expected 400/422 for ID=0, got {res.status_code}"
    res = client.get(f"{BASE_URL}/api/collection-requests/-5", headers=user_headers)
    assert res.status_code in [400, 422], f"Expected 400/422 for ID=-5, got {res.status_code}"
    res = client.get(f"{BASE_URL}/api/collection-requests/99999999", headers=admin_headers)
    assert res.status_code == 404, f"Expected 404 for non-existent ID, got {res.status_code}"
    log("9. Invalid IDs (0, negative, non-existent) properly rejected (400/404/422)", "AUDIT-PASS")

    # 10. Invalid status transitions (e.g. attempting to accept a completed request)
    res = client.patch(f"{BASE_URL}/api/admin/collection-requests/{request_id}/accept", headers=admin_headers)
    assert res.status_code == 400, f"Expected 400 for invalid transition, got {res.status_code}"
    log("10. Invalid status transition blocked with 400 Bad Request", "AUDIT-PASS")

    # 11. Malformed request (e.g. missing required fields in registration or collection)
    res = client.post(f"{BASE_URL}/api/auth/register", json={"email": "incomplete@example.com"})
    assert res.status_code == 422, f"Expected 422 for malformed payload, got {res.status_code}"
    log("11. Malformed request rejected with 422 Unprocessable Entity", "AUDIT-PASS")

    # 12. Invalid pagination (page=0, limit=-1)
    res = client.get(f"{BASE_URL}/api/collection-requests?page=0&limit=10", headers=user_headers)
    assert res.status_code == 422, f"Expected 422 for page=0, got {res.status_code}"
    res = client.get(f"{BASE_URL}/api/waste/reports?page=1&limit=9999", headers=user_headers)
    assert res.status_code == 422, f"Expected 422 for limit exceeding max, got {res.status_code}"
    log("12. Invalid pagination parameters rejected with 422 Unprocessable Entity", "AUDIT-PASS")

    # 13. Invalid filters (invalid date strings)
    res = client.get(
        f"{BASE_URL}/api/admin/collection-requests?from_date=NOT_A_DATE",
        headers=admin_headers,
    )
    assert res.status_code == 422, f"Expected 422 for invalid date filter, got {res.status_code}"
    log("13. Invalid date filter rejected with 422 Unprocessable Entity", "AUDIT-PASS")

    print("\n" + "=" * 60)
    print("FINAL AUDIT COMPLETE: 100% OF TESTS PASSED")
    print("=" * 60)

if __name__ == "__main__":
    run_audit()
