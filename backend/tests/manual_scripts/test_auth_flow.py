"""Automated test script validating the complete authentication and authorization flow.

Verifies:
1. Normal user registration (POST /api/auth/register)
2. Duplicate email registration rejection (400 Bad Request)
3. Successful login (POST /api/auth/login)
4. Incorrect password rejection (401 Unauthorized)
5. Get current user profile (GET /api/auth/me) with JWT
6. Rejection when token is missing (401 Unauthorized)
7. Rejection when token is invalid (401 Unauthorized)
8. Admin endpoint rejection for normal user (403 Forbidden)
9. Admin authentication and authorization success (200 OK)
"""
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.seed_admin import seed_admin

client = TestClient(app)


def run_tests():
    print("=" * 60)
    print("RUNNING AUTHENTICATION & AUTHORIZATION FLOW TESTS")
    print("=" * 60)

    # Ensure tables and initial admin exist
    init_db()
    seed_admin()

    # 1. Register a normal user
    reg_payload = {
        "name": "Jane Green",
        "email": "jane.green@example.com",
        "password": "JanePassword123!",
    }
    r = client.post("/api/auth/register", json=reg_payload)
    if r.status_code == 400 and "already exists" in r.text:
        print("[1] User already registered from previous run, proceeding...")
    else:
        assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["email"] == "jane.green@example.com"
        assert data["role"] == "user"
        assert "password" not in data and "password_hash" not in data
        print(f"[1] PASSED: User registered successfully (Role: {data['role']})")

    # 2. Try registering duplicate email
    r_dup = client.post("/api/auth/register", json=reg_payload)
    assert r_dup.status_code == 400, f"Expected 400 for duplicate, got {r_dup.status_code}"
    print("[2] PASSED: Duplicate registration correctly rejected with 400 Bad Request")

    # 3. Login with correct credentials
    login_payload = {
        "email": "jane.green@example.com",
        "password": "JanePassword123!",
    }
    r_login = client.post("/api/auth/login", json=login_payload)
    assert r_login.status_code == 200, f"Login failed: {r_login.text}"
    login_data = r_login.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    assert login_data["user"]["role"] == "user"
    user_token = login_data["access_token"]
    print(f"[3] PASSED: User login successful. Token acquired. (Role: {login_data['user']['role']})")

    # 4. Login with incorrect credentials
    r_bad_login = client.post(
        "/api/auth/login",
        json={"email": "jane.green@example.com", "password": "WrongPassword999!"},
    )
    assert r_bad_login.status_code == 401, f"Expected 401, got {r_bad_login.status_code}"
    print("[4] PASSED: Invalid credentials rejected with 401 Unauthorized")

    # 5. Call GET /api/auth/me with valid user token
    r_me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r_me.status_code == 200, f"Get me failed: {r_me.text}"
    me_data = r_me.json()
    assert me_data["email"] == "jane.green@example.com"
    assert me_data["role"] == "user"
    assert "password_hash" not in me_data
    print(f"[5] PASSED: GET /api/auth/me returned profile for '{me_data['name']}' (Role: {me_data['role']})")

    # 6. Call GET /api/auth/me with missing token
    r_no_token = client.get("/api/auth/me")
    assert r_no_token.status_code == 401, f"Expected 401, got {r_no_token.status_code}"
    print("[6] PASSED: Missing token rejected with 401 Unauthorized")

    # 7. Call GET /api/auth/me with invalid token
    r_bad_token = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid.fake.token"},
    )
    assert r_bad_token.status_code == 401, f"Expected 401, got {r_bad_token.status_code}"
    print("[7] PASSED: Invalid token rejected with 401 Unauthorized")

    # 8. Normal user attempts to access admin endpoint -> 403 Forbidden
    r_admin_forbidden = client.get(
        "/api/auth/admin-only",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r_admin_forbidden.status_code == 403, (
        f"Expected 403 Forbidden for normal user on admin endpoint, got {r_admin_forbidden.status_code}"
    )
    print("[8] PASSED: Normal user forbidden (403) from admin-only endpoint")

    # 9. Admin login & access admin endpoint
    admin_login_payload = {
        "email": "admin@ecocycle.com",
        "password": "Admin@Secure123!",
    }
    r_admin_login = client.post("/api/auth/login", json=admin_login_payload)
    assert r_admin_login.status_code == 200, f"Admin login failed: {r_admin_login.text}"
    admin_data = r_admin_login.json()
    assert admin_data["user"]["role"] == "admin"
    admin_token = admin_data["access_token"]
    print(f"[9] PASSED: Admin authenticated successfully (Role: {admin_data['user']['role']})")

    # 10. Admin accesses admin endpoint -> 200 OK
    r_admin_access = client.get(
        "/api/auth/admin-only",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_admin_access.status_code == 200, f"Admin access failed: {r_admin_access.text}"
    assert r_admin_access.json()["admin"]["role"] == "admin"
    print("[10] PASSED: Admin granted access (200 OK) to admin-only endpoint")

    print("=" * 60)
    print("ALL 10 AUTHENTICATION & AUTHORIZATION TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
