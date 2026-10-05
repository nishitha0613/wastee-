"""
Database Integrity, Relationships, Foreign Keys, & Rollback Test Suite
Covers:
- Model relationships and back-references
- SQLite Foreign Key constraint enforcement
- Transaction rollback behavior on exceptions
- Prevention of incomplete / orphaned records
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.waste_report import WasteReport
from app.models.collection_request import CollectionRequest, CollectionStatus
from app.utils.security import get_password_hash


def test_user_relationships(db_session: Session):
    """Verify User model bidirectional relationships with WasteReports and CollectionRequests."""
    user = User(
        name="Relationship Test User",
        email="relations@ecocycle.test",
        password_hash=get_password_hash("Pass123!"),
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()

    report = WasteReport(
        user_id=user.id,
        image_path="/uploads/rel_test.jpg",
        waste_type="Paper",
        confidence=0.92,
        disposal_guidance="{}",
    )
    col_req = CollectionRequest(
        user_id=user.id,
        waste_type="Paper",
        quantity="1 box",
        location="Front porch",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add_all([report, col_req])
    db_session.commit()

    db_session.refresh(user)
    assert len(user.waste_reports) == 1
    assert user.waste_reports[0].id == report.id
    assert len(user.collection_requests) == 1
    assert user.collection_requests[0].id == col_req.id


def test_foreign_key_enforcement_on_invalid_user(db_session: Session):
    """Verify SQLite foreign key constraint raises IntegrityError on nonexistent user_id."""
    invalid_report = WasteReport(
        user_id=999999,  # Does not exist
        image_path="/uploads/orphan.jpg",
        waste_type="Plastic",
        confidence=0.90,
        disposal_guidance="{}",
    )
    db_session.add(invalid_report)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_foreign_key_enforcement_on_invalid_collection_user(db_session: Session):
    """Verify CollectionRequest cannot be created with non-existent user_id."""
    invalid_req = CollectionRequest(
        user_id=999999,  # Does not exist
        waste_type="Organic",
        quantity="1 bag",
        location="123 Test St",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add(invalid_req)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_transaction_rollback_leaves_no_incomplete_records(db_session: Session):
    """Verify an aborted transaction rolls back cleanly without leaving partial records."""
    user = User(
        name="Rollback Test User",
        email="rollback@ecocycle.test",
        password_hash=get_password_hash("Pass123!"),
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()

    # Attempt a batch operation where the second operation violates a constraint
    try:
        valid_report = WasteReport(
            user_id=user.id,
            image_path="/uploads/valid_before_fail.jpg",
            waste_type="Glass",
            confidence=0.95,
            disposal_guidance="{}",
        )
        invalid_report = WasteReport(
            user_id=888888,  # Invalid FK
            image_path="/uploads/fail.jpg",
            waste_type="Glass",
            confidence=0.95,
            disposal_guidance="{}",
        )
        db_session.add(valid_report)
        db_session.add(invalid_report)
        db_session.commit()
    except IntegrityError:
        db_session.rollback()

    # Verify that valid_report was NOT committed due to transaction rollback
    reports_in_db = db_session.query(WasteReport).filter(WasteReport.user_id == user.id).all()
    assert len(reports_in_db) == 0


def test_cascade_delete_user_removes_reports_and_requests(db_session: Session):
    """Verify deleting a User cascades to clean up associated WasteReports and CollectionRequests."""
    user = User(
        name="Cascade Test User",
        email="cascade@ecocycle.test",
        password_hash=get_password_hash("Pass123!"),
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()

    report = WasteReport(
        user_id=user.id,
        image_path="/uploads/cascade_report.jpg",
        waste_type="Metal",
        confidence=0.89,
        disposal_guidance="{}",
    )
    req = CollectionRequest(
        user_id=user.id,
        waste_type="Metal",
        quantity="1 sack",
        location="Garage",
        status=CollectionStatus.SUBMITTED.value,
    )
    db_session.add_all([report, req])
    db_session.commit()

    # Delete user
    db_session.delete(user)
    db_session.commit()

    # Verify orphan records are deleted by cascade
    assert db_session.query(WasteReport).filter(WasteReport.user_id == user.id).count() == 0
    assert db_session.query(CollectionRequest).filter(CollectionRequest.user_id == user.id).count() == 0
