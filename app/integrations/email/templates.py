from app.core.config import get_settings


def render_verification_email(*, token: str) -> tuple[str, str]:
    settings = get_settings()
    # In production, replace with a proper templating engine (Jinja2 or similar)
    subject = "Verify your email address"
    verify_url = f"https://app.example.com/verify-email?token={token}"
    body = (
        f"Hello,\n\n"
        f"Please verify your email address by clicking the link below:\n\n"
        f"{verify_url}\n\n"
        f"This link expires in 24 hours.\n\n"
        f"If you did not create an account, please ignore this email.\n\n"
        f"— {settings.smtp_from_name}"
    )
    return subject, body


def render_password_reset_email(*, token: str) -> tuple[str, str]:
    settings = get_settings()
    subject = "Reset your password"
    reset_url = f"https://app.example.com/reset-password?token={token}"
    body = (
        f"Hello,\n\n"
        f"You requested a password reset. Click the link below to set a new password:\n\n"
        f"{reset_url}\n\n"
        f"This link expires in 1 hour.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"— {settings.smtp_from_name}"
    )
    return subject, body
