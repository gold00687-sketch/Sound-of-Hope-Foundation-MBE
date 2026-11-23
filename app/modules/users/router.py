import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.users.schemas import (
    AdminUserListItem,
    EmergencyContactCreate,
    EmergencyContactResponse,
    ProfileUpdateRequest,
    UserAddressCreate,
    UserAddressResponse,
    UserDetailResponse,
)
from app.modules.users.service import UserService
from app.utils.pagination import Page, PaginationParams

router = APIRouter()


def _svc(session: SessionDep) -> UserService:
    return UserService(session)


@router.get("/me", response_model=UserDetailResponse)
async def get_my_profile(current_user: CurrentUser) -> UserDetailResponse:
    return UserDetailResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_email_verified=current_user.is_email_verified,
        first_name=current_user.profile.first_name,
        last_name=current_user.profile.last_name,
        display_name=current_user.profile.display_name,
        bio=current_user.profile.bio,
        avatar_key=current_user.profile.avatar_key,
        created_at=current_user.created_at,
    )


@router.patch("/me", response_model=UserDetailResponse)
async def update_my_profile(
    body: ProfileUpdateRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> UserDetailResponse:
    svc = _svc(session)
    user = await svc.update_profile(current_user.id, body, current_user.id)
    return UserDetailResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        first_name=user.profile.first_name,
        last_name=user.profile.last_name,
        display_name=user.profile.display_name,
        bio=user.profile.bio,
        avatar_key=user.profile.avatar_key,
        created_at=user.created_at,
    )


@router.get("/me/addresses", response_model=list[UserAddressResponse])
async def my_addresses(current_user: CurrentUser, session: SessionDep):
    repo = _svc(session)._repo
    return await repo.get_addresses(current_user.id)


@router.post("/me/addresses", response_model=UserAddressResponse, status_code=status.HTTP_201_CREATED)
async def add_address(
    body: UserAddressCreate,
    current_user: CurrentUser,
    session: SessionDep,
):
    return await _svc(session).add_address(current_user.id, body)


@router.get("/me/emergency-contacts", response_model=list[EmergencyContactResponse])
async def my_emergency_contacts(current_user: CurrentUser, session: SessionDep):
    repo = _svc(session)._repo
    return await repo.get_emergency_contacts(current_user.id)


@router.post(
    "/me/emergency-contacts",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_emergency_contact(
    body: EmergencyContactCreate,
    current_user: CurrentUser,
    session: SessionDep,
):
    return await _svc(session).add_emergency_contact(current_user.id, body)


# Admin endpoints
@router.get(
    "",
    response_model=Page[AdminUserListItem],
    dependencies=[require_permission(Permission.USER_READ)],
)
async def list_users(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
):
    svc = _svc(session)
    users, total = await svc.list_users(
        pagination.limit, pagination.offset, search, is_active
    )
    items = [
        AdminUserListItem(
            id=u.id,
            email=u.email,
            first_name=u.profile.first_name,
            last_name=u.profile.last_name,
            is_active=u.is_active,
            is_email_verified=u.is_email_verified,
            created_at=u.created_at,
        )
        for u in users
    ]
    return Page.create(items, pagination, total)


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    dependencies=[require_permission(Permission.USER_READ)],
)
async def get_user(user_id: uuid.UUID, session: SessionDep):
    user = await _svc(session).get_user(user_id)
    return UserDetailResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        first_name=user.profile.first_name,
        last_name=user.profile.last_name,
        display_name=user.profile.display_name,
        bio=user.profile.bio,
        avatar_key=user.profile.avatar_key,
        created_at=user.created_at,
    )


@router.post(
    "/{user_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission(Permission.USER_MANAGE)],
)
async def deactivate_user(user_id: uuid.UUID, session: SessionDep) -> None:
    await _svc(session).deactivate_user(user_id)


@router.post(
    "/{user_id}/activate",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission(Permission.USER_MANAGE)],
)
async def activate_user(user_id: uuid.UUID, session: SessionDep) -> None:
    await _svc(session).activate_user(user_id)
