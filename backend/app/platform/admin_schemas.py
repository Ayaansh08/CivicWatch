"""
Pydantic request and response schemas for the /admin management endpoints.
"""
from typing import Literal
from pydantic import BaseModel, EmailStr, Field


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

    name: str
    email: EmailStr
    # Officer passwords must be at least 6 characters long
    password: str = Field(..., min_length=6)


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
