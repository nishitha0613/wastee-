"""
Comprehensive Hardening & End-to-End Test Suite for Smart Waste Assistant Backend.
Covers:
- TASK 11: Complete 16-step User -> AI Classification -> Collection -> Admin Lifecycle Workflow
- TASK 12: Negative Security & Robustness Tests
"""

import io
import time
from datetime import datetime, timedelta, timezone
import httpx
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def create_test_image(format="JPEG", color=(34, 139, 34), size=(200, 200)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def run_e2e_tests():
    print("=" * 60)
    print("RUNNING TASK 11: COMPLETE END-TO-END WORKFLOW (16 STEPS)")
    print("=" * 60)

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    ts = int(time.time())
    user_email = f"e2e_user_{ts}@ecocycle.test"
    user_password = "User@Password123!"

    # 1. Register User
    print("Step 1: Register User...")
    reg_resp = client.post(
        "/api/auth/register",
        json={"name": "End To End User", "email": user_email, "password": user_password},
    )
    assert reg_resp.status_code == 201, f"Reg failed: {reg_resp.text}"
    user_data = reg_resp.json()
    assert user_data["email"] == user_email
    assert user_data["role"] == "user"
    print("  ✓ User registered successfully:", user_email)

    # 2. Login User
    print("Step 2: Login User...")
    login_resp = client.post(
        "/api/auth/login",
        json={"email": user_email, "password": user_password},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token_data = login_resp.json()
    user_token = token_data["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    print("  ✓ User logged in successfully, JWT received.")

    # 3. Upload Waste Image
    print("Step 3: Upload waste image...")
    image_bytes = create_test_image(format="JPEG", color=(46, 139, 87), size=(300, 300))
    files = {"file": ("plant_waste.jpg", image_bytes, "image/jpeg")}
    upload_resp = client.post("/api/waste/identify", files=files, headers=user_headers)
    assert upload_resp.status_code == 201, f"Identify failed: {upload_resp.text}"
    ident_data = upload_resp.json()
    print("  ✓ Image uploaded successfully.")

    # 4. AI Identifies Waste
    print("Step 4: AI identifies waste...")
    identified_type = ident_data["waste_type"]
    confidence = ident_data["confidence"]
    print(f"  ✓ Identified Waste Type: {identified_type} (Confidence: {confidence:.2f})")
    assert identified_type in ["Organic", "Plastic", "Paper", "Glass", "Metal", "E-Waste", "Hazardous", "Other"]

    # 5. User receives disposal guidance
    print("Step 5: User receives disposal guidance...")
    guidance = ident_data.get("guidance")
    assert guidance is not None, "Guidance is missing"
    assert "disposal_method" in guidance or "do" in guidance
    print("  ✓ Disposal guidance received:", guidance.get("disposal_method"))

    # 6. Waste report is stored
    print("Step 6: Verify waste report is stored...")
    report_id = ident_data["id"]
    get_report_resp = client.get(f"/api/waste/reports/{report_id}", headers=user_headers)
    assert get_report_resp.status_code == 200, f"Get report failed: {get_report_resp.text}"
    report_data = get_report_resp.json()
    assert report_data["id"] == report_id
    assert report_data["user_id"] == user_data["id"]
    print(f"  ✓ Report #{report_id} verified in database.")

    # 7. User requests collection
    print("Step 7: User requests collection...")
    req_payload = {
        "waste_report_id": report_id,
        "quantity": "2 bags / 5 kg",
        "location": "456 Green Sanctuary Lane, Apt 3B",
        "additional_notes": "Please pick up by the side door entrance.",
    }
    col_resp = client.post("/api/collection-requests", json=req_payload, headers=user_headers)
    assert col_resp.status_code == 201, f"Collection request failed: {col_resp.text}"
    col_data = col_resp.json()
    request_id = col_data["id"]
    assert col_data["status"] == "submitted"
    assert col_data["waste_type"] == identified_type
    print(f"  ✓ Collection request #{request_id} created with status 'submitted'.")

    # 8. User views request status
    print("Step 8: User views request status...")
    user_req_resp = client.get(f"/api/collection-requests/{request_id}", headers=user_headers)
    assert user_req_resp.status_code == 200
    assert user_req_resp.json()["status"] == "submitted"
    print("  ✓ User sees request status as 'submitted'.")

    # 9. Admin logs in
    print("Step 9: Admin logs in...")
    admin_login_resp = client.post(
        "/api/auth/login",
        json={"email": "admin@ecocycle.com", "password": "Admin@Secure123!"},
    )
    assert admin_login_resp.status_code == 200, f"Admin login failed: {admin_login_resp.text}"
    admin_token = admin_login_resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("  ✓ Admin logged in successfully.")

    # 10. Admin views submitted request
    print("Step 10: Admin views submitted request...")
    admin_view_resp = client.get(f"/api/admin/collection-requests/{request_id}", headers=admin_headers)
    assert admin_view_resp.status_code == 200
    admin_view_data = admin_view_resp.json()
    assert admin_view_data["id"] == request_id
    assert admin_view_data["status"] == "submitted"
    assert "user" in admin_view_data
    assert admin_view_data["user"]["email"] == user_email
    print(f"  ✓ Admin found request #{request_id} from {user_email}.")

    # 11. Admin accepts it
    print("Step 11: Admin accepts request...")
    accept_resp = client.patch(
        f"/api/admin/collection-requests/{request_id}/accept",
        json={"notes": "Request verified and approved by admin."},
        headers=admin_headers,
    )
    assert accept_resp.status_code == 200, f"Accept failed: {accept_resp.text}"
    assert accept_resp.json()["status"] == "accepted"
    print("  ✓ Request status updated to 'accepted'.")

    # 12. Admin schedules collection
    print("Step 12: Admin schedules collection...")
    sched_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    sched_resp = client.patch(
        f"/api/admin/collection-requests/{request_id}/schedule",
        json={"scheduled_date": sched_time, "notes": "Scheduled for Thursday morning collection team."},
        headers=admin_headers,
    )
    assert sched_resp.status_code == 200, f"Schedule failed: {sched_resp.text}"
    assert sched_resp.json()["status"] == "scheduled"
    assert sched_resp.json()["scheduled_date"] is not None
    print(f"  ✓ Request status updated to 'scheduled' for {sched_time}.")

    # 13. Admin marks it collected
    print("Step 13: Admin marks it collected...")
    collect_resp = client.patch(
        f"/api/admin/collection-requests/{request_id}/collect",
        json={"notes": "Driver loaded 2 bags into green truck."},
        headers=admin_headers,
    )
    assert collect_resp.status_code == 200, f"Collect failed: {collect_resp.text}"
    assert collect_resp.json()["status"] == "collected"
    print("  ✓ Request status updated to 'collected'.")

    # 14. Admin completes it
    print("Step 14: Admin completes request...")
    comp_resp = client.patch(
        f"/api/admin/collection-requests/{request_id}/complete",
        json={"notes": "Delivered to city composting facility."},
        headers=admin_headers,
    )
    assert comp_resp.status_code == 200, f"Complete failed: {comp_resp.text}"
    completed_data = comp_resp.json()
    assert completed_data["status"] == "completed"
    print("  ✓ Request status updated to 'completed'.")

    # 15. Verify completed_at is stored
    print("Step 15: Verify completed_at is stored...")
    assert completed_data.get("completed_at") is not None
    print("  ✓ completed_at timestamp verified:", completed_data["completed_at"])

    # 16. Verify user sees the updated status
    print("Step 16: Verify user sees updated status...")
    user_final_view = client.get(f"/api/collection-requests/{request_id}", headers=user_headers)
    assert user_final_view.status_code == 200
    assert user_final_view.json()["status"] == "completed"
    assert user_final_view.json()["completed_at"] is not None
    print("  ✓ User sees request final status 'completed' with completion timestamp.")

    print("\n>>> ALL 16 E2E WORKFLOW STEPS PASSED SUCCESSFULLY! <<<\n")


def run_negative_tests():
    print("=" * 60)
    print("RUNNING TASK 12: NEGATIVE TESTING & ROBUSTNESS")
    print("=" * 60)

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    ts = int(time.time())
    user_a_email = f"user_a_{ts}@ecocycle.test"
    user_b_email = f"user_b_{ts}@ecocycle.test"
    pwd = "ValidPassword123!"

    # Create User A and User B
    client.post("/api/auth/register", json={"name": "User A", "email": user_a_email, "password": pwd})
    client.post("/api/auth/register", json={"name": "User B", "email": user_b_email, "password": pwd})

    token_a = client.post("/api/auth/login", json={"email": user_a_email, "password": pwd}).json()["access_token"]
    token_b = client.post("/api/auth/login", json={"email": user_b_email, "password": pwd}).json()["access_token"]

    admin_token = client.post(
        "/api/auth/login",
        json={"email": "admin@ecocycle.com", "password": "Admin@Secure123!"},
    ).json()["access_token"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # 1. Wrong Password (401)
    print("Negative Test 1: Wrong password -> 401")
    r = client.post("/api/auth/login", json={"email": user_a_email, "password": "WrongPassword999!"})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    assert "Invalid email or password" in r.text
    print("  ✓ Passed (401)")

    # 2. Expired / Invalid JWT (401)
    print("Negative Test 2: Expired or malformed JWT -> 401")
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.fake.token"})
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print("  ✓ Passed (401)")

    # 3. Unauthenticated protected endpoint (401)
    print("Negative Test 3: Unauthenticated protected endpoint -> 401")
    r = client.get("/api/auth/me")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    r = client.get("/api/collection-requests")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    print("  ✓ Passed (401)")

    # 4. Normal user accessing admin endpoint (403)
    print("Negative Test 4: Normal user accessing admin endpoints -> 403")
    r = client.get("/api/auth/admin-only", headers=headers_a)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    r = client.get("/api/admin/collection-requests", headers=headers_a)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    r = client.get("/api/admin/collection-requests/stats", headers=headers_a)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    print("  ✓ Passed (403)")

    # 5. User accessing another user's report (403)
    print("Negative Test 5: User B accessing User A's waste report -> 403")
    img_bytes = create_test_image()
    rep_a = client.post("/api/waste/identify", files={"file": ("test.jpg", img_bytes, "image/jpeg")}, headers=headers_a).json()
    rep_a_id = rep_a["id"]

    # User B tries to view User A's report
    r = client.get(f"/api/waste/reports/{rep_a_id}", headers=headers_b)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    # User B tries to delete User A's report
    r = client.delete(f"/api/waste/reports/{rep_a_id}", headers=headers_b)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    print("  ✓ Passed (403)")

    # 6. User accessing another user's collection request (403)
    print("Negative Test 6: User B accessing/cancelling User A's collection request -> 403")
    col_a = client.post(
        "/api/collection-requests",
        json={"waste_report_id": rep_a_id, "quantity": "1 item", "location": "123 Street A"},
        headers=headers_a,
    ).json()
    req_a_id = col_a["id"]

    # User B tries to view User A's collection request
    r = client.get(f"/api/collection-requests/{req_a_id}", headers=headers_b)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    # User B tries to cancel User A's collection request
    r = client.delete(f"/api/collection-requests/{req_a_id}", headers=headers_b)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    print("  ✓ Passed (403)")

    # User B tries to create collection request linking User A's report -> 403
    print("Negative Test 6b: User B linking User A's waste report -> 403")
    r = client.post(
        "/api/collection-requests",
        json={"waste_report_id": rep_a_id, "quantity": "1 item", "location": "User B house"},
        headers=headers_b,
    )
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    print("  ✓ Passed (403)")

    # 7. Invalid image (bad magic bytes / corrupted file) (400)
    print("Negative Test 7: Invalid image content (bad magic bytes or fake text file) -> 400")
    fake_png = b"THIS IS NOT A REAL PNG FILE AT ALL"
    r = client.post(
        "/api/waste/identify",
        files={"file": ("malicious.png", fake_png, "image/png")},
        headers=headers_a,
    )
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("  ✓ Passed (400)")

    # Corrupted JPEG (correct headers but corrupted payload) -> 400
    corrupted_jpg = b"\xff\xd8\xff\xe0" + b"\x00" * 50
    r = client.post(
        "/api/waste/identify",
        files={"file": ("corrupt.jpg", corrupted_jpg, "image/jpeg")},
        headers=headers_a,
    )
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("  ✓ Passed corrupted image detection (400)")

    # Disallowed extension (e.g. .exe / .sh) -> 400
    r = client.post(
        "/api/waste/identify",
        files={"file": ("exploit.sh", b"echo 'hack'", "text/x-shellscript")},
        headers=headers_a,
    )
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("  ✓ Passed disallowed extension rejection (400)")

    # 8. Oversized image (> 5MB) (413)
    print("Negative Test 8: Oversized image (> 5MB) -> 413")
    huge_data = b"\xff\xd8\xff" + (b"\x00" * (6 * 1024 * 1024))
    r = client.post(
        "/api/waste/identify",
        files={"file": ("huge.jpg", huge_data, "image/jpeg")},
        headers=headers_a,
    )
    assert r.status_code == 413, f"Expected 413, got {r.status_code}"
    print("  ✓ Passed (413 Content Too Large)")

    # 9. Invalid waste report ID (404 and negative 400)
    print("Negative Test 9: Invalid waste report ID -> 404 / 400")
    r = client.get("/api/waste/reports/999999", headers=headers_a)
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"
    r = client.get("/api/waste/reports/-5", headers=headers_a)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("  ✓ Passed (404 & 400)")

    # 10. Invalid collection request ID (404 and negative 400)
    print("Negative Test 10: Invalid collection request ID -> 404 / 400")
    r = client.get("/api/collection-requests/999999", headers=headers_a)
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"
    r = client.get("/api/collection-requests/-10", headers=headers_a)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("  ✓ Passed (404 & 400)")

    # 11. Invalid status transitions
    print("Negative Test 11: Invalid status transitions -> 400")
    # Fresh request in 'submitted' status
    col_fresh = client.post(
        "/api/collection-requests",
        json={"waste_type": "Plastic", "quantity": "1 box", "location": "Test Location 123"},
        headers=headers_a,
    ).json()
    fresh_id = col_fresh["id"]

    # submitted -> collected (INVALID: cannot skip accepted & scheduled)
    r = client.patch(f"/api/admin/collection-requests/{fresh_id}/collect", json={}, headers=headers_admin)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert "Invalid status transition" in r.text
    print("  ✓ submitted -> collected prevented (400)")

    # submitted -> completed (INVALID)
    r = client.patch(f"/api/admin/collection-requests/{fresh_id}/complete", json={}, headers=headers_admin)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("  ✓ submitted -> completed prevented (400)")

    # Normal user trying to change status -> 403
    r = client.patch(f"/api/admin/collection-requests/{fresh_id}/accept", json={}, headers=headers_a)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    print("  ✓ Normal user status change rejected (403)")

    # Accept it
    client.patch(f"/api/admin/collection-requests/{fresh_id}/accept", json={}, headers=headers_admin)
    # accepted -> completed (INVALID: must schedule first)
    r = client.patch(f"/api/admin/collection-requests/{fresh_id}/complete", json={}, headers=headers_admin)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("  ✓ accepted -> completed prevented (400)")

    # 12. Invalid scheduled date (past date) -> 422
    print("Negative Test 12: Scheduled date in past -> 422")
    past_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    r = client.patch(
        f"/api/admin/collection-requests/{fresh_id}/schedule",
        json={"scheduled_date": past_date},
        headers=headers_admin,
    )
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print("  ✓ Past scheduled date rejected (422)")

    # 13. Malformed request body / validation errors (422)
    print("Negative Test 13: Malformed request body -> 422")
    # Empty location
    r = client.post(
        "/api/collection-requests",
        json={"waste_type": "Paper", "quantity": "1 item", "location": "   "},
        headers=headers_a,
    )
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"

    # Missing required password in register
    r = client.post("/api/auth/register", json={"email": "bad@email.com", "name": "No Password"})
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"

    # Malformed email format
    r = client.post("/api/auth/register", json={"email": "not-an-email", "name": "Bad", "password": "pass"})
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print("  ✓ Malformed bodies and schema violations rejected cleanly (422)")

    # 14. Cancelling an already accepted request -> 400
    print("Negative Test 14: User cancelling already accepted request -> 400")
    r = client.delete(f"/api/collection-requests/{fresh_id}", headers=headers_a)
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("  ✓ Cancelling accepted request prevented (400)")

    print("\n>>> ALL NEGATIVE TESTS PASSED SUCCESSFULLY! <<<\n")


if __name__ == "__main__":
    run_e2e_tests()
    run_negative_tests()
    print("🎉 ALL TESTS PASSED WITH 100% SUCCESS!")
