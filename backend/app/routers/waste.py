import json
import logging
import os
import uuid
from pathlib import Path
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.user import User, UserRole
from app.models.waste_report import WasteReport
from app.schemas.pagination import PaginatedResponse
from app.schemas.waste_report import (
    WasteIdentificationResponse,
    WasteReportResponse,
    DeleteReportResponse,
)
from app.services.waste_classifier import (
    BaseWasteClassifier,
    get_waste_classifier,
    classify_waste,
    CorruptedImageError,
    InvalidImageError,
)
from app.services.disposal_guidance import get_disposal_guidance
from app.services.storage import BaseStorageService, get_storage_service
from app.utils.dependencies import get_current_user

logger = logging.getLogger("app.routers.waste")

settings = get_settings()

router = APIRouter(prefix="/waste", tags=["Waste Identification & Reports"])

# Magic byte signatures for supported image types
MAGIC_SIGNATURES = {
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG\r\n\x1a\n",
    "webp": (b"RIFF", b"WEBP"),
}


def validate_image_bytes(content: bytes) -> bool:
    """Validate image format by inspecting header magic bytes."""
    if len(content) < 12:
        return False
    if content.startswith(MAGIC_SIGNATURES["jpeg"]):
        return True
    if content.startswith(MAGIC_SIGNATURES["png"]):
        return True
    if (
        content.startswith(MAGIC_SIGNATURES["webp"][0])
        and content[8:12] == MAGIC_SIGNATURES["webp"][1]
    ):
        return True
    return False


@router.post(
    "/identify",
    response_model=WasteIdentificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload image, identify waste, and receive disposal guidance",
    description="Accepts a waste image via multipart/form-data, validates type/size, classifies waste type, retrieves structured disposal guidance, and saves the report.",
)
async def identify_waste(
    file: UploadFile = File(..., description="Waste image file (JPG, PNG, WEBP, max 5MB)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    classifier: BaseWasteClassifier = Depends(get_waste_classifier),
    storage: BaseStorageService = Depends(get_storage_service),
):
    original_filename = file.filename or ""
    file_ext = Path(original_filename).suffix.lower()

    # 1. Validate file extension
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file extension '{file_ext}'. Allowed formats: "
                f"{', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
            ),
        )

    # 2. Validate MIME type
    if file.content_type not in settings.ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported MIME type '{file.content_type}'. Allowed types: "
                f"{', '.join(settings.ALLOWED_IMAGE_MIME_TYPES)}"
            ),
        )

    # 3. Read content and validate size
    max_size_bytes = settings.max_upload_bytes
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    if len(content) > max_size_bytes:
        limit_mb = round(max_size_bytes / (1024 * 1024), 1)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE
            if hasattr(status, "HTTP_413_CONTENT_TOO_LARGE")
            else 413,
            detail=(
                f"File size exceeds the limit of {limit_mb} MB. "
                f"Uploaded: {round(len(content) / (1024 * 1024), 2)} MB."
            ),
        )

    # 4. Validate magic byte image signatures
    if not validate_image_bytes(content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file content does not match a valid image format (JPEG, PNG, or WEBP).",
        )

    # 5. Generate unique safe filename
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"

    # 6. Save image using storage service
    try:
        relative_image_path = await storage.save_image(content, unique_filename)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write image to storage: {str(exc)}",
        )

    # 7. Classify the waste image with error handling
    save_path = settings.upload_path / unique_filename
    try:
        classification = classifier.classify(
            image_input=save_path if save_path.exists() else content,
            original_filename=original_filename,
        )
    except (CorruptedImageError, InvalidImageError) as img_exc:
        await storage.delete_image(relative_image_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(img_exc),
        )
    except Exception as exc:
        await storage.delete_image(relative_image_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification service failed: {str(exc)}",
        )

    waste_type = classification.get("waste_type", "Other")
    confidence = classification.get("confidence", 0.0)
    is_low_confidence = classification.get("is_low_confidence", False)
    message = classification.get("message")
    model_used = classification.get("model_used")
    subtype = classification.get("subtype")

    # 8. Retrieve disposal guidance and recycling methods for identified category
    guidance = get_disposal_guidance(
        waste_type,
        is_low_confidence=is_low_confidence,
        subtype=subtype,
    )

    # 9. Create and persist WasteReport record with guidance
    waste_report = WasteReport(
        user_id=current_user.id,
        image_path=relative_image_path,
        waste_type=waste_type,
        confidence=confidence,
        disposal_guidance=json.dumps(guidance),
        description=message if is_low_confidence else None,
    )

    try:
        db.add(waste_report)
        db.commit()
        db.refresh(waste_report)
    except Exception as exc:
        db.rollback()
        await storage.delete_image(relative_image_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database transaction failed while saving waste report.",
        )

    logger.info(
        f"Waste identified for user {current_user.id}: type={waste_report.waste_type} "
        f"confidence={waste_report.confidence} report_id={waste_report.id}"
    )

    # Return response including guidance, recommendation, and confidence metadata
    return {
        "id": waste_report.id,
        "waste_type": waste_report.waste_type,
        "confidence": waste_report.confidence,
        "image_path": waste_report.image_path,
        "category": guidance.get("category"),
        "recommended_bin": guidance.get("recommended_bin"),
        "subtype": guidance.get("subtype"),
        "guidance": guidance,
        "recommendation": guidance,
        "created_at": waste_report.created_at,
        "is_low_confidence": is_low_confidence,
        "message": message,
        "model_used": model_used,
    }


@router.get(
    "/reports",
    response_model=PaginatedResponse[WasteReportResponse],
    summary="Get user waste report history",
    description="Returns the authenticated user's waste reports ordered newest first with pagination. Admins can view all reports.",
)
def get_waste_reports(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(WasteReport)
    # Admins can see all reports; normal users see only their own
    if current_user.role != UserRole.ADMIN.value:
        query = query.filter(WasteReport.user_id == current_user.id)

    total = query.count()
    offset = (page - 1) * limit
    items = query.order_by(WasteReport.created_at.desc()).offset(offset).limit(limit).all()
    return PaginatedResponse.create(items=items, page=page, limit=limit, total=total)


@router.get(
    "/reports/{report_id}",
    response_model=WasteReportResponse,
    summary="Get an individual waste report by ID",
    description="Fetches a single waste report. Users can only access their own reports; admins can access any report.",
)
def get_waste_report_by_id(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if report_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Waste report ID must be a positive integer.",
        )

    report = db.query(WasteReport).filter(WasteReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found.",
        )

    # Enforce authorization: users cannot access other users' reports
    if report.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        logger.warning(
            f"Unauthorized report access attempt: user {current_user.id} tried to read report {report_id} owned by user {report.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this waste report.",
        )

    return report


@router.delete(
    "/reports/{report_id}",
    response_model=DeleteReportResponse,
    summary="Delete a waste report",
    description="Deletes a waste report and purges its stored image from storage. Users can only delete their own reports; admins can delete any.",
)
async def delete_waste_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: BaseStorageService = Depends(get_storage_service),
):
    if report_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Waste report ID must be a positive integer.",
        )

    report = db.query(WasteReport).filter(WasteReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waste report not found.",
        )

    # Enforce authorization: users cannot delete other users' reports
    if report.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        logger.warning(
            f"Unauthorized delete attempt: user {current_user.id} tried to delete report {report_id} owned by user {report.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this waste report.",
        )

    # Safely delete associated image from storage
    if report.image_path:
        await storage.delete_image(report.image_path)

    # Delete database record
    db.delete(report)
    db.commit()

    return {
        "message": "Waste report deleted successfully.",
        "id": report_id,
    }
