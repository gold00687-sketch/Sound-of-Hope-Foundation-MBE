import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import (
    CACHE_PREFIX_EMAIL_VERIFY,
    CACHE_PREFIX_PASSWORD_RESET,
    EMAIL_VERIFY_TOKEN_TTL,
    PASSWORD_RESET_TOKEN_TTL,
    AuditAction,
    TokenType,
)
from app.core.exceptions import (
    AccountInactiveError,
    AccountLockedError,
    AuthenticationError,
    ConflictError,
    InvalidCredentialsError,
    NotFoundError,
    TokenInvalidError,
)
from app.core.security import (
    create_token,
    hash_password,
    password_needs_rehash,
    verify_password,
)
from app.infrastructure.cache.redis import (
    blacklist_token,
    cache_delete,
    cache_get,
    cache_set,
    is_token_blacklisted,
)
from app.infrastructure.database.transaction import atomic
from app.modules.identity.models import AuthEvent, RefreshToken, User, UserProfile
from app.modules.identity.repository import (
    AuthEventRepository,
    RefreshTokenRepository,
    RoleRepository,
    UserRepository,
)
from app.modules.identity.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.utils.helpers import generate_token


class IdentityService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._tokens = RefreshTokenRepository(session)
        self._roles = RoleRepository(session)
        self._events = AuthEventRepository(session)
        self._settings = get_settings()

    async def register(
        self, data: RegisterRequest, ip: str | None = None
    ) -> User:
        existing = await self._users.get_by_email(data.email)
        if existing:
            raise ConflictError("An account with this email already exists.")

        if data.phone:
            phone_user = await self._users.get_by_phone(data.phone)
            if phone_user:
                raise ConflictError("An account with this phone number already exists.")

        user = User(
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
        )
        profile = UserProfile(
            user=user,
            first_name=data.first_name,
            last_name=data.last_name,
        )

        async with atomic(self._session):
            await self._users.create(user, profile)
            await self._events.record(
                AuthEvent(
                    user_id=user.id,
                    email=user.email,
                    action=AuditAction.CREATE,
                    ip_address=ip,
                )
            )

        await self._send_verification_email(user)
        return user

    async def login(
        self,
        data: LoginRequest,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponse:
        user = await self._users.get_by_email(data.email)

        if user is None:
            async with atomic(self._session):
                await self._events.record(
                    AuthEvent(action=AuditAction.LOGIN_FAILED, email=data.email, ip_address=ip)
                )
            raise InvalidCredentialsError()

        if user.is_locked():
            raise AccountLockedError()

        if not verify_password(data.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self._settings.max_login_attempts:
                user.locked_until = datetime.now(UTC) + timedelta(
                    minutes=self._settings.lockout_duration_minutes
                )
                await self._events.record(
                    AuthEvent(
                        user_id=user.id,
                        email=user.email,
                        action=AuditAction.ACCOUNT_LOCKED,
                        ip_address=ip,
                    )
                )
            else:
                await self._events.record(
                    AuthEvent(
                        user_id=user.id,
                        email=user.email,
                        action=AuditAction.LOGIN_FAILED,
                        ip_address=ip,
                    )
                )
            async with atomic(self._session):
                await self._users.save(user)
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountInactiveError()

        # Successful login — reset failure counter
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(UTC)

        if password_needs_rehash(user.password_hash):
            user.password_hash = hash_password(data.password)

        permissions = await self._users.get_permissions_for_user(user.id)

        raw_refresh = generate_token(64)
        token_hash = hashlib.sha256(raw_refresh.encode()).hexdigest()
        refresh_expires = datetime.now(UTC) + timedelta(
            days=self._settings.refresh_token_expire_days
        )
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=refresh_expires,
            ip_address=ip,
            user_agent=user_agent,
        )

        async with atomic(self._session):
            await self._users.save(user)
            await self._tokens.create(refresh_token)
            await self._events.record(
                AuthEvent(
                    user_id=user.id,
                    email=user.email,
                    action=AuditAction.LOGIN,
                    ip_address=ip,
                    user_agent=user_agent,
                )
            )

        access_token = create_token(
            subject=str(user.id),
            token_type=TokenType.ACCESS,
            extra_claims={"email": user.email, "permissions": permissions},
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            expires_in=self._settings.access_token_expire_minutes * 60,
        )

    async def refresh(
        self, raw_refresh_token: str, ip: str | None = None
    ) -> TokenResponse:
        stored = await self._tokens.get_by_token(raw_refresh_token)

        if stored is None or not stored.is_valid():
            raise TokenInvalidError("Refresh token is invalid or has expired.")

        user = await self._users.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            raise AccountInactiveError()

        permissions = await self._users.get_permissions_for_user(user.id)

        raw_new_refresh = generate_token(64)
        new_token_hash = hashlib.sha256(raw_new_refresh.encode()).hexdigest()
        new_refresh = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=stored.expires_at,
            ip_address=ip,
        )

        async with atomic(self._session):
            stored.revoked_at = datetime.now(UTC)
            stored.replaced_by_id = None  # will be set after flush
            await self._tokens.create(new_refresh)
            stored.replaced_by_id = new_refresh.id

        access_token = create_token(
            subject=str(user.id),
            token_type=TokenType.ACCESS,
            extra_claims={"email": user.email, "permissions": permissions},
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_new_refresh,
            expires_in=self._settings.access_token_expire_minutes * 60,
        )

    async def logout(
        self,
        raw_refresh_token: str,
        access_token_jti: str | None = None,
        access_token_ttl: int | None = None,
    ) -> None:
        stored = await self._tokens.get_by_token(raw_refresh_token)
        if stored and stored.revoked_at is None:
            async with atomic(self._session):
                await self._tokens.revoke(stored)

        if access_token_jti and access_token_ttl:
            await blacklist_token(access_token_jti, ttl=access_token_ttl)

    async def logout_all(self, user_id: uuid.UUID) -> None:
        async with atomic(self._session):
            await self._tokens.revoke_all_for_user(user_id)

    async def verify_email(self, token: str) -> None:
        stored = await cache_get(f"{CACHE_PREFIX_EMAIL_VERIFY}{token}")
        if stored is None:
            raise TokenInvalidError("Email verification token is invalid or has expired.")

        user = await self._users.get_by_id(uuid.UUID(stored))
        if user is None:
            raise NotFoundError()

        async with atomic(self._session):
            user.is_email_verified = True
            await self._users.save(user)
            await self._events.record(
                AuthEvent(
                    user_id=user.id,
                    email=user.email,
                    action=AuditAction.EMAIL_VERIFIED,
                )
            )

        await cache_delete(f"{CACHE_PREFIX_EMAIL_VERIFY}{token}")

    async def request_password_reset(self, email: str) -> None:
        # Always return success — never confirm whether an email exists
        user = await self._users.get_by_email(email)
        if user is None:
            return

        token = generate_token(48)
        await cache_set(
            f"{CACHE_PREFIX_PASSWORD_RESET}{token}",
            str(user.id),
            ttl=PASSWORD_RESET_TOKEN_TTL,
        )
        # Dispatch email via worker — integration point
        from app.workers.tasks.email_tasks import send_password_reset_email
        send_password_reset_email.delay(email=user.email, token=token)

    async def confirm_password_reset(self, token: str, new_password: str) -> None:
        stored = await cache_get(f"{CACHE_PREFIX_PASSWORD_RESET}{token}")
        if stored is None:
            raise TokenInvalidError("Password reset token is invalid or has expired.")

        user = await self._users.get_by_id(uuid.UUID(stored))
        if user is None:
            raise NotFoundError()

        async with atomic(self._session):
            user.password_hash = hash_password(new_password)
            user.failed_login_attempts = 0
            user.locked_until = None
            await self._users.save(user)
            await self._tokens.revoke_all_for_user(user.id)
            await self._events.record(
                AuthEvent(
                    user_id=user.id,
                    email=user.email,
                    action=AuditAction.PASSWORD_RESET,
                )
            )

        await cache_delete(f"{CACHE_PREFIX_PASSWORD_RESET}{token}")

    async def change_password(
        self, user_id: uuid.UUID, current_password: str, new_password: str
    ) -> None:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError()

        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect.")

        async with atomic(self._session):
            user.password_hash = hash_password(new_password)
            await self._users.save(user)
            await self._tokens.revoke_all_for_user(user_id)
            await self._events.record(
                AuthEvent(
                    user_id=user.id,
                    email=user.email,
                    action=AuditAction.PASSWORD_CHANGED,
                )
            )

    async def _send_verification_email(self, user: User) -> None:
        token = generate_token(48)
        await cache_set(
            f"{CACHE_PREFIX_EMAIL_VERIFY}{token}",
            str(user.id),
            ttl=EMAIL_VERIFY_TOKEN_TTL,
        )
        from app.workers.tasks.email_tasks import send_email_verification
        send_email_verification.delay(email=user.email, token=token)

    async def resend_verification(self, email: str) -> None:
        user = await self._users.get_by_email(email)
        if user and not user.is_email_verified:
            await self._send_verification_email(user)
