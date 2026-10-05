import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.collection_request import CollectionRequest, CollectionStatus
from app.schemas.pagination import PaginatedResponse
from app.schemas.collection_request import (
    AdminCollectionRequestResponse,
    ScheduleRequestPayload,
    RejectRequestPayload,
    CollectionStatsResponse,
)
from app.utils.dependencies import get_current_admin

logger = logging.getLogger("app.routers.admin_collection")

router = APIRouter(
    prefix="/admin/collection-requests",
    tags=["Admin - Collection Management"],
)

# Centralized status transition rules (Strict state machine: submitted -> accepted -> scheduled -> collected -> completed, or submitted -> rejected)
ALLOWED_TRANSITIONS = {
    CollectionStatus.SUBMITTED.value: [
        CollectionStatus.ACCEPTED.value,
        CollectionStatus.REJECTED.value,
    ],
    CollectionStatus.ACCEPTED.value: [
        CollectionStatus.SCHEDULED.value,
    ],
    CollectionStatus.SCHEDULED.value: [
        CollectionStatus.COLLECTED.value,
    ],
    CollectionStatus.COLLECTED.value: [
        CollectionStatus.COMPLETED.value,
    ],
    CollectionStatus.COMPLETED.value: [],
    CollectionStatus.REJECTED.value: [],
}


def validate_status_transition(current_status: str, target_status: str) -> None:
    """Ensure that the state transition conforms to the defined lifecycle rules."""
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if target_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition from '{current_status}' to '{target_status}'. "
                f"Allowed target states: {allowed if allowed else 'None (Terminal state)'}."
            ),
        )


@router.get(
    "/stats",
    response_model=CollectionStatsResponse,
    summary="Get collection request counts by status",
    description="Returns aggregate counts across all collection request statuses for the administrative overview.",
)
def get_collection_statistics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    counts = {s.value: 0 for s in CollectionStatus}
    rows = (
        db.query(CollectionRequest.status, func.count(CollectionRequest.id))
        .group_by(CollectionRequest.status)
        .all()
    )
    for st, cnt in rows:
        if st in counts:
            counts[st] = cnt

    counts["total"] = sum(counts.values())
    return CollectionStatsResponse(**counts)


def parse_date_param(param: Optional[str], param_name: str) -> Optional[datetime]:
    if not param or not str(param).strip():
        return None
    val = str(param).strip().replace(" ", "+")
    try:
        if val.endswith("Z"):
            val = val[:-1] + "+00:00"
        return datetime.fromisoformat(val)
    except Exception:
        try:
            return datetime.strptime(val, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid date format for '{param_name}': '{param}'. Expected ISO-8601 or YYYY-MM-DD.",
            )


@router.get(
    "",
    response_model=PaginatedResponse[AdminCollectionRequestResponse],
    summary="List all collection requests with search, filter, and pagination",
    description="Retrieves collection requests with filtering by status, waste_type, date range, search query across user and location, and pagination.",
)
def list_all_collection_requests(
    status_filter: Optional[str] = Query(
        None, alias="status", description="Filter requests by status (e.g. submitted, accepted)"
    ),
    waste_type: Optional[str] = Query(
        None, description="Filter requests by waste category (e.g. Plastic, Organic)"
    ),
    from_date: Optional[str] = Query(
        None, description="Filter requests submitted on or after this timestamp (ISO or YYYY-MM-DD)"
    ),
    to_date: Optional[str] = Query(
        None, description="Filter requests submitted on or before this timestamp (ISO or YYYY-MM-DD)"
    ),
    start_date: Optional[str] = Query(
        None, include_in_schema=False, description="Alias for from_date"
    ),
    end_date: Optional[str] = Query(
        None, include_in_schema=False, description="Alias for to_date"
    ),
    search: Optional[str] = Query(
        None, description="Search query across user name, email, waste type, and location"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(CollectionRequest).join(User, CollectionRequest.user_id == User.id)

    # 1. Filter by status
    if status_filter and status_filter.strip():
        query = query.filter(CollectionRequest.status == status_filter.strip().lower())

    # 2. Filter by waste type
    if waste_type and waste_type.strip():
        query = query.filter(CollectionRequest.waste_type.ilike(waste_type.strip()))

    # 3. Filter by date range
    raw_from = from_date or start_date
    raw_to = to_date or end_date
    dt_from = parse_date_param(raw_from, "from_date")
    dt_to = parse_date_param(raw_to, "to_date")

    if dt_from:
        query = query.filter(CollectionRequest.requested_at >= dt_from)
    if dt_to:
        query = query.filter(CollectionRequest.requested_at <= dt_to)

    # 4. Search across user name, email, waste type, and location
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.name.ilike(pattern),
                User.email.ilike(pattern),
                CollectionRequest.waste_type.ilike(pattern),
                CollectionRequest.location.ilike(pattern),
            )
        )

    # 5. Pagination
    total = query.count()
    offset = (page - 1) * limit
    items = query.order_by(CollectionRequest.requested_at.desc()).offset(offset).limit(limit).all()
    return PaginatedResponse.create(items=items, page=page, limit=limit, total=total)


