"""
Configuration: reads settings from environment variables.
If no env var is set, falls back to safe local defaults for development.
"""
import os
from dotenv import load_dotenv

# Load variables from a .env file if one exists
load_dotenv()

# Role name constants — use these instead of raw strings to avoid typos
ROLE_CITIZEN = "citizen"
ROLE_OFFICER = "officer"
ROLE_ADMIN = "admin"

# Default secret key placeholder — MUST be changed in production
_DEFAULT_SECRET_KEY = "change-me-in-production"

# How long a JWT token stays valid before the user must log in again (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def get_database_url() -> str:
    """Return the database connection string from the environment."""
    # Use a local PostgreSQL URL as the fallback for development
    return os.getenv(
        "DATABASE_URL",
        "postgresql://civic:civic@localhost:5432/civicwatch",
    )


def get_secret_key() -> str:
    """Return the secret key used to sign JWT tokens."""
    return os.getenv("SECRET_KEY", _DEFAULT_SECRET_KEY)


def get_environment() -> str:
    """Return the current deployment environment (development or production)."""
    return os.getenv("ENVIRONMENT", "development")


def get_cors_origins() -> list:
    """
    Return the list of allowed CORS origins.
    Read from the CORS_ORIGINS environment variable (comma-separated).
    Default to the local Vite dev server.
    """
    # Split the comma-separated list and strip whitespace from each origin
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in raw.split(",")]


def check_production_safety() -> None:
    """
    Raise RuntimeError if the application is running in production with the default
    secret key — this prevents accidentally deploying with an insecure key.
    """
    if get_environment() == "production" and get_secret_key() == _DEFAULT_SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY must be changed from the default value in production. "
            "Set the SECRET_KEY environment variable to a long random string."
        )


def get_user_by_email(db, email: str):
    """
    Look up a user by their lower-cased email address.
    Returns the User ORM object or None if not found.
    Helper used by auth_router and other modules to avoid duplicate query code.
    """
    from backend.app.platform.models import User
    # Always search with the lower-cased email so login is case-insensitive
    return db.query(User).filter(User.email == email.lower()).first()
