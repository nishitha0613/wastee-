"""
Admin Workflow, State Machine, & Statistics Test Suite
Covers:
- Complete linear workflow: submitted -> accepted -> scheduled -> collected -> completed
- Alternative rejection workflow: submitted -> rejected
- State transition guards & invalid transition rejection
- completed_at timestamp verification
- Admin collection statistics aggregation
"""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.collection_request import CollectionRequest, CollectionStatus


def test_complete_admin_state_machine_workflow(
    client: TestClient, db_session: Session, normal_user, admin_user
):
    """Test full linear transition: submitted -> accepted -> scheduled -> collected -> completed."""
    # 1. Create a request as user
    col_req = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Plastic",
        quantity="5 boxes",
        location="789 Clean Street",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add(col_req)
    db_session.commit()
    req_id = col_req.id

    # 2. Admin accepts: submitted -> accepted
    r_accept = client.patch(
        f"/api/admin/collection-requests/{req_id}/accept",
        json={"notes": "Approved for processing"},
        headers=admin_user["headers"],
    )
    assert r_accept.status_code == 200
    assert r_accept.json()["status"] == "accepted"

    # 3. Admin schedules: accepted -> scheduled
    future_date = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    r_sched = client.patch(
        f"/api/admin/collection-requests/{req_id}/schedule",
        json={"scheduled_date": future_date, "notes": "Assigned truck #4"},
        headers=admin_user["headers"],
    )
    assert r_sched.status_code == 200
    assert r_sched.json()["status"] == "scheduled"
    assert r_sched.json()["scheduled_date"] is not None

    # 4. Admin marks collected: scheduled -> collected
    r_col = client.patch(
        f"/api/admin/collection-requests/{req_id}/collect",
        json={"notes": "Waste retrieved by driver"},
        headers=admin_user["headers"],
    )
    assert r_col.status_code == 200
    assert r_col.json()["status"] == "collected"

    # 5. Admin marks completed: collected -> completed
    r_comp = client.patch(
        f"/api/admin/collection-requests/{req_id}/complete",
        json={"notes": "Drop-off at recycling facility confirmed"},
        headers=admin_user["headers"],
    )
    assert r_comp.status_code == 200
    comp_data = r_comp.json()
    assert comp_data["status"] == "completed"
    assert comp_data["completed_at"] is not None


def test_admin_rejection_workflow(
    client: TestClient, db_session: Session, normal_user, admin_user
):
    """Test alternative transition: submitted -> rejected."""
    col_req = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Hazardous",
        quantity="1 drum",
        location="Chemical plant zone",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add(col_req)
    db_session.commit()

    response = client.patch(
        f"/api/admin/collection-requests/{col_req.id}/reject",
        json={"notes": "Requires specialized industrial permit."},
        headers=admin_user["headers"],
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_invalid_state_transitions(
    client: TestClient, db_session: Session, normal_user, admin_user
):
    """Verify state machine rejects invalid and out-of-order transitions."""
    col_req = CollectionRequest(
        user_id=normal_user["user"].id,
        waste_type="Paper",
        quantity="10 kg",
        location="Office building",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add(col_req)
    db_session.commit()
    req_id = col_req.id

    # 1. submitted -> collected (Invalid: must be accepted and scheduled first)
    r1 = client.patch(
        f"/api/admin/collection-requests/{req_id}/collect",
        json={},
        headers=admin_user["headers"],
    )
    assert r1.status_code == 400
    assert "invalid status transition" in r1.json()["detail"].lower()

    # 2. submitted -> completed (Invalid)
    r2 = client.patch(
        f"/api/admin/collection-requests/{req_id}/complete",
        json={},
        headers=admin_user["headers"],
    )
    assert r2.status_code == 400

    # Transition to accepted
    client.patch(f"/api/admin/collection-requests/{req_id}/accept", json={}, headers=admin_user["headers"])

    # 3. accepted -> completed (Invalid: must be scheduled and collected first)
    r3 = client.patch(
        f"/api/admin/collection-requests/{req_id}/complete",
        json={},
        headers=admin_user["headers"],
    )
    assert r3.status_code == 400

    # 4. Scheduling with a date in the past returns 422
    past_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    r4 = client.patch(
        f"/api/admin/collection-requests/{req_id}/schedule",
        json={"scheduled_date": past_date},
        headers=admin_user["headers"],
    )
    assert r4.status_code == 422


def test_admin_collection_statistics(
    client: TestClient, db_session: Session, normal_user, admin_user
):
    """Verify statistics endpoint aggregates exact counts by status and total."""
    user_id = normal_user["user"].id

    requests = [
        CollectionRequest(user_id=user_id, waste_type="Plastic", quantity="1", location="A", status=CollectionStatus.SUBMITTED.value),
        CollectionRequest(user_id=user_id, waste_type="Plastic", quantity="2", location="B", status=CollectionStatus.SUBMITTED.value),
        CollectionRequest(user_id=user_id, waste_type="Organic", quantity="1", location="C", status=CollectionStatus.ACCEPTED.value),
        CollectionRequest(user_id=user_id, waste_type="Glass", quantity="1", location="D", status=CollectionStatus.SCHEDULED.value),
        CollectionRequest(user_id=user_id, waste_type="Metal", quantity="1", location="E", status=CollectionStatus.COLLECTED.value),
        CollectionRequest(user_id=user_id, waste_type="Paper", quantity="1", location="F", status=CollectionStatus.COMPLETED.value),
        CollectionRequest(user_id=user_id, waste_type="Hazardous", quantity="1", location="G", status=CollectionStatus.REJECTED.value),
    ]
    db_session.add_all(requests)
    db_session.commit()

    response = client.get("/api/admin/collection-requests/stats", headers=admin_user["headers"])
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 7
    assert data["submitted"] == 2
    assert data["accepted"] == 1
    assert data["scheduled"] == 1
    assert data["collected"] == 1
    assert data["completed"] == 1
    assert data["rejected"] == 1
