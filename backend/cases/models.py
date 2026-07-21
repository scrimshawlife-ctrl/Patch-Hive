"""SQLAlchemy models for legacy racks and the normalized hardware case catalog."""

from __future__ import annotations

from datetime import datetime, timezone
import re

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Case(Base):
    """Legacy Eurorack case record retained for rack compatibility."""

    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    total_hp = Column(Integer, nullable=False)
    rows = Column(Integer, nullable=False, default=1)
    hp_per_row = Column(JSON, nullable=False, default=list)
    power_12v_ma = Column(Integer, nullable=True)
    power_neg12v_ma = Column(Integer, nullable=True)
    power_5v_ma = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    manufacturer_url = Column(String(500), nullable=True)
    meta = Column(JSON, nullable=True)
    source = Column(String(50), nullable=False)
    source_reference = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    racks = relationship("Rack", back_populates="case", cascade="all, delete-orphan")


class CaseCatalog(Base):
    """Lightweight searchable identity for all modular case formats."""

    __tablename__ = "case_catalog"

    id = Column(Integer, primary_key=True)
    slug = Column(String(220), nullable=False, unique=True, index=True)
    manufacturer = Column(String(120), nullable=False, index=True)
    model = Column(String(180), nullable=False, index=True)
    format_family = Column(String(40), nullable=False, index=True)
    production_status = Column(String(24), nullable=False, default="unknown", index=True)
    powered = Column(Boolean, nullable=True, index=True)
    image_url = Column(String(1000), nullable=True)
    official_url = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    revisions = relationship("CaseRevision", back_populates="case", cascade="all, delete-orphan")
    prices = relationship("CasePrice", back_populates="case", cascade="all, delete-orphan")
    sources = relationship("CaseSource", back_populates="case", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("manufacturer", "model", name="uq_case_catalog_manufacturer_model"),
        CheckConstraint(
            "format_family IN ('eurorack','intellijel_1u','pulplogic_1u','buchla_200','serge_4u','mu_5u','frac','other')",
            name="ck_case_catalog_format_family",
        ),
        Index("ix_case_catalog_manufacturer_model", "manufacturer", "model"),
        Index("ix_case_catalog_format_status", "format_family", "production_status"),
    )

    @staticmethod
    def create_slug(manufacturer: str, model: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", f"{manufacturer}-{model}".lower()).strip("-")


class CaseRevision(Base):
    """Revision-specific physical and usability specifications."""

    __tablename__ = "case_revisions"

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("case_catalog.id", ondelete="CASCADE"), nullable=False)
    revision_key = Column(String(80), nullable=False, default="default")
    revision_label = Column(String(160), nullable=True)
    row_count = Column(Integer, nullable=True)
    capacity_value = Column(Float, nullable=True)
    capacity_unit = Column(String(32), nullable=True)
    usable_capacity_value = Column(Float, nullable=True)
    depth_min_mm = Column(Float, nullable=True)
    depth_max_mm = Column(Float, nullable=True)
    depth_notes = Column(Text, nullable=True)
    width_mm = Column(Float, nullable=True)
    height_mm = Column(Float, nullable=True)
    depth_mm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    materials = Column(Text, nullable=True)
    mounting_type = Column(String(80), nullable=True)
    portable = Column(Boolean, nullable=True)
    removable_lid = Column(Boolean, nullable=True)
    close_patched_lid = Column(Boolean, nullable=True)
    integrated_stand = Column(Boolean, nullable=True)
    rack_mountable = Column(Boolean, nullable=True)
    notes = Column(Text, nullable=True)
    confidence = Column(String(16), nullable=False, default="medium")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    case = relationship("CaseCatalog", back_populates="revisions")
    rows = relationship("CaseRow", back_populates="revision", cascade="all, delete-orphan")
    power_systems = relationship("CasePowerSystem", back_populates="revision", cascade="all, delete-orphan")
    features = relationship("CaseFeature", back_populates="revision", cascade="all, delete-orphan")
    sources = relationship("CaseSource", back_populates="revision")

    __table_args__ = (
        UniqueConstraint("case_id", "revision_key", name="uq_case_revision_key"),
        CheckConstraint(
            "capacity_unit IS NULL OR capacity_unit IN ('hp','mu_space','buchla_panel','serge_panel','frac_width','custom')",
            name="ck_case_revision_capacity_unit",
        ),
        CheckConstraint(
            "confidence IN ('verified','high','medium','low','conflict')",
            name="ck_case_revision_confidence",
        ),
        Index("ix_case_revision_capacity", "capacity_unit", "capacity_value"),
        Index("ix_case_revision_depth", "depth_max_mm"),
    )


