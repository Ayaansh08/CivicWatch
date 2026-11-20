"""
Simple in-memory rate limiter for failed login attempts.

Uses a plain dictionary — no new library needed.
Key = client IP + lower-cased email.
5 failed logins within 60 seconds block that key for the remainder of the window.
"""
import time

# Dictionary storing failed login attempts: key -> list of timestamps
_failed_attempts: dict = {}

# How many failures within the time window trigger a block
MAX_FAILURES = 5

# How many seconds the window lasts
WINDOW_SECONDS = 60


def record_failed_login(key: str) -> None:
    """
    Record one failed login attempt for the given key.
    Old attempts outside the window are pruned first to keep memory small.
    """
    now = time.time()
    # Initialize the list for this key if it does not exist yet
    if key not in _failed_attempts:
        _failed_attempts[key] = []
    # Remove timestamps that are older than the window
    _failed_attempts[key] = [
        ts for ts in _failed_attempts[key] if now - ts < WINDOW_SECONDS
    ]
    # Add the current timestamp
    _failed_attempts[key].append(now)


def is_blocked(key: str) -> bool:
    """
    Return True if the key has 5 or more failed attempts within the last 60 seconds.
    """
    now = time.time()
    if key not in _failed_attempts:
        return False
    # Count only recent failures within the window
    recent = [ts for ts in _failed_attempts[key] if now - ts < WINDOW_SECONDS]
    return len(recent) >= MAX_FAILURES


def reset(key: str) -> None:
    """Remove all recorded failures for the given key (call after a successful login)."""
    _failed_attempts.pop(key, None)


def clear_all() -> None:
    """Remove all stored attempt data. Used in tests to prevent interference between tests."""
    _failed_attempts.clear()
