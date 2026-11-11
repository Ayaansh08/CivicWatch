"""
Database connection setup using SQLAlchemy.
Provides the engine, session factory, Base class, and a FastAPI dependency.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.platform.config import get_database_url

# Create the SQLAlchemy engine using the URL from config
engine = create_engine(get_database_url())

# SessionLocal is a factory for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all SQLAlchemy model classes
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that opens a database session for one request,
    then closes it when the request is done.
    """
    # Open a new session
    db = SessionLocal()
    try:
        # Hand the session to the route handler
        yield db
    finally:
        # Always close the session, even if an error occurred
        db.close()
