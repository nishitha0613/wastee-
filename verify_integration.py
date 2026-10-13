#!/usr/bin/env python3
"""
Full-Stack Verification Script for EcoCycle:
Tests backend deployment endpoints and full User & Admin flows against the running server.
"""

import sys
import json
import time
import httpx
import io
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def main():
    client = httpx.Client(timeout=15.0)
    log(f"Connecting to live backend at {BASE_URL}...")

    # 1. Health Endpoint
    res = client.get(f"{BASE_URL}/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    assert health_data.get("status") == "ok", f"Health status not ok: {health_data}"
    log(f"1. Health check passed: {health_data}", "SUCCESS")

    # 2. Citizen Registration
    timestamp = int(time.time())
    user_email = f"citizen_{timestamp}@ecocycle-demo.org"
    user_password = "CitizenPass123!"
    user_name = f"Citizen Demo {timestamp}"

    res = client.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": user_name, "email": user_email, "password": user_password},
    )
    assert res.status_code == 201, f"Registration failed: {res.text}"
    reg_data = res.json()
    assert "email" in reg_data and reg_data["email"] == user_email
    user_id = reg_data["id"]
    log(f"2. Citizen registered: ID={user_id}, Email={user_email}", "SUCCESS")

    # 3. Citizen Login
    res = client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": user_email, "password": user_password},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    login_data = res.json()
    assert "access_token" in login_data
    user_token = login_data["access_token"]
    log(f"3. Citizen logged in successfully: role={login_data['user']['role']}", "SUCCESS")

    # 4. Token validation / me endpoint
    user_headers = {"Authorization": f"Bearer {user_token}"}
    res = client.get(f"{BASE_URL}/api/auth/me", headers=user_headers)
    assert res.status_code == 200
    assert res.json()["email"] == user_email
    log("4. JWT token verified via /api/auth/me", "SUCCESS")

    # 5. Waste Identification (AI)
    # Generate a dummy test image
    img = Image.new("RGB", (256, 256), color=(40, 160, 60))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)

    files = {"file": ("test_plastic_bottle.jpg", img_byte_arr.getvalue(), "image/jpeg")}
    res = client.post(f"{BASE_URL}/api/waste/identify", files=files, headers=user_headers)
    assert res.status_code in [200, 201], f"Waste identification failed: {res.text}"
    waste_ident = res.json()
    assert "waste_type" in waste_ident
    assert "guidance" in waste_ident
    waste_type = waste_ident["waste_type"]
    log(f"5. AI Waste identification passed: type='{waste_type}', confidence={waste_ident.get('confidence')}", "SUCCESS")
    log(f"   Guidance: {waste_ident['guidance'].get('disposal_method')}")

    # 6. Verify Waste Report created during identification
    report_id = waste_ident["id"]
    res = client.get(f"{BASE_URL}/api/waste/reports/{report_id}", headers=user_headers)
    assert res.status_code == 200, f"Get waste report failed: {res.text}"
    report_data = res.json()
    assert report_data["id"] == report_id
    assert report_data["waste_type"] == waste_type
    log(f"6. Waste Report verified: ID={report_id}, Type={report_data['waste_type']}", "SUCCESS")

    # 7. Create Collection Request linked to report
    res = client.post(
        f"{BASE_URL}/api/collection-requests",
        headers=user_headers,
        json={
            "waste_report_id": report_id,
            "quantity": "Medium (2 bags)",
            "location": "North Campus Gate 4, Sector 7",
            "additional_notes": "Please collect before 5 PM",
        },
    )
    assert res.status_code == 201, f"Create collection request failed: {res.text}"
    col_req_data = res.json()
    request_id = col_req_data["id"]
    assert col_req_data["status"] == "submitted"
    assert col_req_data["waste_type"] == waste_type
    log(f"7. Collection Request created: ID={request_id}, Status={col_req_data['status']}", "SUCCESS")

    # 8. User Views their collection requests (with pagination)
    res = client.get(f"{BASE_URL}/api/collection-requests?page=1&limit=5", headers=user_headers)
    assert res.status_code == 200
    user_requests_page = res.json()
    assert any(item["id"] == request_id for item in user_requests_page["items"])
    log(f"8. User fetched collection requests: total={user_requests_page['total']}", "SUCCESS")

    # 9. Admin Login
    res = client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@ecocycle.com", "password": "Admin@Secure123!"},
    )
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    log("9. Admin logged in successfully", "SUCCESS")

    # 10. Admin Views and Filters Collection Requests
    res = client.get(
        f"{BASE_URL}/api/admin/collection-requests?status=submitted&search=North Campus",
        headers=admin_headers,
    )
    assert res.status_code == 200
    filtered = res.json()
    assert any(item["id"] == request_id for item in filtered["items"])
    log(f"10. Admin filtered & searched requests successfully (found request {request_id})", "SUCCESS")

    # 11. Admin Workflow: submitted -> accepted
    res = client.patch(
        f"{BASE_URL}/api/admin/collection-requests/{request_id}/accept",
        headers=admin_headers,
    )
    assert res.status_code == 200, f"Status update to accepted failed: {res.text}"
    assert res.json()["status"] == "accepted"
    log(f"11a. Admin updated request {request_id} -> 'accepted'", "SUCCESS")

    # 11b. accepted -> scheduled
    from datetime import datetime, timezone, timedelta
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    res = client.patch(
        f"{BASE_URL}/api/admin/collection-requests/{request_id}/schedule",
        headers=admin_headers,
        json={"scheduled_date": future_date},
    )
    assert res.status_code == 200, f"Status update to scheduled failed: {res.text}"
    assert res.json()["status"] == "scheduled"
    log(f"11b. Admin updated request {request_id} -> 'scheduled'", "SUCCESS")

    # 11c. scheduled -> collected
    res = client.patch(
        f"{BASE_URL}/api/admin/collection-requests/{request_id}/collect",
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "collected"
    log(f"11c. Admin updated request {request_id} -> 'collected'", "SUCCESS")

    # 11d. collected -> completed
    res = client.patch(
        f"{BASE_URL}/api/admin/collection-requests/{request_id}/complete",
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "completed"
    log(f"11d. Admin updated request {request_id} -> 'completed'", "SUCCESS")

    # 12. User verifies updated status
    res = client.get(f"{BASE_URL}/api/collection-requests/{request_id}", headers=user_headers)
    assert res.status_code == 200
    updated_req = res.json()
    assert updated_req["status"] == "completed"
    assert updated_req["completed_at"] is not None
    log(f"12. Citizen fetched updated request: Status={updated_req['status']}, CompletedAt={updated_req['completed_at']}", "SUCCESS")

    # 13. Admin Analytics / Statistics
    res = client.get(f"{BASE_URL}/api/admin/collection-requests/stats", headers=admin_headers)
    assert res.status_code == 200, f"Get stats failed: {res.text}"
    stats = res.json()
    assert "total" in stats or "completed" in stats or "submitted" in stats
    log(f"13. Admin statistics verified: {stats}", "SUCCESS")

    # 14. Error Handling Checks:
    # 14a: Non-admin trying to access admin endpoint
    res = client.get(f"{BASE_URL}/api/admin/collection-requests", headers=user_headers)
    assert res.status_code == 403, f"Expected 403 for citizen on admin route, got {res.status_code}"
    log("14a. Citizen blocked from admin endpoint (403 Forbidden)", "SUCCESS")

    # 14b: Unauthenticated request to protected route
    res = client.get(f"{BASE_URL}/api/auth/me")
    assert res.status_code == 401, f"Expected 401 for no token, got {res.status_code}"
    log("14b. Unauthenticated request rejected (401 Unauthorized)", "SUCCESS")

    # 14c: Invalid image upload (text file renamed as image)
    files = {"file": ("fake.png", b"this is plain text not an image", "image/png")}
    res = client.post(f"{BASE_URL}/api/waste/identify", files=files, headers=user_headers)
    assert res.status_code == 400, f"Expected 400 for corrupted image, got {res.status_code}"
    log("14c. Corrupted/disguised file upload rejected (400 Bad Request)", "SUCCESS")

    # 14d: Oversized file
    big_data = b"0" * (6 * 1024 * 1024)
    files = {"file": ("big.jpg", big_data, "image/jpeg")}
    res = client.post(f"{BASE_URL}/api/waste/identify", files=files, headers=user_headers)
    assert res.status_code in [400, 413], f"Expected 400 or 413 for oversized file, got {res.status_code}"
    log(f"14d. Oversized file upload rejected ({res.status_code})", "SUCCESS")

    print("\n========================================================")
    print("ALL PRODUCTION INTEGRATION AND FLOW TESTS PASSED (100%)")
    print("========================================================")

if __name__ == "__main__":
    main()
