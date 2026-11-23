import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def dispatch_in_app_notification(
    self, *, user_id: str, title: str, body: str, data: dict | None = None
) -> None:
    try:
        logger.info("in_app_notification_dispatched", user_id=user_id, title=title)
        # Persistence to notifications table happens via the notifications module service.
    except Exception as exc:
        logger.error("in_app_notification_failed", user_id=user_id, error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_notification(self, *, phone: str, message: str) -> None:
    try:
        from app.integrations.sms.sender import send_sms

        send_sms(to=phone, message=message)
        logger.info("sms_sent", phone=phone)
    except Exception as exc:
        logger.error("sms_failed", phone=phone, error=str(exc))
        raise self.retry(exc=exc)
