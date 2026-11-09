import time
from datetime import datetime, timezone


def current_utc_time() -> datetime:
    """Return the current datetime in UTC timezone."""
    return datetime.now(timezone.utc)


def current_time_ms() -> int:
    """Return current timestamp in milliseconds."""
    return int(time.time() * 1000)


def calculate_window_start_ms(now_ms: int, window_seconds: int) -> int:
    """Calculate the starting timestamp of a sliding window in milliseconds."""
    return now_ms - (window_seconds * 1000)

