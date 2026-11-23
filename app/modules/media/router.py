import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.media.schemas import MediaAssetResponse
from app.modules.media.service import MediaService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


@router.post(
    "/upload",
    response_model=MediaAssetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission(Permission.MEDIA_UPLOAD)],
)
async def upload_media(
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    folder: str = Form(default="general"),
    alt_text: str | None = Form(default=None),
):
    return await MediaService(session).upload(
        file=file,
        folder=folder,
        alt_text=alt_text,
        uploaded_by_id=current_user.id,
    )


@router.get(
    "",
    response_model=Page[MediaAssetResponse],
    dependencies=[require_permission(Permission.MEDIA_MANAGE)],
)
async def list_media(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    folder: str | None = Query(default=None),
):
    items, total = await MediaService(session).list_assets(
        pagination.limit, pagination.offset, folder
    )
    return Page.create(items, pagination, total)


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission(Permission.MEDIA_MANAGE)],
)
async def delete_media(asset_id: uuid.UUID, session: SessionDep):
    await MediaService(session).delete(asset_id)
