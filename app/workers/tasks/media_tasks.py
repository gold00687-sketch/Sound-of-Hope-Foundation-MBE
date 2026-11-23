import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def process_uploaded_image(self, *, storage_key: str, generate_thumbnails: bool = True) -> None:
    """Resize and optimise an uploaded image in the background."""
    try:
        logger.info("image_processing_started", key=storage_key)
        # Image processing implementation goes here using Pillow
        logger.info("image_processing_complete", key=storage_key)
    except Exception as exc:
        logger.error("image_processing_failed", key=storage_key, error=str(exc))
        raise self.retry(exc=exc)
