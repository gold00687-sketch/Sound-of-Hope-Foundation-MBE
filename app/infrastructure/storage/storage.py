import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import StorageError
from app.core.logging import get_logger

logger = get_logger(__name__)


class LocalStorage:
    """Development-grade local file storage."""

    def __init__(self, base_path: str) -> None:
        self.base = Path(base_path)

    def _resolve(self, key: str) -> Path:
        return self.base / key

    async def save(self, file: UploadFile, folder: str = "uploads") -> str:
        suffix = Path(file.filename or "file").suffix
        key = f"{folder}/{uuid.uuid4().hex}{suffix}"
        dest = self._resolve(key)
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            content = await file.read()
            dest.write_bytes(content)
            await file.seek(0)
        except OSError as exc:
            raise StorageError(f"Failed to write file: {exc}") from exc
        return key

    async def delete(self, key: str) -> None:
        path = self._resolve(key)
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            logger.warning("storage_delete_failed", key=key, error=str(exc))

    def public_url(self, key: str) -> str:
        return f"/media/{key}"


def get_storage() -> LocalStorage:
    settings = get_settings()
    if settings.storage_backend == "local":
        return LocalStorage(settings.storage_local_path)
    # S3 integration point — add S3Storage class when credentials are available
    raise StorageError(f"Unsupported storage backend: {settings.storage_backend}")
