"""
Authentication routes: register, login, and get current user.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app.platform.config import get_user_by_email
from backend.app.platform.database import get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User
from backend.app.platform.rate_limit import is_blocked, record_failed_login, reset
from backend.app.platform.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from backend.app.platform.security import (
    create_access_token,
    hash_password,
    verify_password,
)

# Group all auth routes under the /auth prefix
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new account",
    description="Create a citizen account with name, email, and password. "
                "Returns the user object without the password.",
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Always assigns the role 'citizen'.
    Returns the user data (never the password).
    """
    # Normalise the email to lower-case before storing
    email_lower = request.email.lower()

    # Trim and validate the name (must be 2–60 non-whitespace characters)
    trimmed_name = request.name.strip()
    if len(trimmed_name) < 2 or len(trimmed_name) > 60:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Name must be between 2 and 60 characters",
        )

    # Reject passwords that exceed bcrypt's 72-byte limit
    if len(request.password) > 72:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at most 72 characters",
        )

    # Check if the email is already taken
    existing = get_user_by_email(db, email_lower)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    # Hash the password before storing it
    new_user = User(
        name=trimmed_name,
        email=email_lower,
        password_hash=hash_password(request.password),
        role="citizen",
    )
    # Save the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in",
    description="Authenticate with email and password. Returns a JWT access token. "
                "Returns 429 after 5 consecutive failed attempts within 60 seconds.",
)
def login(http_request: Request, request: LoginRequest, db: Session = Depends(get_db)):
    """
    Log in with email and password.
    Returns a JWT access token on success.
    """
    # Build the rate-limit key from client IP + lower-cased email
    client_ip = http_request.client.host if http_request.client else "unknown"
    email_lower = request.email.lower()
    rate_key = f"{client_ip}:{email_lower}"

    # Reject the request immediately if this IP+email is blocked
    if is_blocked(rate_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again in a minute.",
            headers={"Retry-After": "60"},
        )

    # Look up the user by lower-cased email (case-insensitive login)
    user = get_user_by_email(db, email_lower)

    # Return 401 for wrong email or wrong password (same message for security)
    if not user or not verify_password(request.password, user.password_hash):
        # Record the failure so the rate limiter can track it
        record_failed_login(rate_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Successful login — reset the failed-attempt counter for this key
    reset(rate_key)

    # Create a JWT containing the user's id and email
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Return the profile of the currently authenticated user.",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the currently logged-in user's profile.
    Requires a valid Bearer token in the Authorization header.
    """
    # Return the authenticated user loaded by get_current_user
    return current_user
