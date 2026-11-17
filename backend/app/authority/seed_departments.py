"""
Seed script: inserts the four standard city departments if they are missing.

Run with: python -m backend.app.authority.seed_departments

Why this exists: the admin API (CW-209, Gaurav's work) may not be merged yet,
so we seed the departments manually so the assign endpoint has data to work with.
"""
from backend.app.platform.database import SessionLocal
from backend.app.platform.models import Department

# Standard departments that every CivicWatch deployment should have
DEFAULT_DEPARTMENTS = [
    "Water Department",
    "Roads Department",
    "Sanitation Department",
    "Electricity Department",
]


def seed():
    """Insert default departments into the database if they do not already exist."""
    db = SessionLocal()
    try:
        for name in DEFAULT_DEPARTMENTS:
            # Check whether this department already exists
            existing = db.query(Department).filter(Department.name == name).first()
            if not existing:
                # Create and persist the missing department
                db.add(Department(name=name))
                print(f"Added: {name}")
            else:
                print(f"Already exists: {name}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
