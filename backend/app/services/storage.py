import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.config import get_settings

logger = logging.getLogger("app.services.storage")
settings = get_settings()


class BaseStorageService(ABC):
    """Abstract interface defining file storage operations.
    Enables pluggable backends (Local Disk, AWS S3, Google Cloud Storage, Azure Blob).
    """

    @abstractmethod
    async def save_image(self, content: bytes, filename: str) -> str:
        """Persist image binary data and return access path or public URL."""
        pass

    @abstractmethod
    async def delete_image(self, image_path: str) -> bool:
        """Remove image from storage. Returns True if deleted or already absent."""
        pass

    @abstractmethod
    def get_full_url(self, image_path: str, base_url: Optional[str] = None) -> str:
        """Construct fully-qualified accessible URL for client consumption."""
        pass


class LocalStorageService(BaseStorageService):
    """Local filesystem storage provider for development and single-host deployments."""

    def __init__(self, upload_directory: Optional[Path] = None):
        self.upload_dir = upload_directory or settings.upload_path
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_image(self, content: bytes, filename: str) -> str:
        # Sanitize filename: strip directory parts to prevent path traversal
        safe_name = Path(filename).name
        target_path = self.upload_dir / safe_name

        # Ensure target remains inside designated upload folder
        if not target_path.resolve().is_relative_to(self.upload_dir.resolve()):
            raise ValueError(f"Path traversal detected for filename: {filename}")

        target_path.write_bytes(content)
        logger.info(f"Image stored locally at {target_path} ({len(content)} bytes)")
        return f"/uploads/{safe_name}"

    async def delete_image(self, image_path: str) -> bool:
        if not image_path:
            return False

        filename = Path(image_path).name
        target_path = self.upload_dir / filename

        # Security check: verify path resolution
        try:
            if target_path.resolve().is_relative_to(self.upload_dir.resolve()) and target_path.exists():
                target_path.unlink()
                logger.info(f"Deleted local file: {target_path}")
                return True
        except Exception as exc:
            logger.warning(f"Failed to delete local file {target_path}: {exc}")
        return False

    def get_full_url(self, image_path: str, base_url: Optional[str] = None) -> str:
        if not image_path:
            return ""
        if image_path.startswith("http://") or image_path.startswith("https://"):
            return image_path
        if base_url:
            return f"{base_url.rstrip('/')}/{image_path.lstrip('/')}"
        return image_path


# Dependency injector for FastAPI routes
def get_storage_service() -> BaseStorageService:
    """Returns the configured storage service provider."""
    # Pluggable: easily branch on settings.STORAGE_TYPE == 's3' when adding cloud storage
    return LocalStorageService()
