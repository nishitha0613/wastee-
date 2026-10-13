import json
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, model_validator


class DisposalGuidanceResponse(BaseModel):
    category: Optional[str] = Field(None, example="Recyclable Waste")
    subtype: Optional[str] = Field(None, example="PET Plastic (#1)")
    recommended_bin: Optional[str] = Field(
        None,
        example="Dry Waste / Plastic Recycling",
    )
    bin: Optional[str] = Field(
        None,
        example="Dry Waste / Plastic Recycling",
    )
    primary_method: Optional[str] = Field(
        None,
        example="Plastic segregation and certified mechanical recycling",
    )
    recycling_methods: List[str] = Field(
        default_factory=list,
        example=[
            "Empty the bottle completely.",
            "Rinse it if needed and allow it to dry.",
            "Separate the cap and label if required by the local recycling facility.",
            "Check the resin identification code, if available, to help determine the plastic type.",
            "Place it in an authorized plastic recycling or dry-waste collection stream.",
            "If local facilities do not accept it, direct the user to an appropriate municipal collection point.",
        ],
    )
    disposal_method: str = Field(
        ...,
        example="Rinse, dry, and place into the dry recyclable stream.",
    )
    recommendation: Optional[str] = Field(
        None,
        example="Rinse, dry, and place into the dry recyclable stream.",
    )
    do: List[str] = Field(
        ...,
        example=["Rinse containers before binning", "Flatten plastic bottles"],
    )
    action_steps: Optional[List[str]] = Field(
        None,
        example=["Rinse containers before binning", "Flatten plastic bottles"],
    )
    dont: List[str] = Field(
        ...,
        example=["Never burn plastic", "Do not mix with dirty grease"],
    )
    precautions: Optional[List[str]] = Field(
        None,
        example=["Never burn plastic", "Do not mix with dirty grease"],
    )
    environmental_impact: Optional[str] = Field(
        None,
        example="Recycling plastic conserves finite petroleum reserves and reduces emissions.",
    )
    recyclable: bool = Field(..., example=True)
    collection_recommended: bool = Field(..., example=False)


class WasteReportBase(BaseModel):
    image_path: Optional[str] = Field(None, example="/uploads/sample-bottle.jpg")
    waste_type: Optional[str] = Field(None, example="Plastic")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, example=0.94)
    description: Optional[str] = Field(None, example="Clear plastic bottle.")


class WasteReportCreate(WasteReportBase):
    user_id: int = Field(..., example=1)


class WasteIdentificationResponse(BaseModel):
    id: int
    waste_type: str
    confidence: float
    image_path: str
    category: Optional[str] = None
    recommended_bin: Optional[str] = None
    subtype: Optional[str] = None
    guidance: Optional[DisposalGuidanceResponse] = None
    recommendation: Optional[DisposalGuidanceResponse] = None
    created_at: datetime
    is_low_confidence: Optional[bool] = False
    message: Optional[str] = None
    model_used: Optional[str] = None

    class Config:
        from_attributes = True


class WasteReportResponse(BaseModel):
    id: int
    user_id: int
    waste_type: Optional[str] = None
    confidence: Optional[float] = None
    image_path: Optional[str] = None
    description: Optional[str] = None
    guidance: Optional[DisposalGuidanceResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def parse_guidance_field(cls, data: Any) -> Any:
        # Deserialize JSON string from disposal_guidance column
        if hasattr(data, "disposal_guidance"):
            raw_guidance = getattr(data, "disposal_guidance", None)
            guidance_dict = None
            if raw_guidance and isinstance(raw_guidance, str):
                try:
                    parsed = json.loads(raw_guidance)
                    if isinstance(parsed, dict) and "disposal_method" in parsed:
                        guidance_dict = parsed
                except Exception:
                    guidance_dict = None
            return {
                "id": data.id,
                "user_id": data.user_id,
                "waste_type": data.waste_type,
                "confidence": data.confidence,
                "image_path": data.image_path,
                "description": data.description,
                "guidance": guidance_dict,
                "created_at": data.created_at,
            }
        elif isinstance(data, dict) and "disposal_guidance" in data:
            raw_guidance = data.get("disposal_guidance")
            if raw_guidance and isinstance(raw_guidance, str):
                try:
                    parsed = json.loads(raw_guidance)
                    if isinstance(parsed, dict) and "disposal_method" in parsed:
                        data["guidance"] = parsed
                    else:
                        data["guidance"] = None
                except Exception:
                    data["guidance"] = None
        return data


class DeleteReportResponse(BaseModel):
    message: str = Field(..., example="Waste report deleted successfully.")
    id: int = Field(..., example=1)