@router.get(
    "/{request_id}",
    response_model=AdminCollectionRequestResponse,
    summary="Get detailed collection request by ID",
    description="Retrieves complete collection request information including associated user details.",
)
def get_admin_collection_request(
    request_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    req = (
        db.query(CollectionRequest)
        .filter(CollectionRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection request not found.",
        )
    return req


@router.patch(
    "/{request_id}/accept",
    response_model=AdminCollectionRequestResponse,
    summary="Accept a submitted collection request",
    description="Transitions a request from 'submitted' to 'accepted'.",
)
def accept_collection_request(
    request_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    req = (
        db.query(CollectionRequest)
        .filter(CollectionRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection request not found.",
        )

    validate_status_transition(req.status, CollectionStatus.ACCEPTED.value)

    req.status = CollectionStatus.ACCEPTED.value
    db.commit()
    db.refresh(req)
    return req


@router.patch(
    "/{request_id}/reject",
    response_model=AdminCollectionRequestResponse,
    summary="Reject a collection request",
    description="Transitions a request to 'rejected' with an optional rejection reason.",
)
def reject_collection_request(
    request_id: int,
    payload: Optional[RejectRequestPayload] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    req = (
        db.query(CollectionRequest)
        .filter(CollectionRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection request not found.",
        )

    validate_status_transition(req.status, CollectionStatus.REJECTED.value)

    req.status = CollectionStatus.REJECTED.value
    if payload and payload.reason:
        reason_note = f"[Rejection Reason]: {payload.reason.strip()}"
        req.additional_notes = (
            f"{req.additional_notes}\n{reason_note}"
            if req.additional_notes
            else reason_note
        )

    db.commit()
    db.refresh(req)
    return req


@router.patch(
    "/{request_id}/schedule",
    response_model=AdminCollectionRequestResponse,
    summary="Schedule an accepted collection request",
    description="Transitions a request from 'accepted' to 'scheduled' and assigns the pickup date/time.",
)
def schedule_collection_request(
    request_id: int,
    payload: ScheduleRequestPayload,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    req = (
        db.query(CollectionRequest)
        .filter(CollectionRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection request not found.",
        )

    validate_status_transition(req.status, CollectionStatus.SCHEDULED.value)

    req.status = CollectionStatus.SCHEDULED.value
    req.scheduled_date = payload.scheduled_date
    db.commit()
    db.refresh(req)
    return req


@router.patch(
    "/{request_id}/collect",
    response_model=AdminCollectionRequestResponse,
    summary="Mark collection request as collected",
    description="Transitions a request from 'scheduled' to 'collected'.",
)
def mark_collection_as_collected(
    request_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    req = (
        db.query(CollectionRequest)
        .filter(CollectionRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection request not found.",
        )

    validate_status_transition(req.status, CollectionStatus.COLLECTED.value)

    req.status = CollectionStatus.COLLECTED.value
    db.commit()
    db.refresh(req)
    return req


@router.patch(
    "/{request_id}/complete",
    response_model=AdminCollectionRequestResponse,
    summary="Mark collection request as completed",
    description="Transitions a request from 'collected' to 'completed' and automatically stamps the completion date.",
)
def complete_collection_request(
    request_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    req = (
        db.query(CollectionRequest)
        .filter(CollectionRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection request not found.",
        )

    validate_status_transition(req.status, CollectionStatus.COMPLETED.value)

    req.status = CollectionStatus.COMPLETED.value
    req.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    return req
