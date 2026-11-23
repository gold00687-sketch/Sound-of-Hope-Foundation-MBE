import mimetypes
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infrastructure.database.transaction import atomic
from app.infrastructure.storage.storage import get_storage
from app.infrastructure.storage.upload_validation import (
    ALLOWED_DOCUMENT_TYPES,
    ALLOWED_IMAGE_TYPES,
    validate_document,
    validate_image,
)
from app.modules.media.models import MediaAsset
from app.modules.media.repository import MediaRepository


def _sniff_mime(filename: str, declared: str | None) -> str:
    if declared and declared != "application/octet-stream":
        return declared.split(";")[0].strip().lower()
    guessed, _ = mimetypes.guess_type(filename)
    return (guessed or "application/octet-stream").lower()


class MediaService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = MediaRepository(session)

    async def upload(
        self,
        file: UploadFile,
        folder: str,
        alt_text: str | None,
        uploaded_by_id: uuid.UUID,
    ) -> MediaAsset:
        mime = _sniff_mime(file.filename or "", file.content_type)

        # Route to appropriate validator based on MIME type
        if mime in ALLOWED_IMAGE_TYPES:
            await validate_image(file)
        else:
            await validate_document(file)

        # Read size before storage consumes the stream
        content = await file.read()
        file_size = len(content)
        await file.seek(0)

        storage = get_storage()
        storage_key = await storage.save(file, folder=folder)

        asset = MediaAsset(
            uploaded_by_id=uploaded_by_id,
            storage_key=storage_key,
            original_filename=file.filename or "upload",
            mime_type=mime,
            file_size=file_size,
            alt_text=alt_text,
            folder=folder,
        )
        async with atomic(self._repo._session):
            await self._repo.save(asset)
        return asset

    async def list_assets(
        self, limit: int, offset: int, folder: str | None
    ) -> tuple[list[MediaAsset], int]:
        return await self._repo.list_assets(limit, offset, folder)

    async def delete(self, asset_id: uuid.UUID) -> None:
        asset = await self._repo.get_by_id(asset_id)
        if asset is None:
            raise NotFoundError("Media asset not found.")
        storage = get_storage()
        await storage.delete(asset.storage_key)
        async with atomic(self._repo._session):
            await self._repo.delete(asset)
