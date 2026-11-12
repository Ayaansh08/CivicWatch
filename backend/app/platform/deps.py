"""
FastAPI dependency functions used by route handlers.
"""
from typing import Dict, Any


def get_current_user() -> Dict[str, Any]:
    """
    STUB — returns a hard-coded user so teammates can build their routes
    before real JWT auth is wired up in CW-205.
    Temporary until real JWT auth in CW-205; teammates use this on Day 1.
    """
    # Return a fake user dict with id, email, and role
    return {"id": 1, "email": "stub@civicwatch.com", "role": "citizen"}
