import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db
from app.routers.admin_collection import router as admin_collection_router
from app.routers.auth import router as auth_router
from app.routers.collection import router as collection_router
from app.routers.health import router as health_router
from app.routers.waste import router as waste_router

# Configure centralized backend logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    logger.info("Starting Waste Disposal Assistant backend...")
    init_db()
    # Ensure upload directory exists
    _ = settings.upload_path
    logger.info("Backend initialized successfully.")
    yield
    logger.info("Shutting down Waste Disposal Assistant backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for Smart AI Assistant for Waste Disposal Guidance",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded static images safely
app.mount(
    "/uploads",
    StaticFiles(directory=settings.upload_path),
    name="uploads",
)

# Mount all API routers under /api
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(waste_router, prefix=settings.API_V1_STR)
app.include_router(collection_router, prefix=settings.API_V1_STR)
app.include_router(admin_collection_router, prefix=settings.API_V1_STR)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unhandled exceptions to prevent stack traces, database internals,
    or filesystem paths from leaking to client responses.
    """
    logger.error(
        "Unhandled server error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


@app.get("/", tags=["Root"])
def root():
    """Root endpoint welcoming developers and pointing to documentation."""
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "uploads": "/uploads",
    }
