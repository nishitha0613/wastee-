from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.waste import router as waste_router
from app.routers.collection import router as collection_router
from app.routers.admin_collection import router as admin_collection_router

__all__ = [
    "health_router",
    "auth_router",
    "waste_router",
    "collection_router",
    "admin_collection_router",
]
