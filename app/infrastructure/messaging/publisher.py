"""Thin wrapper that routes domain events to the internal bus or a Celery task.

For background jobs that must survive process restarts (email, SMS, reports),
publish via Celery. For lightweight in-process side-effects (audit log entries,
cache invalidation), publish directly on the event bus.
"""

from typing import Any

from app.infrastructure.messaging.event_bus import publish


async def emit(event_name: str, payload: dict[str, Any]) -> None:
    await publish(event_name, payload)
