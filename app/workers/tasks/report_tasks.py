import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def generate_programme_report(self, *, programme_id: str, requested_by: str) -> None:
    try:
        logger.info("report_generation_started", programme_id=programme_id)
        # Report generation implementation
        logger.info("report_generation_complete", programme_id=programme_id)
    except Exception as exc:
        logger.error("report_generation_failed", programme_id=programme_id, error=str(exc))
        raise self.retry(exc=exc)
