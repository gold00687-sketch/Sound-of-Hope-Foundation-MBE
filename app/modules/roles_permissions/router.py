import uuid

from fastapi import APIRouter, status

from app.core.dependencies import SessionDep
from app.core.permissions import Permission
from app.modules.identity.dependencies import CurrentUser, require_permission
from app.modules.roles_permissions.schemas import (
    AssignPermissionsRequest,
    AssignRoleRequest,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UserRoleResponse,
)
from app.modules.roles_permissions.service import RolesPermissionsService

router = APIRouter()


@router.get("", response_model=list[RoleResponse],
            dependencies=[require_permission(Permission.ROLE_READ)])
async def list_roles(session: SessionDep):
    return await RolesPermissionsService(session).list_roles()


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[require_permission(Permission.ROLE_MANAGE)])
async def create_role(body: RoleCreate, session: SessionDep):
    return await RolesPermissionsService(session).create_role(body)


@router.patch("/{role_id}", response_model=RoleResponse,
              dependencies=[require_permission(Permission.ROLE_MANAGE)])
async def update_role(role_id: uuid.UUID, body: RoleUpdate, session: SessionDep):
    return await RolesPermissionsService(session).update_role(role_id, body)


@router.put("/{role_id}/permissions", response_model=RoleResponse,
            dependencies=[require_permission(Permission.PERMISSION_MANAGE)])
async def assign_permissions(
    role_id: uuid.UUID, body: AssignPermissionsRequest, session: SessionDep
):
    return await RolesPermissionsService(session).assign_permissions(role_id, body)


@router.post("/users/{user_id}/assign", status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[require_permission(Permission.ROLE_MANAGE)])
async def assign_role_to_user(
    user_id: uuid.UUID,
    body: AssignRoleRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    await RolesPermissionsService(session).assign_role_to_user(
        user_id, body.role_name, current_user.id
    )


@router.delete("/users/{user_id}/remove", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[require_permission(Permission.ROLE_MANAGE)])
async def remove_role_from_user(
    user_id: uuid.UUID, body: AssignRoleRequest, session: SessionDep
) -> None:
    await RolesPermissionsService(session).remove_role_from_user(user_id, body.role_name)


@router.get("/users/{user_id}", response_model=list[UserRoleResponse],
            dependencies=[require_permission(Permission.ROLE_READ)])
async def get_user_roles(user_id: uuid.UUID, session: SessionDep):
    user_roles = await RolesPermissionsService(session).list_user_roles(user_id)
    return [
        UserRoleResponse(
            user_id=ur.user_id,
            role_id=ur.role_id,
            role_name=ur.role.name,
            created_at=ur.created_at,
        )
        for ur in user_roles
    ]
