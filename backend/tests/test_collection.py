"""
Collection Request Test Suite
Covers:
- Creating a collection request with & without waste report link
- Validation of waste_report_id existence & ownership
- Prevention of duplicate active requests for the same report
- Retrieving user's own requests
- Request cancellation rules (submitted allowed, accepted/beyond rejected)
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.waste_report import WasteReport
from app.models.collection_request import CollectionRequest, CollectionStatus


def test_create_collection_request_direct(client: TestClient, normal_user):
    """Verify user can create a collection request directly specifying waste type."""
    payload = {
        "waste_type": "Plastic",
        "quantity": "3 large bags",
        "location": "100 Green Avenue, Apt 4",
        "additional_notes": "Leave at front gate",
    }
    response = client.post("/api/collection-requests", json=payload, headers=normal_user["headers"])
    assert response.status_code == 201
    data = response.json()
    assert data["waste_type"] == "Plastic"
    assert data["quantity"] == "3 large bags"
    assert data["location"] == "100 Green Avenue, Apt 4"
    assert data["status"] == "submitted"
    assert data["user_id"] == normal_user["user"].id


def test_create_collection_request_linked_to_report(
    client: TestClient, db_session: Session, normal_user
):
    """Verify collection request links to user's WasteReport and derives waste type."""
    report = WasteReport(
        user_id=normal_user["user"].id,
        image_path="/uploads/test.jpg",
        waste_type="E-Waste",
        confidence=0.94,
        disposal_guidance="{}",
    )
    db_session.add(report)
    db_session.commit()

    payload = {
        "waste_report_id": report.id,
        "quantity": "1 old desktop PC",
        "location": "100 Green Avenue, Apt 4",
    }
    response = client.post("/api/collection-requests", json=payload, headers=normal_user["headers"])
    assert response.status_code == 201
    data = response.json()
    assert data["waste_report_id"] == report.id
    assert data["waste_type"] == "E-Waste"
    assert data["status"] == "submitted"


def test_create_collection_request_invalid_report_id(client: TestClient, normal_user):
    """Verify linking a non-existent report ID returns 404 Not Found."""
    payload = {
        "waste_report_id": 999999,
        "quantity": "1 item",
        "location": "100 Green Avenue",
    }
    response = client.post("/api/collection-requests", json=payload, headers=normal_user["headers"])
    assert response.status_code == 404
    assert "referenced waste report not found" in response.json()["detail"].lower()


def test_create_collection_request_linking_other_user_report(
    client: TestClient, db_session: Session, normal_user, second_user
):
    """Verify user cannot link another user's waste report to a collection request."""
    # Report belongs to second_user
    report = WasteReport(
        user_id=second_user["user"].id,
        image_path="/uploads/test.jpg",
        waste_type="Metal",
        confidence=0.90,
        disposal_guidance="{}",
    )
    db_session.add(report)
    db_session.commit()

    # normal_user attempts to link second_user's report
    payload = {
        "waste_report_id": report.id,
        "quantity": "5 metal cans",
        "location": "User 1 address",
    }
    response = client.post("/api/collection-requests", json=payload, headers=normal_user["headers"])
    assert response.status_code == 403
    assert "only request collection for your own" in response.json()["detail"].lower()


def test_prevent_duplicate_request_for_same_report(
    client: TestClient, db_session: Session, normal_user
):
    """Verify only one active collection request can be created per waste report."""
    report = WasteReport(
        user_id=normal_user["user"].id,
        image_path="/uploads/test.jpg",
        waste_type="Paper",
        confidence=0.88,
        disposal_guidance="{}",
    )
    db_session.add(report)
    db_session.commit()

    payload = {
        "waste_report_id": report.id,
        "quantity": "Stack of newspapers",
        "location": "100 Green Avenue",
    }
    # First submission succeeds
    r1 = client.post("/api/collection-requests", json=payload, headers=normal_user["headers"])
    assert r1.status_code == 201

    # Second submission for the same report fails with 400 Bad Request
    r2 = client.post("/api/collection-requests", json=payload, headers=normal_user["headers"])
    assert r2.status_code == 400
    assert "already been submitted" in r2.json()["detail"].lower()


def test_get_user_collection_requests(client: TestClient, db_session: Session, normal_user):
    """Verify user retrieves only their own collection requests."""
    req1 = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Plastic",
        quantity="1 box",
        location="123 Eco Way",
        status=CollectionStatus.SUBMITTED.value,
    )
    req2 = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Glass",
        quantity="2 boxes",
        location="123 Eco Way",
        status=CollectionStatus.ACCEPTED.value,
    )
    db_session.add_all([req1, req2])
    db_session.commit()

    response = client.get("/api/collection-requests", headers=normal_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] == 2
    requests = data["items"]
    assert len(requests) == 2
    ids = [r["id"] for r in requests]
    assert req1.id in ids
    assert req2.id in ids


def test_cancel_collection_request_in_submitted_status(
    client: TestClient, db_session: Session, normal_user
):
    """Verify user can cancel a request that is still in 'submitted' status."""
    req = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Organic",
        quantity="1 compost bucket",
        location="123 Eco Way",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add(req)
    db_session.commit()

    response = client.delete(f"/api/collection-requests/{req.id}", headers=normal_user["headers"])
    assert response.status_code == 200
    assert "cancelled successfully" in response.json()["message"].lower()

    # Confirm it is removed from database
    verify_resp = client.get(f"/api/collection-requests/{req.id}", headers=normal_user["headers"])
    assert verify_resp.status_code == 404


def test_cannot_cancel_collection_request_after_acceptance(
    client: TestClient, db_session: Session, normal_user
):
    """Verify user cannot cancel a request once accepted or scheduled."""
    req = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Plastic",
        quantity="1 crate",
        location="123 Eco Way",
        status=CollectionStatus.ACCEPTED.value,
    )
    db_session.add(req)
    db_session.commit()

    response = client.delete(f"/api/collection-requests/{req.id}", headers=normal_user["headers"])
    assert response.status_code == 400
    assert "cannot cancel a collection request with status 'accepted'" in response.json()["detail"].lower()
