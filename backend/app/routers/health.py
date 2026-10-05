from fastapi import APIRouter
from app.schemas.health import HealthCheckResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check endpoint",
    description="Returns the operational status of the Smart Waste Management API.",
)
def health_check():
    return {
        "status": "ok",
        "message": "Smart Waste Management API is running",
    }
