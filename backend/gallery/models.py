"""
SQLAlchemy models for gallery revisions (append-only).
"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String

from core.database import Base


class GalleryRevision(Base):
    """Append-only gallery revision record."""

    __tablename__ = "gallery_revisions"

    id = Column(Integer, primary_key=True, index=True)
    module_key = Column(String(200), nullable=False, index=True)
    revision_id = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="Pending")
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
