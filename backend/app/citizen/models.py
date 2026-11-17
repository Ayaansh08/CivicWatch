"""ORM models for citizen tracking, history and feedback."""
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from backend.app.platform.database import Base


class StatusHistory(Base):
    """Logs every status change of a complaint."""

    __tablename__ = "complaint_status_history"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Feedback(Base):
    """Stores citizen rating and comment for resolved complaints."""

    __tablename__ = "complaint_feedback"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(
        Integer, ForeignKey("complaints.id"), unique=True, nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
