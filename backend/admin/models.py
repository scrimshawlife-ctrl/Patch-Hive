"""
SQLAlchemy models for admin audit logging.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from core.database import Base


class AdminAuditLog(Base):
    """Append-only admin audit log."""

    __tablename__ = "admin_audit_log"

    id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_role = Column(String(20), nullable=False)
    action_type = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(50), nullable=True)
    delta_json = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    actor = relationship("User", backref="admin_audit_logs")


class PendingFunction(Base):
    """Pending function/jack review queue for proprietary names."""

    __tablename__ = "pending_functions"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    function_name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    canonical_function = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    module = relationship("Module", backref="pending_functions")
