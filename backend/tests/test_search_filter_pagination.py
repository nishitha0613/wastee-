"""
Search, Filtering, and Pagination Test Suite
Covers:
- Waste reports pagination (empty, multiple pages, isolation, invalid parameters)
- Collection requests pagination (empty, multiple pages, isolation, invalid parameters)
- Admin filtering by status, waste_type, and date range
- Admin search across user name, user email, waste type, and location
- Combined filters, search, and pagination
- Parameter boundary validation (page < 1, limit <= 0, limit > 100)
"""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.waste_report import WasteReport
from app.models.collection_request import CollectionRequest, CollectionStatus
from app.utils.security import get_password_hash


# ----------------------------------------------------------------------
# 1. Waste Reports Pagination Tests
# ----------------------------------------------------------------------

def test_waste_reports_pagination_empty(client: TestClient, normal_user):
    """Verify empty waste reports returns total=0, total_pages=0, items=[]."""
    response = client.get("/api/waste/reports?page=1&limit=10", headers=normal_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["total"] == 0
    assert data["total_pages"] == 0


def test_waste_reports_pagination_multiple_pages(client: TestClient, db_session: Session, normal_user):
    """Verify pagination across multiple pages for waste reports."""
    user_id = normal_user["user"].id
    # Seed 15 reports
    reports = [
        WasteReport(
            user_id=user_id,
            image_path=f"/uploads/img_{i}.jpg",
            waste_type="Plastic",
            confidence=0.90,
            disposal_guidance="{}",
        )
        for i in range(15)
    ]
    db_session.add_all(reports)
    db_session.commit()

    # Request Page 1, limit 10
    r1 = client.get("/api/waste/reports?page=1&limit=10", headers=normal_user["headers"])
    assert r1.status_code == 200
    d1 = r1.json()
    assert len(d1["items"]) == 10
    assert d1["page"] == 1
    assert d1["limit"] == 10
    assert d1["total"] == 15
    assert d1["total_pages"] == 2

    # Request Page 2, limit 10
    r2 = client.get("/api/waste/reports?page=2&limit=10", headers=normal_user["headers"])
    assert r2.status_code == 200
    d2 = r2.json()
    assert len(d2["items"]) == 5
    assert d2["page"] == 2
    assert d2["total"] == 15
    assert d2["total_pages"] == 2


def test_waste_reports_pagination_user_isolation(
    client: TestClient, db_session: Session, normal_user, second_user
):
    """Verify normal user pagination only includes their own reports."""
    # Seed 3 reports for normal_user, 5 for second_user
    db_session.add_all([
        WasteReport(user_id=normal_user["user"].id, image_path="/uploads/u1.jpg", waste_type="Paper", confidence=0.8, disposal_guidance="{}")
        for _ in range(3)
    ])
    db_session.add_all([
        WasteReport(user_id=second_user["user"].id, image_path="/uploads/u2.jpg", waste_type="Metal", confidence=0.8, disposal_guidance="{}")
        for _ in range(5)
    ])
    db_session.commit()

    response = client.get("/api/waste/reports?page=1&limit=10", headers=normal_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    for item in data["items"]:
        assert item["user_id"] == normal_user["user"].id


def test_waste_reports_invalid_pagination_parameters(client: TestClient, normal_user):
    """Verify invalid page/limit parameters are rejected with 422 Unprocessable Entity."""
    # page < 1
    r1 = client.get("/api/waste/reports?page=0&limit=10", headers=normal_user["headers"])
    assert r1.status_code == 422

    # limit <= 0
    r2 = client.get("/api/waste/reports?page=1&limit=0", headers=normal_user["headers"])
    assert r2.status_code == 422

    # limit > 100
    r3 = client.get("/api/waste/reports?page=1&limit=150", headers=normal_user["headers"])
    assert r3.status_code == 422


# ----------------------------------------------------------------------
# 2. Collection Requests Pagination Tests
# ----------------------------------------------------------------------

def test_collection_requests_pagination_empty(client: TestClient, normal_user):
    """Verify empty collection requests returns total=0, total_pages=0, items=[]."""
    response = client.get("/api/collection-requests?page=1&limit=10", headers=normal_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["total_pages"] == 0


def test_collection_requests_pagination_multiple_pages(client: TestClient, db_session: Session, normal_user):
    """Verify pagination across multiple pages for collection requests."""
    user_id = normal_user["user"].id
    requests = [
        CollectionRequest(
            user_id=user_id,
            waste_type="Organic",
            quantity=f"{i} kg",
            location=f"House {i}",
            status=CollectionStatus.SUBMITTED.value,
        )
        for i in range(12)
    ]
    db_session.add_all(requests)
    db_session.commit()

    # Page 1, limit 5
    r1 = client.get("/api/collection-requests?page=1&limit=5", headers=normal_user["headers"])
    assert r1.status_code == 200
    d1 = r1.json()
    assert len(d1["items"]) == 5
    assert d1["total"] == 12
    assert d1["total_pages"] == 3

    # Page 3, limit 5 (remaining 2 items)
    r3 = client.get("/api/collection-requests?page=3&limit=5", headers=normal_user["headers"])
    assert r3.status_code == 200
    d3 = r3.json()
    assert len(d3["items"]) == 2
    assert d3["page"] == 3


def test_collection_requests_invalid_pagination_parameters(client: TestClient, normal_user):
    """Verify invalid pagination values on collection requests return 422."""
    r1 = client.get("/api/collection-requests?page=-1&limit=10", headers=normal_user["headers"])
    assert r1.status_code == 422

    r2 = client.get("/api/collection-requests?page=1&limit=500", headers=normal_user["headers"])
    assert r2.status_code == 422


# ----------------------------------------------------------------------
# 3. Admin Filtering Tests (Status, Waste Type, Date Range)
# ----------------------------------------------------------------------

def test_admin_filter_by_status(client: TestClient, db_session: Session, normal_user, admin_user):
    """Verify admin can filter collection requests by status."""
    u_id = normal_user["user"].id
    db_session.add_all([
        CollectionRequest(user_id=u_id, waste_type="Plastic", quantity="1", location="Loc 1", status=CollectionStatus.SUBMITTED.value),
        CollectionRequest(user_id=u_id, waste_type="Plastic", quantity="2", location="Loc 2", status=CollectionStatus.ACCEPTED.value),
        CollectionRequest(user_id=u_id, waste_type="Plastic", quantity="3", location="Loc 3", status=CollectionStatus.COMPLETED.value),
    ])
    db_session.commit()

    # Filter status=submitted
    res_sub = client.get("/api/admin/collection-requests?status=submitted", headers=admin_user["headers"])
    assert res_sub.status_code == 200
    d_sub = res_sub.json()
    assert d_sub["total"] == 1
    assert d_sub["items"][0]["status"] == "submitted"

    # Filter status=completed
    res_comp = client.get("/api/admin/collection-requests?status=completed", headers=admin_user["headers"])
    assert res_comp.status_code == 200
    d_comp = res_comp.json()
    assert d_comp["total"] == 1
    assert d_comp["items"][0]["status"] == "completed"


def test_admin_filter_by_waste_type(client: TestClient, db_session: Session, normal_user, admin_user):
    """Verify admin can filter collection requests by waste_type."""
    u_id = normal_user["user"].id
    db_session.add_all([
        CollectionRequest(user_id=u_id, waste_type="E-Waste", quantity="1", location="Loc 1", status=CollectionStatus.SUBMITTED.value),
        CollectionRequest(user_id=u_id, waste_type="Hazardous", quantity="1", location="Loc 2", status=CollectionStatus.SUBMITTED.value),
        CollectionRequest(user_id=u_id, waste_type="E-Waste", quantity="2", location="Loc 3", status=CollectionStatus.SUBMITTED.value),
    ])
    db_session.commit()

    res = client.get("/api/admin/collection-requests?waste_type=E-Waste", headers=admin_user["headers"])
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    for item in data["items"]:
        assert item["waste_type"].lower() == "e-waste"


def test_admin_filter_by_date_range(client: TestClient, db_session: Session, normal_user, admin_user):
    """Verify admin can filter collection requests by requested_at date range."""
    u_id = normal_user["user"].id
    now = datetime.now(timezone.utc)

    # 1 item 5 days ago, 1 item 2 days ago, 1 item today
    r_old = CollectionRequest(user_id=u_id, waste_type="Paper", quantity="1", location="Loc Old", status=CollectionStatus.SUBMITTED.value)
    r_old.requested_at = now - timedelta(days=5)

    r_mid = CollectionRequest(user_id=u_id, waste_type="Paper", quantity="2", location="Loc Mid", status=CollectionStatus.SUBMITTED.value)
    r_mid.requested_at = now - timedelta(days=2)

    r_new = CollectionRequest(user_id=u_id, waste_type="Paper", quantity="3", location="Loc New", status=CollectionStatus.SUBMITTED.value)
    r_new.requested_at = now

    db_session.add_all([r_old, r_mid, r_new])
    db_session.commit()

    # Filter between 3 days ago and 1 day ago (should match only r_mid)
    from_date = (now - timedelta(days=3)).isoformat()
    to_date = (now - timedelta(days=1)).isoformat()

    res = client.get(
        f"/api/admin/collection-requests?from_date={from_date}&to_date={to_date}",
        headers=admin_user["headers"],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["location"] == "Loc Mid"


# ----------------------------------------------------------------------
# 4. Admin Search Tests (User Name, Email, Waste Type, Location)
# ----------------------------------------------------------------------

def test_admin_search_by_user_name_and_email(client: TestClient, db_session: Session, admin_user):
    """Verify search finds collection requests by citizen's name and email."""
    user_alice = User(
        name="Alice Wonderland",
        email="alice.wonder@ecocycle.test",
        password_hash=get_password_hash("Pass123!"),
        role=UserRole.USER.value,
    )
    user_bob = User(
        name="Bob Builder",
        email="bob.builder@ecocycle.test",
        password_hash=get_password_hash("Pass123!"),
        role=UserRole.USER.value,
    )
    db_session.add_all([user_alice, user_bob])
    db_session.commit()

    db_session.add(CollectionRequest(user_id=user_alice.id, waste_type="Glass", quantity="1", location="Wonderland Manor", status="submitted"))
    db_session.add(CollectionRequest(user_id=user_bob.id, waste_type="Metal", quantity="1", location="Builder Yard", status="submitted"))
    db_session.commit()

    # Search user name "Alice"
    res_alice = client.get("/api/admin/collection-requests?search=Alice", headers=admin_user["headers"])
    assert res_alice.status_code == 200
    assert res_alice.json()["total"] == 1
    assert res_alice.json()["items"][0]["user"]["name"] == "Alice Wonderland"

    # Search user email "bob.builder"
    res_bob = client.get("/api/admin/collection-requests?search=bob.builder", headers=admin_user["headers"])
    assert res_bob.status_code == 200
    assert res_bob.json()["total"] == 1
    assert res_bob.json()["items"][0]["user"]["email"] == "bob.builder@ecocycle.test"


def test_admin_search_by_location(client: TestClient, db_session: Session, normal_user, admin_user):
    """Verify search finds collection requests by location substring."""
    u_id = normal_user["user"].id
    db_session.add_all([
        CollectionRequest(user_id=u_id, waste_type="Plastic", quantity="1", location="Sunset Boulevard #42", status="submitted"),
        CollectionRequest(user_id=u_id, waste_type="Plastic", quantity="1", location="Sunrise Avenue #10", status="submitted"),
    ])
    db_session.commit()

    res = client.get("/api/admin/collection-requests?search=Sunset", headers=admin_user["headers"])
    assert res.status_code == 200
    assert res.json()["total"] == 1
    assert "Sunset Boulevard" in res.json()["items"][0]["location"]


# ----------------------------------------------------------------------
# 5. Combined Filters + Search + Pagination
# ----------------------------------------------------------------------

def test_admin_combined_filter_search_and_pagination(
    client: TestClient, db_session: Session, normal_user, admin_user
):
    """Verify combined status filter, waste_type filter, search query, and pagination."""
    u_id = normal_user["user"].id

    # Add 6 matching items and 4 non-matching items
    matching = [
        CollectionRequest(user_id=u_id, waste_type="Plastic", quantity=f"{i}", location=f"Green Zone Sector {i}", status="submitted")
        for i in range(6)
    ]
    non_matching_status = [
        CollectionRequest(user_id=u_id, waste_type="Plastic", quantity="1", location="Green Zone Sector X", status="completed")
    ]
    non_matching_location = [
        CollectionRequest(user_id=u_id, waste_type="Plastic", quantity="1", location="Red Zone Sector Y", status="submitted")
    ]
    non_matching_type = [
        CollectionRequest(user_id=u_id, waste_type="Organic", quantity="1", location="Green Zone Sector Z", status="submitted")
    ]
    db_session.add_all(matching + non_matching_status + non_matching_location + non_matching_type)
    db_session.commit()

    # Query: status=submitted & waste_type=Plastic & search=Green & limit=4
    res = client.get(
        "/api/admin/collection-requests?status=submitted&waste_type=Plastic&search=Green&page=1&limit=4",
        headers=admin_user["headers"],
    )
    assert res.status_code == 200
    data = res.json()

    assert data["total"] == 6
    assert data["total_pages"] == 2
    assert len(data["items"]) == 4
    for item in data["items"]:
        assert item["status"] == "submitted"
        assert item["waste_type"] == "Plastic"
        assert "Green" in item["location"]

    # Page 2 should have the remaining 2 items
    res_p2 = client.get(
        "/api/admin/collection-requests?status=submitted&waste_type=Plastic&search=Green&page=2&limit=4",
        headers=admin_user["headers"],
    )
    assert res_p2.status_code == 200
    assert len(res_p2.json()["items"]) == 2
