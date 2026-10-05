from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.models.collection_request import CollectionStatus
from app.schemas.user import UserBasicInfo


class CollectionRequestBase(BaseModel):
    waste_type: Optional[str] = Field(
        None,
        example="E-Waste",
        description="Waste category (derived automatically from WasteReport if omitted)",
    )
    quantity: Optional[str] = Field(
        None, example="2 items", description="Quantity or volume estimate"
    )
    location: str = Field(
        ...,
        min_length=3,
        max_length=500,
        example="123 Eco Street, Indiranagar, near Metro Pillar 45",
        description="Pickup location, street address, or landmark",
    )
    additional_notes: Optional[str] = Field(
        None,
        max_length=1000,
        example="Ring bell #3, box placed on porch.",
        description="Additional pickup instructions",
    )

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 3:
            raise ValueError("Location must contain at least 3 non-whitespace characters.")
        return clean

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if len(clean) == 0:
                return None
            if len(clean) > 100:
                raise ValueError("Quantity description exceeds maximum length of 100 characters.")
            return clean
        return v


class CollectionRequestCreate(CollectionRequestBase):
    waste_report_id: Optional[int] = Field(
        None, example=5, description="ID of the referenced WasteReport"
    )

    @field_validator("waste_report_id")
    @classmethod
    def validate_report_id(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("waste_report_id must be a positive integer.")
        return v


class CollectionRequestUpdate(BaseModel):
    status: Optional[CollectionStatus] = None
    scheduled_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    additional_notes: Optional[str] = None


class CollectionRequestResponse(BaseModel):
    id: int
    user_id: int
    waste_report_id: Optional[int] = None
    waste_type: str
    quantity: Optional[str] = None
    location: str
    additional_notes: Optional[str] = None
    status: str
    requested_at: datetime
    scheduled_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdminCollectionRequestResponse(BaseModel):
    id: int
    user_id: int
    user: Optional[UserBasicInfo] = None
    waste_report_id: Optional[int] = None
    waste_type: str
    quantity: Optional[str] = None
    location: str
    additional_notes: Optional[str] = None
    status: str
    requested_at: datetime
    scheduled_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScheduleRequestPayload(BaseModel):
    scheduled_date: datetime = Field(
        ...,
        example="2026-10-10T15:00:00",
        description="Date and time when collection is scheduled to occur",
    )

    @field_validator("scheduled_date")
    @classmethod
    def validate_scheduled_date(cls, v: datetime) -> datetime:
        # Normalize to UTC comparison if tz-aware
        now = datetime.now(timezone.utc)
        target = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        # Allow at most 10 minutes past to tolerate small network/clock deviations
        from datetime import timedelta
        if target < (now - timedelta(minutes=10)):
            raise ValueError("Scheduled pickup date cannot be in the past.")
        return v


class RejectRequestPayload(BaseModel):
    reason: Optional[str] = Field(
        None,
        example="Pickup location outside current municipal operational jurisdiction.",
        description="Optional reason explaining the rejection to the user",
    )


class CollectionStatsResponse(BaseModel):
    submitted: int = Field(0, description="Count of submitted requests pending review")
    accepted: int = Field(0, description="Count of accepted requests awaiting scheduling")
    scheduled: int = Field(0, description="Count of scheduled requests pending pickup")
    collected: int = Field(0, description="Count of collected requests in transit")
    completed: int = Field(0, description="Count of fully processed/completed requests")
    rejected: int = Field(0, description="Count of rejected requests")
    total: int = Field(0, description="Total count across all collection requests")


class DeleteCollectionRequestResponse(BaseModel):
    message: str = Field(..., example="Collection request cancelled successfully.")
    id: int = Field(..., example=1)
