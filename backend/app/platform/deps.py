"""
FastAPI dependency functions used by route handlers.

Role name constants are defined here so every module imports from one place
instead of using raw strings like "officer" that are easy to mistype.
"""
from typing import Any, Dict, Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.platform.config import ROLE_ADMIN, ROLE_CITIZEN, ROLE_OFFICER  # noqa: F401
from backend.app.platform.database import get_db
from backend.app.platform.models import User
from backend.app.platform.security import decode_access_token

# Use auto_error=False so missing Authorization headers return 401 instead of 403
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_stub() -> Dict[str, Any]:
    """
    STUB — returns a hard-coded user for teammates whose early tests
    do not need real JWT auth. Keep this until all teammates migrate.
    Temporary until real JWT auth in CW-205; teammates use this on Day 1.
    """
    # Return a fake user dict with id, email, and role
    return {"id": 1, "email": "stub@civicwatch.com", "role": "citizen"}


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Real JWT dependency: reads the Bearer token, verifies it,
    and returns the matching User from the database.
    Raises 401 if the token is missing, invalid, or expired.
    """
    # Reject requests that did not provide a Bearer token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    # Decode the token — raises PyJWTError if invalid or expired
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    # Look up the matching user in the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


# Usage example in a route:
# def officer_endpoint(user: User = Depends(require_role("officer", "admin"))):
def require_role(*allowed_roles: str):
    """
    Create a FastAPI dependency that allows only users with one of the given roles.
    Builds on get_current_user so existing get_current_user test overrides keep working.
    Example: Depends(require_role("officer", "admin"))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """Check whether the authenticated user's role is permitted."""
        # Support ORM User objects returned by get_current_user (and dicts in legacy stubs)
        user_role = (
            current_user.get("role")
            if isinstance(current_user, dict)
            else getattr(current_user, "role", None)
        )
        # Raise 403 Forbidden if the user's role is not in allowed_roles
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to do this",
            )
        return current_user

    return role_checker