class CaseRow(Base):
    __tablename__ = "case_rows"

    id = Column(Integer, primary_key=True)
    revision_id = Column(Integer, ForeignKey("case_revisions.id", ondelete="CASCADE"), nullable=False)
    row_index = Column(Integer, nullable=False)
    format_family = Column(String(40), nullable=False)
    capacity_value = Column(Float, nullable=True)
    capacity_unit = Column(String(32), nullable=True)
    usable_capacity_value = Column(Float, nullable=True)
    depth_min_mm = Column(Float, nullable=True)
    depth_max_mm = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    revision = relationship("CaseRevision", back_populates="rows")

    __table_args__ = (
        UniqueConstraint("revision_id", "row_index", name="uq_case_row_index"),
        CheckConstraint("row_index >= 0", name="ck_case_row_nonnegative"),
    )


class CasePowerSystem(Base):
    __tablename__ = "case_power_systems"

    id = Column(Integer, primary_key=True)
    revision_id = Column(Integer, ForeignKey("case_revisions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(140), nullable=False, default="primary")
    supply_type = Column(String(80), nullable=True)
    external_input = Column(String(180), nullable=True)
    busboard_type = Column(String(120), nullable=True)
    connector_count = Column(Integer, nullable=True)
    current_pos12_ma = Column(Integer, nullable=True)
    current_neg12_ma = Column(Integer, nullable=True)
    current_pos5_ma = Column(Integer, nullable=True)
    power_watts = Column(Float, nullable=True)
    zoned_distribution = Column(Boolean, nullable=True)
    protections = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    revision = relationship("CaseRevision", back_populates="power_systems")

    __table_args__ = (
        UniqueConstraint("revision_id", "name", name="uq_case_power_system_name"),
        CheckConstraint("connector_count IS NULL OR connector_count >= 0", name="ck_case_power_connectors"),
        CheckConstraint("current_pos12_ma IS NULL OR current_pos12_ma >= 0", name="ck_case_power_pos12"),
        CheckConstraint("current_neg12_ma IS NULL OR current_neg12_ma >= 0", name="ck_case_power_neg12"),
        CheckConstraint("current_pos5_ma IS NULL OR current_pos5_ma >= 0", name="ck_case_power_pos5"),
        Index("ix_case_power_rails", "current_pos12_ma", "current_neg12_ma", "current_pos5_ma"),
    )


class CaseFeature(Base):
    __tablename__ = "case_features"

    id = Column(Integer, primary_key=True)
    revision_id = Column(Integer, ForeignKey("case_revisions.id", ondelete="CASCADE"), nullable=False)
    feature_key = Column(String(80), nullable=False)
    feature_value = Column(String(500), nullable=True)
    verified = Column(Boolean, nullable=False, default=False)
    revision = relationship("CaseRevision", back_populates="features")

    __table_args__ = (
        UniqueConstraint("revision_id", "feature_key", name="uq_case_feature_key"),
        Index("ix_case_feature_key", "feature_key"),
    )


class CasePrice(Base):
    __tablename__ = "case_prices"

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("case_catalog.id", ondelete="CASCADE"), nullable=False)
    source_name = Column(String(160), nullable=False)
    source_url = Column(String(1000), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    region = Column(String(40), nullable=True)
    price_type = Column(String(24), nullable=False, default="street")
    in_stock = Column(Boolean, nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    case = relationship("CaseCatalog", back_populates="prices")
    __table_args__ = (Index("ix_case_price_lookup", "case_id", "currency", "captured_at"),)


class CaseSource(Base):
    __tablename__ = "case_sources"

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("case_catalog.id", ondelete="CASCADE"), nullable=False)
    revision_id = Column(Integer, ForeignKey("case_revisions.id", ondelete="SET NULL"), nullable=True)
    source_type = Column(String(32), nullable=False)
    title = Column(String(300), nullable=True)
    url = Column(String(1000), nullable=False)
    field_path = Column(String(180), nullable=True)
    published_value = Column(Text, nullable=True)
    normalized_value = Column(Text, nullable=True)
    discrepancy_note = Column(Text, nullable=True)
    confidence = Column(String(16), nullable=False, default="medium")
    captured_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    case = relationship("CaseCatalog", back_populates="sources")
    revision = relationship("CaseRevision", back_populates="sources")

    __table_args__ = (
        UniqueConstraint("case_id", "url", "field_path", name="uq_case_source_field"),
        CheckConstraint(
            "confidence IN ('verified','high','medium','low','conflict')",
            name="ck_case_source_confidence",
        ),
        Index("ix_case_source_case_revision", "case_id", "revision_id"),
        Index("ix_case_source_field", "field_path"),
    )
