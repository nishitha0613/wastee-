"""
Authentication & JWT Security Test Suite
Covers:
- Registration success, duplicate rejection, schema validation
- Login success, incorrect password, nonexistent user
- /api/auth/me profile retrieval with valid token
- Missing, malformed, and expired JWT handling
"""

from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from app.utils.security import create_access_token


def test_successful_registration(client: TestClient):
    """Verify new user registration persists and returns user data without password hash."""
    payload = {
        "name": "Jane Eco",
        "email": "jane@ecocycle.test",
        "password": "SecurePassword123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Eco"
    assert data["email"] == "jane@ecocycle.test"
    assert data["role"] == "user"
    assert "id" in data
    assert "password_hash" not in data
    assert "password" not in data


def test_duplicate_email_registration(client: TestClient, normal_user):
    """Verify registration with an existing email returns 400 Bad Request."""
    payload = {
        "name": "Another Person",
        "email": normal_user["user"].email,
        "password": "AnyPassword123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"name": "No Password", "email": "valid@email.com"},  # missing password
        {"name": "No Email", "password": "Password123!"},  # missing email
        {"email": "invalid-email-format", "password": "Password123!", "name": "Bad Email"},  # bad email
        {"name": "   ", "email": "whitespace@email.com", "password": "Password123!"},  # whitespace name
    ],
)
def test_invalid_registration_data(client: TestClient, invalid_payload):
    """Verify malformed registration requests are rejected with 422 Unprocessable Entity."""
    response = client.post("/api/auth/register", json=invalid_payload)
    assert response.status_code == 422


def test_successful_login(client: TestClient, normal_user):
    """Verify login with correct credentials returns valid JWT token and user info."""
    payload = {
        "email": normal_user["user"].email,
        "password": "Password123!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == normal_user["user"].email
    assert data["user"]["role"] == "user"


def test_login_incorrect_password(client: TestClient, normal_user):
    """Verify login with wrong password returns 401 Unauthorized."""
    payload = {
        "email": normal_user["user"].email,
        "password": "WrongPassword999!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient):
    """Verify login with unregistered email returns 401 Unauthorized."""
    payload = {
        "email": "nonexistent@ecocycle.test",
        "password": "Password123!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_get_current_user_with_valid_token(client: TestClient, normal_user):
    """Verify /api/auth/me returns current user profile when valid token provided."""
    response = client.get("/api/auth/me", headers=normal_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == normal_user["user"].email
    assert data["id"] == normal_user["user"].id
    assert "password_hash" not in data


def test_get_current_user_without_token(client: TestClient):
    """Verify /api/auth/me without authorization header returns 401 Unauthorized."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "missing" in response.json()["detail"].lower()


def test_get_current_user_with_invalid_jwt(client: TestClient):
    """Verify /api/auth/me with malformed JWT returns 401 Unauthorized."""
    headers = {"Authorization": "Bearer this.is.an.invalid.token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "Invalid or expired" in response.json()["detail"]


def test_get_current_user_with_expired_jwt(client: TestClient, normal_user):
    """Verify /api/auth/me with expired JWT returns 401 Unauthorized."""
    # Generate token expired 1 hour ago
    expired_token = create_access_token(
        data={"sub": str(normal_user["user"].id), "email": normal_user["user"].email, "role": normal_user["user"].role},
        expires_delta=timedelta(hours=-1),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "Invalid or expired" in response.json()["detail"]
