"""Email background tasks.

Actual email delivery is handled by the email integration module.
These tasks provide the Celery wrapper so delivery is decoupled from
the web request lifecycle.
"""

import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_verification(self, *, email: str, token: str) -> None:
    try:
        from app.integrations.email.sender import send_email
        from app.integrations.email.templates import render_verification_email

        subject, body = render_verification_email(token=token)
        send_email(to=email, subject=subject, body=body)
        logger.info("verification_email_sent", email=email)
    except Exception as exc:
        logger.error("verification_email_failed", email=email, error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, *, email: str, token: str) -> None:
    try:
        from app.integrations.email.sender import send_email
        from app.integrations.email.templates import render_password_reset_email

        subject, body = render_password_reset_email(token=token)
        send_email(to=email, subject=subject, body=body)
        logger.info("password_reset_email_sent", email=email)
    except Exception as exc:
        logger.error("password_reset_email_failed", email=email, error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_email(self, *, to: str, subject: str, body: str) -> None:
    try:
        from app.integrations.email.sender import send_email

        send_email(to=to, subject=subject, body=body)
    except Exception as exc:
        logger.error("notification_email_failed", to=to, error=str(exc))
        raise self.retry(exc=exc)
