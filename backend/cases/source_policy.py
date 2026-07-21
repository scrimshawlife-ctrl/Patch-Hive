"""Source-policy records for modular case evidence.

These records extend ``CaseSource`` without changing its identity role. They
capture the access, licensing, evidence, review, and hashing fields required by
PatchHive's canonical External Source Policy.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CaseSourcePolicyPacket(Base):
    """Field-level provenance and review state for one case source record."""

    __tablename__ = "case_source_policy_packets"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("case_sources.id", ondelete="CASCADE"), nullable=False)
    external_record_id = Column(String(240), nullable=True)
    access_basis = Column(String(40), nullable=False, default="unknown")
    license_status = Column(String(40), nullable=False, default="unknown")
    evidence_status = Column(String(40), nullable=False, default="UNKNOWN")
    review_state = Column(String(32), nullable=False, default="unreviewed")
    observed_at = Column(DateTime(timezone=True), nullable=True)
    retrieved_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    content_hash = Column(String(64), nullable=True)
    normalizer_version = Column(String(64), nullable=True)
    reviewed_by = Column(String(160), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    source = relationship("CaseSource")

    __table_args__ = (
        UniqueConstraint("source_id", name="uq_case_source_policy_source"),
        CheckConstraint(
            "access_basis IN ('official_publication','authorized_feed','licensed_dataset','user_authorized_export','manual_research','user_upload','provider_inference','unknown')",
            name="ck_case_source_policy_access_basis",
        ),
        CheckConstraint(
            "evidence_status IN ('MANUFACTURER_CONFIRMED','MANUAL_CONFIRMED','REGISTRY_CONFIRMED','USER_CONFIRMED','RETAILER_OBSERVED','CATALOG_OBSERVED','INFERRED','CONFLICTED','REJECTED','UNKNOWN','NOT_COMPUTABLE')",
            name="ck_case_source_policy_evidence_status",
        ),
        CheckConstraint(
            "review_state IN ('unreviewed','accepted','rejected','conflicted','needs_review')",
            name="ck_case_source_policy_review_state",
        ),
        Index("ix_case_source_policy_evidence", "evidence_status", "review_state"),
        Index("ix_case_source_policy_access", "access_basis", "license_status"),
        Index("ix_case_source_policy_hash", "content_hash"),
    )
