"""
Integration tests for the core participant journey:
register → create participant → apply → enrol.

These require a live PostgreSQL and Redis — skipped in unit CI
unless INTEGRATION_TESTS=1 is set.
"""

import os
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("INTEGRATION_TESTS") != "1",
    reason="Set INTEGRATION_TESTS=1 to run integration tests",
)
