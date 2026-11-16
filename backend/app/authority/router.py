"""
Authority module router (CW-302).

This router holds all authority-related API endpoints.
"""
from fastapi import APIRouter

# Create a router with the /authority prefix for all authority endpoints
router = APIRouter(prefix="/authority", tags=["authority"])


@router.get("/ping")
def ping():
    """Return a simple JSON so teammates can confirm the authority module is wired up."""
    # Role check (officer or admin only) is added in Sprint 2 by the platform RBAC (CW-208)
    return {"module": "authority", "status": "ok"}
