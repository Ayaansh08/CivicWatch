"""
Bootstrap script to create the first admin account in CivicWatch.

Why this exists:
  Public /auth/register always assigns the 'citizen' role, and /admin/officers
  requires an existing admin. Therefore, there must be at least one admin in the
  database before anyone can create officers or manage departments.

How to run:
  python -m backend.app.platform.create_admin "Admin" admin@civicwatch.com secret123
"""
import argparse
from sqlalchemy.orm import Session

from backend.app.platform.database import SessionLocal
from backend.app.platform.models import User
from backend.app.platform.security import hash_password


def create_admin_user(
    db: Session, name: str, email: str, password: str
) -> User:
    """
    Create an admin user with a bcrypt-hashed password.
    If a user with the given email already exists, return them without duplicating.
    """
    # Return the existing user if this email is already registered
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    # Create a new User row with role='admin' and a hashed password
    admin = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


if __name__ == "__main__":
    # Parse name, email, and password from command-line arguments
    parser = argparse.ArgumentParser(
        description="Create the initial CivicWatch admin user."
    )
    parser.add_argument("name", help="Full name of the admin user")
    parser.add_argument("email", help="Email address of the admin user")
    parser.add_argument("password", help="Plain-text password (will be hashed)")
    args = parser.parse_args()

    # Open a session to the real database and create the admin account
    db_session = SessionLocal()
    try:
        user = create_admin_user(
            db_session, args.name, args.email, args.password
        )
        print(f"Admin ready: {user.email} (id={user.id}, role={user.role})")
    finally:
        db_session.close()
