"""Datetime helpers used by the scheduler runtime."""

from datetime import datetime, timezone


def get_current_utc_time() -> datetime:
    """Return the current UTC-aware datetime."""
    return datetime.now(timezone.utc)
