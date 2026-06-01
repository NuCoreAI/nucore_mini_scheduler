from datetime import datetime, timezone


def get_current_utc_time() -> datetime:
    return datetime.now(timezone.utc)
