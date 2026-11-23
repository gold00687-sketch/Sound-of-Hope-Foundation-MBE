"""Shared async HTTP client for external service calls.

All outbound HTTP calls to third-party services should go through this module
so we have a single place to configure timeouts, retries, and observability.
"""

from contextlib import asynccontextmanager
from typing import Any

import httpx
import structlog

from app.core.exceptions import ExternalServiceError

logger = structlog.get_logger(__name__)

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


@asynccontextmanager
async def get_client(**kwargs: Any):
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, **kwargs) as client:
        yield client


async def post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    async with get_client() as client:
        try:
            response = await client.post(url, json=payload, headers=headers or {})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("external_http_error", url=url, status=exc.response.status_code)
            raise ExternalServiceError(f"External service returned {exc.response.status_code}.") from exc
        except httpx.RequestError as exc:
            logger.error("external_request_error", url=url, error=str(exc))
            raise ExternalServiceError("Could not reach external service.") from exc
