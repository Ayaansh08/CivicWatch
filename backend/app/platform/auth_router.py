"""
Authentication routes: register, login, and get current user.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.platform.database import get_db
from backend.app.platform.deps import get_current_user
from backend.app.platform.models import User
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


@router.post("/register", response_model=UserResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Always assigns the role 'citizen'.
    Returns the user data (never the password).
    """
    # Check if the email is already taken
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    # Hash the password before storing it
    new_user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role="citizen",
    )
    # Save the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Log in with email and password.
    Returns a JWT access token on success.
    """
    # Look up the user by email
    user = db.query(User).filter(User.email == request.email).first()
    # Return 401 for wrong email or wrong password (same message for security)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    # Create a JWT containing the user's id and email
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the currently logged-in user's profile.
    Requires a valid Bearer token in the Authorization header.
    """
    # Return the authenticated user loaded by get_current_user
    return current_user
