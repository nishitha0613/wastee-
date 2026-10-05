from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="ok", description="Current service health status")
    message: str = Field(
        ...,
        example="Smart Waste Management API is running",
        description="Informational status message",
    )
