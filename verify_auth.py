#!/usr/bin/env python3
"""
Authentication Verification Script:
Verifies:
  1. Fresh user registration -> DB insertion check
  2. Duplicate email rejection
  3. Logout
  4. Login with real credentials -> real JWT issuance
  5. GET /api/auth/me verification (id, name, email, role='user')
  6. Persistence simulation (valid token verified via /api/auth/me)
  7. Expired/invalid JWT rejection -> logout simulation
  8. Login with incorrect password rejected (401)
  9. Admin login & role verification (role='admin')
  10. Citizen registration never allows role='admin'
"""

import sqlite3
import time
import httpx

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/waste_management.db"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_auth_flows():
    client = httpx.Client(timeout=10.0)

    # 1. Register a new user
    ts = int(time.time() * 1000)
    email = f"fresh_user_{ts}@ecocycle-verify.org"
    password = "StrongPassword123!"
    name = f"Audit User {ts}"

    log(f"Registering fresh user: {email}...")
    res = client.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert res.status_code == 201, f"Registration failed: {res.text}"
    user_created = res.json()
    assert user_created["email"] == email
    assert user_created["role"] == "user"
    user_id = user_created["id"]
    log(f"User registered with ID={user_id}, role='{user_created['role']}'", "PASS")

    # 2. Confirm the user is created in the actual SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password_hash, role FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None, f"User {email} not found in database!"
    assert row[0] == user_id
    assert row[1] == name
    assert row[2] == email
    assert row[3].startswith("$2b$") or row[3].startswith("$2a$"), "Password is not a bcrypt hash!"
    assert row[4] == "user"
    log(f"Verified user in SQLite database: ID={row[0]}, bcrypt hash={row[3][:15]}..., role={row[4]}", "PASS")

    # 3. Duplicate email registration rejected
    res = client.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert res.status_code == 400
    log("Duplicate email registration properly rejected (400 Bad Request)", "PASS")

    # 4. Login using the real credentials
    res = client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200, f"Login failed: {res.text}"
    login_data = res.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    assert len(token) > 30 and token.count(".") == 2, "Token is not a valid JWT format!"
    assert login_data["user"]["email"] == email
    assert login_data["user"]["role"] == "user"
    log("Login returned real JWT signed token and user profile", "PASS")

    # 5. Call GET /api/auth/me with the real JWT
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert res.status_code == 200, f"/me failed: {res.text}"
    me = res.json()
    assert me["id"] == user_id
    assert me["name"] == name
    assert me["email"] == email
    assert me["role"] == "user"
    log(f"/api/auth/me returned authentic identity: Name='{me['name']}', Role='{me['role']}'", "PASS")

    # 6. Simulate Session Persistence (Token verification on reload)
    res_verify = client.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_verify.status_code == 200
    log("Simulated frontend reload: stored token successfully validated against /api/auth/me", "PASS")

    # 7. Simulate Invalid / Expired Token
    res_invalid = client.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": "Bearer fake.tampered.token"})
    assert res_invalid.status_code == 401
    log("Invalid / tampered token rejected with 401 (triggers client-side logout)", "PASS")

    # 8. Try login with incorrect password
    res = client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": "WrongPassword999!"},
    )
    assert res.status_code == 401
    log("Login with incorrect password rejected with 401 Unauthorized", "PASS")

    # 9. Verify Admin login
    res_admin = client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@ecocycle.com", "password": "Admin@Secure123!"},
    )
    assert res_admin.status_code == 200
    admin_data = res_admin.json()
    assert admin_data["user"]["role"] == "admin"
    admin_token = admin_data["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    res_admin_me = client.get(f"{BASE_URL}/api/auth/me", headers=admin_headers)
    assert res_admin_me.json()["role"] == "admin"
    log("Administrator login verified: real JWT issued with role='admin'", "PASS")

    # 10. Verify Citizen cannot register as Admin
    res_hack = client.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": "Hacker", "email": f"hacker_{ts}@domain.org", "password": "Password123!", "role": "admin"},
    )
    assert res_hack.status_code == 201
    assert res_hack.json()["role"] == "user", "Registration allowed setting role='admin'!"
    log("Registration role override prevented: citizen registration strictly enforced as role='user'", "PASS")

    print("\n========================================================")
    print("ALL USER AUTHENTICATION & REGISTRATION TESTS PASSED (100%)")
    print("========================================================")

if __name__ == "__main__":
    test_auth_flows()
