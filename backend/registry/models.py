"""
Device Registry models — canonical source for Product Database (PDB).

Full hierarchy per DEVICE_REGISTRY.md + PRODUCT_DATABASE_COMPLETENESS_ROADMAP + ADR-006:

Manufacturer -> DeviceFamily -> DeviceModel -> DeviceRevision -> [Ports, Controls, Capabilities]

Design goals:
- Stable IDs (prefer slugs + deterministic keys).
- Fail-closed: unknowns stay UNKNOWN / null. Never invent specs.
- Snapshot-friendly (to_dict + from_dict for JSON registry snapshots).
- Compatible transition from ModuleCatalog / GalleryRevision.

Status: Foundation complete for Phase 1. DB wiring + Alembic in next operator step.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from core.database import Base


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    aliases = Column(JSON, nullable=False, default=list)
    website = Column(String(500), nullable=True)
    status = Column(String(20), default="active", index=True)  # active, discontinued, acquired, unknown
    provenance = Column(JSON, nullable=True)  # list of sources
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    families = relationship("DeviceFamily", back_populates="manufacturer", cascade="all, delete-orphan")


class DeviceFamily(Base):
    __tablename__ = "device_families"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"), nullable=False, index=True)
    canonical_name = Column(String(100), nullable=False, index=True)
    slug = Column(String(120), nullable=False, index=True)
    description = Column(Text, nullable=True)
    provenance = Column(JSON, nullable=True)

    manufacturer = relationship("Manufacturer", back_populates="families")
    models = relationship("DeviceModel", back_populates="family", cascade="all, delete-orphan")


class DeviceModel(Base):
    __tablename__ = "device_models"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"), nullable=False, index=True)
    family_id = Column(Integer, ForeignKey("device_families.id"), nullable=True, index=True)
    canonical_name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    device_type = Column(String(50), nullable=True, index=True)  # VCO, VCF, UTIL, etc. or broader
    format = Column(String(30), nullable=True)  # eurorack, semi-modular, pedal...
    hp = Column(Integer, nullable=True)
    depth_mm = Column(Float, nullable=True)
    release_state = Column(String(20), default="available")
    official_sources = Column(JSON, nullable=True)
    provenance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    manufacturer = relationship("Manufacturer")
    family = relationship("DeviceFamily", back_populates="models")
    revisions = relationship("DeviceRevision", back_populates="model", cascade="all, delete-orphan")


class DeviceRevision(Base):
    __tablename__ = "device_revisions"

    id = Column(Integer, primary_key=True, index=True)
    device_model_id = Column(Integer, ForeignKey("device_models.id"), nullable=False, index=True)
    revision_label = Column(String(50), nullable=False)
    panel_variant = Column(String(50), nullable=True)
    firmware_constraints = Column(JSON, nullable=True)
    physical_changes = Column(JSON, nullable=True)
    functional_changes = Column(JSON, nullable=True)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    provenance = Column(JSON, nullable=True)

    model = relationship("DeviceModel", back_populates="revisions")
    ports = relationship("Port", back_populates="revision", cascade="all, delete-orphan")
    controls = relationship("Control", back_populates="revision", cascade="all, delete-orphan")


class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    revision_id = Column(Integer, ForeignKey("device_revisions.id"), nullable=False, index=True)
    canonical_label = Column(String(100), nullable=False)
    aliases = Column(JSON, nullable=False, default=list)
    direction = Column(String(20), nullable=True)  # in, out, bidirectional
    signal_class = Column(String(30), nullable=True)
    connector_type = Column(String(30), nullable=True)
    channel_count = Column(Integer, nullable=True)
    voltage_or_level_domain = Column(String(50), nullable=True)
    evidence_status = Column(String(30), default="UNKNOWN")

    revision = relationship("DeviceRevision", back_populates="ports")


class Control(Base):
    __tablename__ = "controls"

    id = Column(Integer, primary_key=True, index=True)
    revision_id = Column(Integer, ForeignKey("device_revisions.id"), nullable=False, index=True)
    canonical_label = Column(String(100), nullable=False)
    control_type = Column(String(30), nullable=True)
    range = Column(JSON, nullable=True)  # [min, max] or dict
    units = Column(String(20), nullable=True)
    discrete_values = Column(JSON, nullable=True)
    default_or_neutral_position = Column(String(50), nullable=True)
    evidence_status = Column(String(30), default="UNKNOWN")

    revision = relationship("DeviceRevision", back_populates="controls")


class Capability(Base):
    __tablename__ = "capabilities"

    id = Column(Integer, primary_key=True, index=True)
    canonical_type = Column(String(50), nullable=False, index=True)
    parameters = Column(JSON, nullable=True)
    constraints = Column(JSON, nullable=True)
    required_ports = Column(JSON, nullable=True)
    required_controls = Column(JSON, nullable=True)
    provenance = Column(JSON, nullable=True)


# ---------- Snapshot helpers (pure structure, DB optional) ----------

def model_to_dict(obj: Any) -> dict:
    """Minimal to_dict for snapshot generation."""
    if obj is None:
        return None
    if hasattr(obj, "__table__"):
        d = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            if isinstance(val, datetime):
                val = val.isoformat()
            d[col.name] = val
        return d
    return obj  # already dict-like


def build_snapshot(manufacturers: list) -> dict:
    """Produce a portable registry snapshot from model instances or dicts."""
    return {
        "schema_version": "1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "manufacturers": [model_to_dict(m) for m in manufacturers],
    }
