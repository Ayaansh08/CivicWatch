"""
Permissions helper for the authority module (CW-303).

Creates the require_officer dependency that gates all authority endpoints.
Replace with platform require_role when teammate Gaurav's RBAC is merged.
"""
from fastapi import Depends, HTTPException, status
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User


def require_officer(current_user: User = Depends(get_current_user)) -> User:
    """Allow only users with role 'officer' or 'admin'; raise 403 otherwise."""
    # Check the user's role and reject anyone who is not an officer or admin
    if current_user.role not in ("officer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to do this",
        )
    return current_user
