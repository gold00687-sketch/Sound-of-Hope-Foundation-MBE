from typing import Any


class AppError(Exception):
    """Base class for all application-level errors."""

    status_code: int = 500
    error_code: str = "internal_error"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, **context: Any) -> None:
        self.message = message or self.__class__.message
        self.context = context
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"
    message = "The requested resource was not found."


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"
    message = "A conflict occurred with the current state of the resource."


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"
    message = "The provided data failed validation."


class AuthenticationError(AppError):
    status_code = 401
    error_code = "authentication_error"
    message = "Authentication is required."


class InvalidCredentialsError(AuthenticationError):
    error_code = "invalid_credentials"
    message = "Invalid email or password."


class AccountLockedError(AuthenticationError):
    error_code = "account_locked"
    message = "Account is temporarily locked due to too many failed attempts."


class AccountInactiveError(AuthenticationError):
    error_code = "account_inactive"
    message = "Account is not active."


class TokenExpiredError(AuthenticationError):
    error_code = "token_expired"
    message = "The token has expired."


class TokenInvalidError(AuthenticationError):
    error_code = "token_invalid"
    message = "The token is invalid."


class PermissionDeniedError(AppError):
    status_code = 403
    error_code = "permission_denied"
    message = "You do not have permission to perform this action."


class RateLimitError(AppError):
    status_code = 429
    error_code = "rate_limit_exceeded"
    message = "Too many requests. Please try again later."


class StorageError(AppError):
    status_code = 500
    error_code = "storage_error"
    message = "A storage operation failed."


class ExternalServiceError(AppError):
    status_code = 502
    error_code = "external_service_error"
    message = "An external service call failed."


class DuplicateEnrolmentError(ConflictError):
    error_code = "duplicate_enrolment"
    message = "The participant is already enrolled in this programme."


class PaymentError(AppError):
    status_code = 402
    error_code = "payment_error"
    message = "Payment processing failed."
