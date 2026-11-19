"""
Pydantic request and response schemas for the /admin management endpoints.
"""
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


class DepartmentCreate(BaseModel):
    """Data required to create or rename a city department."""

    # Department names must be at least 3 characters long
    name: str = Field(..., min_length=3)


class DepartmentOut(BaseModel):
    """Department data returned by the API."""

    id: int
    name: str

    model_config = {"from_attributes": True}


class OfficerCreate(BaseModel):
    """Data required for an admin to create a new officer account."""

    # Name must be 2–60 non-whitespace characters
    name: str = Field(..., min_length=2, max_length=60)
    email: EmailStr
    # Officer passwords must be 6–72 characters (bcrypt limit)
    password: str = Field(..., min_length=6, max_length=72)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        """Reject names that are only whitespace."""
        stripped = value.strip()
        # Ensure the trimmed name still meets the minimum length
        if len(stripped) < 2:
            raise ValueError("Name must be at least 2 non-whitespace characters")
        return stripped


class UserOut(BaseModel):
    """Safe user representation returned by admin endpoints (never includes password_hash)."""

    id: int
    name: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class RoleUpdate(BaseModel):
    """Data required to change a user's role."""

    # Limit roles to the three supported CivicWatch roles
    role: Literal["citizen", "officer", "admin"]
