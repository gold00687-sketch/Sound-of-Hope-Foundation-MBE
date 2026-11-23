from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import SessionDep
from app.modules.identity.dependencies import CurrentUser
from app.modules.identity.schemas import (
    AssignRoleRequest,
    EmailVerifyRequest,
    LoginRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    RoleResponse,
    TokenResponse,
    UserResponse,
)
from app.modules.identity.service import IdentityService

router = APIRouter()


def _ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register(
    body: RegisterRequest,
    request: Request,
    session: SessionDep,
) -> UserResponse:
    svc = IdentityService(session)
    user = await svc.register(body, ip=_ip(request))
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        first_name=user.profile.first_name,
        last_name=user.profile.last_name,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    session: SessionDep,
) -> TokenResponse:
    svc = IdentityService(session)
    return await svc.login(
        body,
        ip=_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    request: Request,
    session: SessionDep,
) -> TokenResponse:
    svc = IdentityService(session)
    return await svc.refresh(body.refresh_token, ip=_ip(request))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: RefreshRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    svc = IdentityService(session)
    await svc.logout(body.refresh_token)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    svc = IdentityService(session)
    await svc.logout_all(current_user.id)


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(body: EmailVerifyRequest, session: SessionDep) -> None:
    svc = IdentityService(session)
    await svc.verify_email(body.token)


@router.post("/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
async def resend_verification(body: PasswordResetRequest, session: SessionDep) -> None:
    svc = IdentityService(session)
    await svc.resend_verification(body.email)


@router.post("/password/change", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: PasswordChangeRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    svc = IdentityService(session)
    await svc.change_password(current_user.id, body.current_password, body.new_password)


@router.post("/password/reset", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(
    body: PasswordResetRequest,
    session: SessionDep,
) -> None:
    svc = IdentityService(session)
    await svc.request_password_reset(body.email)


@router.post("/password/reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_password_reset(
    body: PasswordResetConfirm,
    session: SessionDep,
) -> None:
    svc = IdentityService(session)
    await svc.confirm_password_reset(body.token, body.new_password)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_email_verified=current_user.is_email_verified,
        first_name=current_user.profile.first_name,
        last_name=current_user.profile.last_name,
        created_at=current_user.created_at,
    )
