"""
SQLAlchemy ORM models (database table definitions) for the platform.

NOTE for teammates: Ayaansh will add the PostGIS geometry column in his own
migration. Use plain Float for latitude and longitude for now.
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text,
    DateTime, ForeignKey,
)
from backend.app.platform.database import Base


class User(Base):
    """Represents a registered user of CivicWatch."""

    __tablename__ = "users"

    # Primary key — auto-incremented integer
    id = Column(Integer, primary_key=True, index=True)
    # Full name of the user
    name = Column(String(255), nullable=False)
    # Email must be unique across all users
    email = Column(String(255), unique=True, nullable=False, index=True)
    # Hashed password — never store plain text
    password_hash = Column(String(255), nullable=False)
    # Role defaults to citizen; can be changed to authority or admin later
    role = Column(String(50), nullable=False, default="citizen")
    # Automatically set when the row is created
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Category(Base):
    """Lookup table of complaint categories (e.g. Pothole, Garbage)."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    # Category name must be unique
    name = Column(String(100), unique=True, nullable=False)


class Department(Base):
    """Lookup table of city departments that handle complaints."""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    # Department name must be unique
    name = Column(String(100), unique=True, nullable=False)


class Complaint(Base):
    """
    A complaint filed by a citizen about an issue in their area.

    NOTE: Ayaansh adds the PostGIS geometry column in a later migration.
    Plain Float columns (latitude, longitude) are used here.
    """

    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    # Short title describing the complaint
    title = Column(String(255), nullable=False)
    # Detailed description of the problem
    description = Column(Text, nullable=True)
    # Which category of problem this is
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    # Workflow status — starts as Submitted
    status = Column(String(50), nullable=False, default="Submitted")
    # Priority level — defaults to Medium
    priority = Column(String(50), nullable=False, default="Medium")
    # Location of the complaint (plain floats; PostGIS geometry added later)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    # Optional photo attached to the complaint
    photo_path = Column(String(500), nullable=True)
    # Which user filed the complaint
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Which department is handling it (assigned later)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
