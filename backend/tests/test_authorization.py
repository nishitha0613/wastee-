"""
Role-Based Authorization & Resource Ownership Test Suite
Covers:
- Normal user accessing own resources
- Cross-user resource isolation (reports, collection requests)
- Normal user forbidden from admin endpoints
- Admin privileges and full access
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.waste_report import WasteReport
from app.models.collection_request import CollectionRequest, CollectionStatus


def test_user_can_access_own_waste_report(client: TestClient, db_session: Session, normal_user):
    """Verify normal user can access their own waste report."""
    report = WasteReport(
        user_id=normal_user["user"].id,
        image_path="/uploads/test.jpg",
        waste_type="Plastic",
        confidence=0.92,
        disposal_guidance="{}",
    )
    db_session.add(report)
    db_session.commit()

    response = client.get(f"/api/waste/reports/{report.id}", headers=normal_user["headers"])
    assert response.status_code == 200
    assert response.json()["id"] == report.id


def test_user_cannot_access_another_user_waste_report(
    client: TestClient, db_session: Session, normal_user, second_user
):
    """Verify normal user is forbidden (403) from viewing another user's waste report."""
    report = WasteReport(
        user_id=normal_user["user"].id,
        image_path="/uploads/test.jpg",
        waste_type="Glass",
        confidence=0.88,
        disposal_guidance="{}",
    )
    db_session.add(report)
    db_session.commit()

    # Second user attempts to access first user's report
    response = client.get(f"/api/waste/reports/{report.id}", headers=second_user["headers"])
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_user_cannot_delete_another_user_waste_report(
    client: TestClient, db_session: Session, normal_user, second_user
):
    """Verify normal user cannot delete another user's waste report."""
    report = WasteReport(
        user_id=normal_user["user"].id,
        image_path="/uploads/test.jpg",
        waste_type="Paper",
        confidence=0.85,
        disposal_guidance="{}",
    )
    db_session.add(report)
    db_session.commit()

    response = client.delete(f"/api/waste/reports/{report.id}", headers=second_user["headers"])
    assert response.status_code == 403


def test_user_can_access_own_collection_request(
    client: TestClient, db_session: Session, normal_user
):
    """Verify normal user can view their own collection request."""
    col_req = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Metal",
        quantity="2 items",
        location="123 Eco Way",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add(col_req)
    db_session.commit()

    response = client.get(f"/api/collection-requests/{col_req.id}", headers=normal_user["headers"])
    assert response.status_code == 200
    assert response.json()["id"] == col_req.id


def test_user_cannot_access_another_user_collection_request(
    client: TestClient, db_session: Session, normal_user, second_user
):
    """Verify normal user cannot view another user's collection request."""
    col_req = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Organic",
        quantity="5 kg",
        location="123 Eco Way",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add(col_req)
    db_session.commit()

    response = client.get(f"/api/collection-requests/{col_req.id}", headers=second_user["headers"])
    assert response.status_code == 403


def test_user_cannot_cancel_another_user_collection_request(
    client: TestClient, db_session: Session, normal_user, second_user
):
    """Verify normal user cannot cancel another user's collection request."""
    col_req = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Plastic",
        quantity="1 box",
        location="123 Eco Way",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add(col_req)
    db_session.commit()

    response = client.delete(f"/api/collection-requests/{col_req.id}", headers=second_user["headers"])
    assert response.status_code == 403


def test_normal_user_forbidden_from_admin_endpoints(
    client: TestClient, db_session: Session, normal_user
):
    """Verify standard user receives 403 Forbidden on all admin endpoints."""
    # 1. Admin verification endpoint
    r1 = client.get("/api/auth/admin-only", headers=normal_user["headers"])
    assert r1.status_code == 403

    # 2. Admin collection requests list
    r2 = client.get("/api/admin/collection-requests", headers=normal_user["headers"])
    assert r2.status_code == 403

    # 3. Admin collection requests statistics
    r3 = client.get("/api/admin/collection-requests/stats", headers=normal_user["headers"])
    assert r3.status_code == 403

    # 4. Admin status transition endpoint
    col_req = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Plastic",
        quantity="1 box",
        location="123 Eco Way",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add(col_req)
    db_session.commit()

    r4 = client.patch(
        f"/api/admin/collection-requests/{col_req.id}/accept",
        json={"notes": "Illegal user action"},
        headers=normal_user["headers"],
    )
    assert r4.status_code == 403


def test_admin_can_access_admin_endpoints(client: TestClient, admin_user):
    """Verify admin user can successfully access admin endpoints."""
    # 1. Admin verification endpoint
    r1 = client.get("/api/auth/admin-only", headers=admin_user["headers"])
    assert r1.status_code == 200
    assert r1.json()["admin"]["role"] == "admin"

    # 2. Admin collection requests list
    r2 = client.get("/api/admin/collection-requests", headers=admin_user["headers"])
    assert r2.status_code == 200
    assert isinstance(r2.json()["items"], list)

    # 3. Admin collection statistics
    r3 = client.get("/api/admin/collection-requests/stats", headers=admin_user["headers"])
    assert r3.status_code == 200
    assert "total" in r3.json()
    assert "submitted" in r3.json()
