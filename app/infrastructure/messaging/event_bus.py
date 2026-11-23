from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

Handler = Callable[[dict[str, Any]], Awaitable[None]]

_handlers: dict[str, list[Handler]] = defaultdict(list)


def subscribe(event_name: str, handler: Handler) -> None:
    _handlers[event_name].append(handler)


async def publish(event_name: str, payload: dict[str, Any]) -> None:
    for handler in _handlers.get(event_name, []):
        try:
            await handler(payload)
        except Exception as exc:
            logger.error(
                "event_handler_failed",
                event=event_name,
                handler=handler.__name__,
                error=str(exc),
            )
