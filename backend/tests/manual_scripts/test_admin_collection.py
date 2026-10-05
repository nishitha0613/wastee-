"""Automated test script for administrator collection management APIs.

Verifies:
1. Normal user rejection from admin endpoints (403 Forbidden)
2. Admin authentication & retrieval of all collection requests
3. Status filtering (?status=submitted)
4. Aggregate status statistics (GET /api/admin/collection-requests/stats)
5. Full collection lifecycle:
   submitted -> accepted -> scheduled -> collected -> completed
6. Automatic completed_at timestamp stamping
7. Rejection flow (submitted -> rejected) with optional reason
8. Invalid status transition rejections (400 Bad Request)
9. Unauthenticated access rejection (401 Unauthorized)
"""
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.seed_admin import seed_admin

client = TestClient(app)


def get_token(email: str, password: str, name: str = "User") -> str:
    client.post("/api/auth/register", json={"name": name, "email": email, "password": password})
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


def run_tests():
    print("=" * 65)
    print("RUNNING ADMIN COLLECTION MANAGEMENT TESTS")
    print("=" * 65)

    init_db()
    seed_admin()

    # Normal user token
    user_token = get_token("regular_citizen@example.com", "CitizenPass123!", "Citizen Jane")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Admin token
    admin_res = client.post(
        "/api/auth/login",
        json={"email": "admin@ecocycle.com", "password": "Admin@Secure123!"},
    )
    assert admin_res.status_code == 200
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Verify normal user is rejected from admin endpoints (403 Forbidden)
    r_unauth_user = client.get("/api/admin/collection-requests", headers=user_headers)
    assert r_unauth_user.status_code == 403, f"Expected 403, got {r_unauth_user.status_code}"
    print("[1] PASSED: Normal user rejected from admin endpoint with 403 Forbidden")

    # 2. Verify unauthenticated access (no token) is rejected with 401 Unauthorized
    r_no_auth = client.get("/api/admin/collection-requests")
    assert r_no_auth.status_code == 401
    print("[2] PASSED: Unauthenticated access rejected with 401 Unauthorized")

    # 3. Create sample collection requests as normal user for testing
    req1_payload = {
        "waste_type": "E-Waste",
        "quantity": "1 obsolete desktop tower",
        "location": "100 Innovation Park, Whitefield, Bangalore",
        "additional_notes": "Needs cart for transport",
    }
    create_res1 = client.post("/api/collection-requests", headers=user_headers, json=req1_payload)
    assert create_res1.status_code == 201
    req1_id = create_res1.json()["id"]

    req2_payload = {
        "waste_type": "Hazardous",
        "quantity": "2 battery packs",
        "location": "45 Central Street, Indiranagar, Bangalore",
    }
    create_res2 = client.post("/api/collection-requests", headers=user_headers, json=req2_payload)
    assert create_res2.status_code == 201
    req2_id = create_res2.json()["id"]

    print(f"[3] PASSED: Created test requests #{req1_id} and #{req2_id} (both status: 'submitted')")

    # 4. Admin lists all collection requests
    list_all_res = client.get("/api/admin/collection-requests", headers=admin_headers)
    assert list_all_res.status_code == 200
    all_requests = list_all_res.json()
    assert len(all_requests) >= 2
    # Verify user metadata is populated and no passwords exposed
    first_req = all_requests[0]
    assert "user" in first_req
    assert "password" not in first_req["user"] and "password_hash" not in first_req["user"]
    print(f"[4] PASSED: Admin retrieved all requests ({len(all_requests)} items) with safe user details")

    # 5. Admin filters by status=submitted
    filter_res = client.get("/api/admin/collection-requests?status=submitted", headers=admin_headers)
    assert filter_res.status_code == 200
    submitted_requests = filter_res.json()
    for req in submitted_requests:
        assert req["status"] == "submitted"
    print(f"[5] PASSED: Filtered requests by ?status=submitted ({len(submitted_requests)} found)")

    # 6. Admin views single request by ID
    single_res = client.get(f"/api/admin/collection-requests/{req1_id}", headers=admin_headers)
    assert single_res.status_code == 200
    assert single_res.json()["id"] == req1_id
    assert single_res.json()["user"]["email"] == "regular_citizen@example.com"
    print(f"[6] PASSED: Admin viewed single request #{req1_id} with full user details")

    # 7. Invalid transition test: submitted -> scheduled (must be accepted first)
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    invalid_sched_res = client.patch(
        f"/api/admin/collection-requests/{req1_id}/schedule",
        headers=admin_headers,
        json={"scheduled_date": future_date},
    )
    assert invalid_sched_res.status_code == 400
    assert "Invalid status transition" in invalid_sched_res.json()["detail"]
    print("[7] PASSED: Invalid transition (submitted -> scheduled) correctly rejected with 400 Bad Request")

    # 8. Accept request: submitted -> accepted
    accept_res = client.patch(f"/api/admin/collection-requests/{req1_id}/accept", headers=admin_headers)
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "accepted"
    print(f"[8] PASSED: Request #{req1_id} transitioned to 'accepted'")

    # 9. Schedule request: accepted -> scheduled
    sched_res = client.patch(
        f"/api/admin/collection-requests/{req1_id}/schedule",
        headers=admin_headers,
        json={"scheduled_date": future_date},
    )
    assert sched_res.status_code == 200
    assert sched_res.json()["status"] == "scheduled"
    assert sched_res.json()["scheduled_date"] is not None
    print(f"[9] PASSED: Request #{req1_id} scheduled for {future_date}")

    # 10. Mark collected: scheduled -> collected
    collect_res = client.patch(f"/api/admin/collection-requests/{req1_id}/collect", headers=admin_headers)
    assert collect_res.status_code == 200
    assert collect_res.json()["status"] == "collected"
    print(f"[10] PASSED: Request #{req1_id} marked as 'collected'")

    # 11. Complete request: collected -> completed & verify completed_at
    complete_res = client.patch(f"/api/admin/collection-requests/{req1_id}/complete", headers=admin_headers)
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "completed"
    assert complete_res.json()["completed_at"] is not None
    print(f"[11] PASSED: Request #{req1_id} marked as 'completed' (completed_at: {complete_res.json()['completed_at']})")

    # 12. Invalid transition test: completed -> accepted
    invalid_comp_res = client.patch(f"/api/admin/collection-requests/{req1_id}/accept", headers=admin_headers)
    assert invalid_comp_res.status_code == 400
    print("[12] PASSED: Invalid transition from terminal 'completed' state rejected with 400 Bad Request")

    # 13. Rejection test on request 2: submitted -> rejected
    reject_res = client.patch(
        f"/api/admin/collection-requests/{req2_id}/reject",
        headers=admin_headers,
        json={"reason": "Hazardous material not packaged in compliant leak-proof container."},
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "rejected"
    assert "Rejection Reason" in reject_res.json()["additional_notes"]
    print(f"[13] PASSED: Request #{req2_id} rejected with reason stored in notes")

    # 14. Invalid transition test: rejected -> scheduled
    invalid_rej_res = client.patch(
        f"/api/admin/collection-requests/{req2_id}/schedule",
        headers=admin_headers,
        json={"scheduled_date": future_date},
    )
    assert invalid_rej_res.status_code == 400
    print("[14] PASSED: Invalid transition from terminal 'rejected' state rejected with 400 Bad Request")

    # 15. Admin statistics verification (GET /api/admin/collection-requests/stats)
    stats_res = client.get("/api/admin/collection-requests/stats", headers=admin_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "completed" in stats and stats["completed"] >= 1
    assert "rejected" in stats and stats["rejected"] >= 1
    assert "total" in stats and stats["total"] >= 2
    print(f"[15] PASSED: Admin statistics verified: {stats}")

    print("=" * 65)
    print("ALL 15 ADMIN COLLECTION MANAGEMENT TESTS PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
