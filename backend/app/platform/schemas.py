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
    def password_length(cls, value: str) -> str:
        """Reject passwords shorter than 6 or longer than 72 characters (bcrypt limit)."""
        # Raise a ValueError so Pydantic returns HTTP 422 automatically
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        # bcrypt silently truncates at 72 bytes — reject early to avoid confusion
        if len(value) > 72:
            raise ValueError("Password must be at most 72 characters long")
        return value

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        """Reject names that are only whitespace or shorter than 2 characters."""
        # Strip whitespace and check the minimum length
        stripped = value.strip()
        if len(stripped) < 2:
            raise ValueError("Name must be at least 2 characters and not only spaces")
        if len(stripped) > 60:
            raise ValueError("Name must be at most 60 characters")
        return stripped


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
