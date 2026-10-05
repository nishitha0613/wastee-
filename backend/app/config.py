import os
from functools import lru_cache
from pathlib import Path
from typing import List, Union, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Waste Management API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./waste_management.db"

    # CORS & Web
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    # JWT Authentication
    JWT_SECRET_KEY: str = "supersecret_jwt_key_waste_management_change_in_production_32bytes"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Initial Admin Seed
    ADMIN_NAME: str = "System Administrator"
    ADMIN_EMAIL: str = "admin@ecocycle.com"
    ADMIN_PASSWORD: str = "Admin@Secure123!"

    # File Upload Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: Optional[int] = 5242880  # 5 MB in bytes (or pass in env)
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    ALLOWED_IMAGE_MIME_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    # AI / ML Classifier Configuration
    AI_CONFIDENCE_THRESHOLD: float = 0.60
    AI_MODEL_PATH: Optional[str] = "app/models_ml/waste_classifier.onnx"
    IMAGE_INPUT_SIZE: int = 224

    @property
    def max_upload_bytes(self) -> int:
        """Returns max upload size in bytes."""
        if self.MAX_UPLOAD_SIZE is not None:
            if self.MAX_UPLOAD_SIZE > 1024:
                return self.MAX_UPLOAD_SIZE
            return self.MAX_UPLOAD_SIZE * 1024 * 1024
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        """Returns the absolute Path to the uploads directory and ensures it exists."""
        base_dir = Path(__file__).resolve().parent.parent
        path = base_dir / self.UPLOAD_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def cors_origins_list(self) -> List[str]:
        origins = list(self.CORS_ORIGINS) if isinstance(self.CORS_ORIGINS, list) else [self.CORS_ORIGINS]
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        # Exclude wildcard '*' for strict CORS in production
        return [o for o in origins if o != "*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
