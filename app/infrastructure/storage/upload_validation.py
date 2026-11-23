import mimetypes
from pathlib import Path

from fastapi import UploadFile

from app.core.exceptions import ValidationError

# Allowed MIME types by upload category
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
}

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/ogg",
    "audio/flac",
    "audio/aac",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/ogg",
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024       # 10 MB
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024    # 50 MB
MAX_AUDIO_SIZE = 100 * 1024 * 1024      # 100 MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024      # 500 MB


def _sniff_mime(filename: str, declared: str | None) -> str:
    """Prefer declared content type, fall back to extension sniff."""
    if declared and declared != "application/octet-stream":
        return declared.split(";")[0].strip().lower()
    guessed, _ = mimetypes.guess_type(filename)
    return (guessed or "application/octet-stream").lower()


async def validate_image(file: UploadFile) -> None:
    mime = _sniff_mime(file.filename or "", file.content_type)
    if mime not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(f"File type '{mime}' is not an accepted image format.")
    content = await file.read()
    await file.seek(0)
    if len(content) > MAX_IMAGE_SIZE:
        raise ValidationError("Image exceeds the 10 MB size limit.")


async def validate_document(file: UploadFile) -> None:
    mime = _sniff_mime(file.filename or "", file.content_type)
    if mime not in ALLOWED_DOCUMENT_TYPES:
        raise ValidationError(f"File type '{mime}' is not an accepted document format.")
    content = await file.read()
    await file.seek(0)
    if len(content) > MAX_DOCUMENT_SIZE:
        raise ValidationError("Document exceeds the 50 MB size limit.")


async def validate_audio(file: UploadFile) -> None:
    mime = _sniff_mime(file.filename or "", file.content_type)
    if mime not in ALLOWED_AUDIO_TYPES:
        raise ValidationError(f"File type '{mime}' is not an accepted audio format.")
    content = await file.read()
    await file.seek(0)
    if len(content) > MAX_AUDIO_SIZE:
        raise ValidationError("Audio file exceeds the 100 MB size limit.")
