from enum import StrEnum


class Permission(StrEnum):
    # User management
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"

    # Roles & permissions
    ROLE_READ = "role:read"
    ROLE_MANAGE = "role:manage"
    PERMISSION_MANAGE = "permission:manage"

    # Organisation
    ORGANISATION_READ = "organisation:read"
    ORGANISATION_UPDATE = "organisation:update"

    # Staff
    STAFF_READ = "staff:read"
    STAFF_CREATE = "staff:create"
    STAFF_UPDATE = "staff:update"
    STAFF_DELETE = "staff:delete"

    # Participants
    PARTICIPANT_READ = "participant:read"
    PARTICIPANT_CREATE = "participant:create"
    PARTICIPANT_UPDATE = "participant:update"
    PARTICIPANT_DELETE = "participant:delete"

    # Programmes
    PROGRAMME_READ = "programme:read"
    PROGRAMME_CREATE = "programme:create"
    PROGRAMME_UPDATE = "programme:update"
    PROGRAMME_DELETE = "programme:delete"
    PROGRAMME_MANAGE = "programme:manage"

    # Applications
    APPLICATION_READ = "application:read"
    APPLICATION_REVIEW = "application:review"
    APPLICATION_MANAGE = "application:manage"

    # Enrolments
    ENROLMENT_READ = "enrolment:read"
    ENROLMENT_CREATE = "enrolment:create"
    ENROLMENT_UPDATE = "enrolment:update"
    ENROLMENT_DELETE = "enrolment:delete"

    # Education
    COURSE_READ = "course:read"
    COURSE_MANAGE = "course:manage"
    CLASS_READ = "class:read"
    CLASS_MANAGE = "class:manage"
    ATTENDANCE_READ = "attendance:read"
    ATTENDANCE_RECORD = "attendance:record"
    ASSESSMENT_READ = "assessment:read"
    ASSESSMENT_MANAGE = "assessment:manage"
    CERTIFICATE_ISSUE = "certificate:issue"

    # Events
    EVENT_READ = "event:read"
    EVENT_CREATE = "event:create"
    EVENT_MANAGE = "event:manage"

    # Content
    CONTENT_READ = "content:read"
    CONTENT_CREATE = "content:create"
    CONTENT_PUBLISH = "content:publish"
    CONTENT_MANAGE = "content:manage"
    MEDIA_UPLOAD = "media:upload"
    MEDIA_MANAGE = "media:manage"

    # Finance
    FINANCE_READ = "finance:read"
    FINANCE_MANAGE = "finance:manage"
    DONATION_READ = "donation:read"
    DONATION_MANAGE = "donation:manage"
    PAYMENT_READ = "payment:read"
    PAYMENT_MANAGE = "payment:manage"
    BOOKING_READ = "booking:read"
    BOOKING_MANAGE = "booking:manage"
    EXPENSE_READ = "expense:read"
    EXPENSE_MANAGE = "expense:manage"

    # Safeguarding — deliberately narrow
    SAFEGUARDING_READ = "safeguarding:read"
    SAFEGUARDING_MANAGE = "safeguarding:manage"
    CONSENT_READ = "consent:read"
    CONSENT_MANAGE = "consent:manage"
    REFERRAL_READ = "referral:read"
    REFERRAL_MANAGE = "referral:manage"

    # Research & library
    LIBRARY_READ = "library:read"
    LIBRARY_MANAGE = "library:manage"
    PUBLICATION_READ = "publication:read"
    PUBLICATION_MANAGE = "publication:manage"
    RESEARCH_READ = "research:read"
    RESEARCH_MANAGE = "research:manage"

    # Reporting & analytics
    REPORT_READ = "report:read"
    REPORT_GENERATE = "report:generate"
    ANALYTICS_READ = "analytics:read"

    # Audit
    AUDIT_READ = "audit:read"

    # Notifications
    NOTIFICATION_SEND = "notification:send"
    NOTIFICATION_MANAGE = "notification:manage"

    # System administration
    SYSTEM_ADMIN = "system:admin"


# Convenience groupings used when seeding roles
ADMIN_PERMISSIONS: frozenset[Permission] = frozenset(Permission)

PROGRAMME_MANAGER_PERMISSIONS: frozenset[Permission] = frozenset({
    Permission.PARTICIPANT_READ,
    Permission.PARTICIPANT_CREATE,
    Permission.PARTICIPANT_UPDATE,
    Permission.PROGRAMME_READ,
    Permission.PROGRAMME_CREATE,
    Permission.PROGRAMME_UPDATE,
    Permission.PROGRAMME_MANAGE,
    Permission.APPLICATION_READ,
    Permission.APPLICATION_REVIEW,
    Permission.APPLICATION_MANAGE,
    Permission.ENROLMENT_READ,
    Permission.ENROLMENT_CREATE,
    Permission.ENROLMENT_UPDATE,
    Permission.COURSE_READ,
    Permission.COURSE_MANAGE,
    Permission.CLASS_READ,
    Permission.CLASS_MANAGE,
    Permission.ATTENDANCE_READ,
    Permission.ATTENDANCE_RECORD,
    Permission.ASSESSMENT_READ,
    Permission.ASSESSMENT_MANAGE,
    Permission.CERTIFICATE_ISSUE,
    Permission.EVENT_READ,
    Permission.EVENT_CREATE,
    Permission.REPORT_READ,
    Permission.REPORT_GENERATE,
})

INSTRUCTOR_PERMISSIONS: frozenset[Permission] = frozenset({
    Permission.PARTICIPANT_READ,
    Permission.COURSE_READ,
    Permission.CLASS_READ,
    Permission.ATTENDANCE_READ,
    Permission.ATTENDANCE_RECORD,
    Permission.ASSESSMENT_READ,
    Permission.ASSESSMENT_MANAGE,
})

STAFF_PERMISSIONS: frozenset[Permission] = frozenset({
    Permission.PARTICIPANT_READ,
    Permission.PROGRAMME_READ,
    Permission.ENROLMENT_READ,
    Permission.COURSE_READ,
    Permission.CLASS_READ,
    Permission.ATTENDANCE_READ,
    Permission.EVENT_READ,
    Permission.CONTENT_READ,
    Permission.LIBRARY_READ,
    Permission.PUBLICATION_READ,
})

PARTICIPANT_PERMISSIONS: frozenset[Permission] = frozenset({
    Permission.PROGRAMME_READ,
    Permission.COURSE_READ,
    Permission.CLASS_READ,
    Permission.EVENT_READ,
    Permission.CONTENT_READ,
    Permission.LIBRARY_READ,
    Permission.PUBLICATION_READ,
})
