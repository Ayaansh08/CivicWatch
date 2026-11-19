"""
Shared pytest fixtures for platform tests.
This file is automatically loaded by pytest for all tests in this directory.
"""
import pytest
from backend.app.platform.rate_limit import clear_all


@pytest.fixture(autouse=True)
def clear_rate_limiter():
    """
    Clear the in-memory rate limiter before each test so failed-login counters
    from one test do not affect any other test.
    """
    # Reset before the test runs
    clear_all()
    yield
    # Also clear after the test in case it left state
    clear_all()
