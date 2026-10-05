import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.waste_report import WasteReport
from app.models.collection_request import CollectionRequest, CollectionStatus
from app.schemas.pagination import PaginatedResponse
from app.schemas.collection_request import (
    CollectionRequestCreate,
    CollectionRequestResponse,
    DeleteCollectionRequestResponse,
)
from app.utils.dependencies import get_current_user

logger = logging.getLogger("app.routers.collection")

router = APIRouter(prefix="/collection-requests", tags=["Collection Requests"])


@router.post(
    "",
    response_model=CollectionRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new collection request",
    description="Submits a collection request for identified waste. Derives waste type from referenced WasteReport and sets status to 'submitted'.",
)
def create_collection_request(
    payload: CollectionRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    final_waste_type = payload.waste_type

    # 1. If referencing a WasteReport, validate existence and ownership
    if payload.waste_report_id is not None:
        report = (
            db.query(WasteReport)
            .filter(WasteReport.id == payload.waste_report_id)
            .first()
        )
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referenced waste report not found.",
            )

        # Enforce report ownership
        if report.user_id != current_user.id:
            logger.warning(
                "User %d attempted to link report %d belonging to another user",
                current_user.id,
                report.id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only request collection for your own waste reports.",
            )

        # Derive waste type from the verified WasteReport
        if report.waste_type:
            final_waste_type = report.waste_type

        # Check if an active collection request is already linked to this report
        existing_req = (
            db.query(CollectionRequest)
            .filter(
                CollectionRequest.waste_report_id == report.id,
                CollectionRequest.status != CollectionStatus.REJECTED.value,
            )
            .first()
        )
        if existing_req:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A collection request (#{existing_req.id}) has already been submitted for this waste report.",
            )

    # 2. Ensure waste type is available
    if not final_waste_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Waste type must be provided or derived from an existing waste report.",
        )

    # 3. Create collection request with initial status = 'submitted'
    collection_request = CollectionRequest(
        user_id=current_user.id,
        waste_report_id=payload.waste_report_id,
        waste_type=final_waste_type,
        quantity=payload.quantity,
        location=payload.location.strip(),
        additional_notes=payload.additional_notes.strip() if payload.additional_notes else None,
        status=CollectionStatus.SUBMITTED.value,
    )

    db.add(collection_request)
    db.commit()
    db.refresh(collection_request)

    logger.info(
        "Collection request created: id=%d by user_id=%d for waste_type=%s",
        collection_request.id,
        current_user.id,
        collection_request.waste_type,
    )

    return collection_request


@router.get(
    "",
    response_model=PaginatedResponse[CollectionRequestResponse],
    summary="Get user's collection requests",
    description="Returns collection requests for the authenticated user, ordered newest first with pagination. Admins can view all requests.",
)
def get_collection_requests(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(CollectionRequest)
    # Normal users only see their own requests
    if current_user.role != UserRole.ADMIN.value:
        query = query.filter(CollectionRequest.user_id == current_user.id)

    total = query.count()
    offset = (page - 1) * limit
    items = query.order_by(CollectionRequest.requested_at.desc()).offset(offset).limit(limit).all()
    return PaginatedResponse.create(items=items, page=page, limit=limit, total=total)


@router.get(
    "/{request_id}",
    response_model=CollectionRequestResponse,
    summary="Get an individual collection request",
    description="Retrieves single request details. Accessible only by the owner or an admin.",
)
def get_collection_request_by_id(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid collection request ID.",
        )

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

    # Enforce authorization
    if req.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        logger.warning(
            "Unauthorized access attempt to collection request %d by user %d",
            request_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this collection request.",
        )

    return req


@router.delete(
    "/{request_id}",
    response_model=DeleteCollectionRequestResponse,
    summary="Cancel a submitted collection request",
    description="Allows a user to cancel their own collection request if it is still in 'submitted' status.",
)
def cancel_collection_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid collection request ID.",
        )

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

    # Enforce authorization
    if req.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        logger.warning(
            "Unauthorized cancellation attempt of collection request %d by user %d",
            request_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this collection request.",
        )

    # Check status rule: only 'submitted' requests can be cancelled
    if req.status != CollectionStatus.SUBMITTED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot cancel a collection request with status '{req.status}'. "
                "Only requests in 'submitted' status can be cancelled."
            ),
        )

    db.delete(req)
    db.commit()

    logger.info(
        "Collection request cancelled: id=%d by user_id=%d",
        request_id,
        current_user.id,
    )

    return {
        "message": "Collection request cancelled successfully.",
        "id": request_id,
    }
