from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"
    LOCKED = "locked"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class ParticipantStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    WITHDRAWN = "withdrawn"


class ApplicationStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WAITLISTED = "waitlisted"
    WITHDRAWN = "withdrawn"


class EnrolmentStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"
    SUSPENDED = "suspended"


class AttendanceStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class PublishStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFIED = "email_verified"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    TOKEN_REVOKED = "token_revoked"
    PERMISSION_CHANGED = "permission_changed"
    EXPORT = "export"
    VIEW_SENSITIVE = "view_sensitive"


# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Cache key prefixes
CACHE_PREFIX_USER = "user:"
CACHE_PREFIX_SESSION = "session:"
CACHE_PREFIX_RATE_LIMIT = "rl:"
CACHE_PREFIX_EMAIL_VERIFY = "ev:"
CACHE_PREFIX_PASSWORD_RESET = "pr:"

# Token expiry (seconds)
EMAIL_VERIFY_TOKEN_TTL = 86400       # 24 hours
PASSWORD_RESET_TOKEN_TTL = 3600      # 1 hour
