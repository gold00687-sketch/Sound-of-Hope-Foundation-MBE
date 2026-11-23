"""SMTP email sender.

For production, replace the SMTP implementation with a provider such as
SendGrid, Mailgun, or Amazon SES by swapping this module only.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError

logger = structlog.get_logger(__name__)


def send_email(*, to: str, subject: str, body: str, html_body: str | None = None) -> None:
    settings = get_settings()
    if not settings.smtp_host:
        logger.warning("smtp_not_configured", to=to, subject=subject)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to
    msg.attach(MIMEText(body, "plain"))
    if html_body:
        msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.sendmail(settings.smtp_from_email, to, msg.as_string())
    except smtplib.SMTPException as exc:
        logger.error("email_send_failed", to=to, subject=subject, error=str(exc))
        raise ExternalServiceError("Email delivery failed.") from exc
