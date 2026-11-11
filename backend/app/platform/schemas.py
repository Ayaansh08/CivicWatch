"""
Pydantic schemas: define the shape of request bodies and response bodies.
Pydantic validates the data automatically before it reaches our route handlers.
"""
from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    """Data the client sends when registering a new account."""

    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_must_be_at_least_6_chars(cls, value: str) -> str:
        """Reject passwords shorter than 6 characters."""
        # Raise a ValueError so Pydantic returns HTTP 422 automatically
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value


class LoginRequest(BaseModel):
    """Data the client sends when logging in."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """The user data we send back — never includes the password."""

    id: int
    name: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """The token we send back after a successful login."""

    access_token: str
    token_type: str = "bearer"
