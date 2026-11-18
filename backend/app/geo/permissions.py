"""
Geo feature permissions.
Restricts advanced geospatial endpoints (heatmap, hotspots, reports)
to authority officers and platform administrators.
"""
from fastapi import Depends, HTTPException, status

from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User


# Replace with platform require_role when teammate Gaurav's RBAC is merged.
def require_officer(current_user: User = Depends(get_current_user)):
    """
    Ensure the current user has officer or admin privileges.
    Raises 403 Forbidden if the user is a citizen or unprivileged.
    """
    # Extract role whether current_user is an ORM User model or a dictionary
    role = (
        current_user.get("role")
        if isinstance(current_user, dict)
        else getattr(current_user, "role", None)
    )

    # Allow officer and admin roles, reject others with 403
    if role not in ("officer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to do this",
        )
    return current_user
