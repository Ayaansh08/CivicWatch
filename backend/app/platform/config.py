"""
Configuration: reads settings from environment variables.
If no env var is set, falls back to safe local defaults for development.
"""
import os
from dotenv import load_dotenv

# Load variables from a .env file if one exists
load_dotenv()


def get_database_url() -> str:
    """Return the database connection string from the environment."""
    # Use a local PostgreSQL URL as the fallback for development
    return os.getenv(
        "DATABASE_URL",
        "postgresql://civic:civic@localhost:5432/civicwatch",
    )


def get_secret_key() -> str:
    """Return the secret key used to sign JWT tokens."""
    # Use a placeholder default — MUST be changed in production
    return os.getenv("SECRET_KEY", "change-me-in-production")
