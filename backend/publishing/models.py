"""
SQLAlchemy models for publishing layer (exports, publications, reports).
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from core.database import Base


class Export(Base):
    """Export artifacts generated from patches or racks."""

    __tablename__ = "exports"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    patch_id = Column(
        Integer, ForeignKey("patches.id", ondelete="SET NULL"), nullable=True, index=True
    )
    rack_id = Column(
        Integer, ForeignKey("racks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    export_type = Column(String(20), nullable=False, index=True)  # "patch" or "rack"

    license = Column(String(100), nullable=False, default="CC BY-NC 4.0")
    run_id = Column(String(64), nullable=False, index=True)
    generated_at = Column(DateTime, nullable=False)
    patch_count = Column(Integer, nullable=True)
    manifest_hash = Column(String(64), nullable=False, index=True)

    artifact_urls = Column(JSON, nullable=False, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User")
    patch = relationship("Patch")
    rack = relationship("Rack")


class Publication(Base):
    """Publication of an export artifact."""

    __tablename__ = "publications"
    __table_args__ = (UniqueConstraint("export_id", name="unique_publication_export"),)

    id = Column(Integer, primary_key=True, index=True)
    export_id = Column(Integer, ForeignKey("exports.id", ondelete="RESTRICT"), nullable=False)
    publisher_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    slug = Column(String(160), unique=True, nullable=False, index=True)
    visibility = Column(String(20), nullable=False, default="unlisted")  # unlisted/public
    status = Column(String(20), nullable=False, default="draft")  # draft/published/hidden/removed

    allow_download = Column(Boolean, default=True, nullable=False)
    allow_remix = Column(Boolean, default=False, nullable=False)

    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    cover_image_url = Column(String(500), nullable=True)

    published_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    removed_reason = Column(String(500), nullable=True)
    moderation_audit_id = Column(
        Integer, ForeignKey("admin_audit_log.id", ondelete="SET NULL"), nullable=True
    )

    export = relationship("Export")
    publisher = relationship("User")
    moderation_audit = relationship("AdminAuditLog")


class PublicationReport(Base):
    """User report for a publication."""

    __tablename__ = "publication_reports"

    id = Column(Integer, primary_key=True, index=True)
    publication_id = Column(
        Integer, ForeignKey("publications.id", ondelete="CASCADE"), nullable=False
    )
    reporter_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reason = Column(String(200), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    publication = relationship("Publication")
    reporter = relationship("User")
