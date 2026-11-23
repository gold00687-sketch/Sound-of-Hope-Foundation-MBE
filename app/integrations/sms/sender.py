"""SMS delivery integration boundary.

Configure TWILIO_* environment variables to enable Twilio.
Swap this implementation for any other provider without touching callers.
"""

import structlog

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError

logger = structlog.get_logger(__name__)


def send_sms(*, to: str, message: str) -> None:
    settings = get_settings()

    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        logger.warning("sms_provider_not_configured", to=to)
        return

    try:
        from twilio.rest import Client  # type: ignore[import]

        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        client.messages.create(
            body=message,
            from_=settings.twilio_from_number,
            to=to,
        )
        logger.info("sms_sent", to=to)
    except Exception as exc:
        logger.error("sms_send_failed", to=to, error=str(exc))
        raise ExternalServiceError("SMS delivery failed.") from exc
