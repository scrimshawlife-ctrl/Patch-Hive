"""
SQLAlchemy models for admin audit logging.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from core.database import Base


class AdminAuditLog(Base):
    """Admin audit log for moderation actions."""

    __tablename__ = "admin_audit_log"

    id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(String(50), nullable=False, index=True)
    target_type = Column(String(50), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)
    delta_json = Column(JSON, nullable=False)
    reason = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    actor = relationship("User", lazy="joined")
