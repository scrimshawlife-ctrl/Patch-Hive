"""
SQLAlchemy models for Eurorack modules.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base


class Module(Base):
    """Eurorack module model with full metadata."""

    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    brand = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    hp = Column(Integer, nullable=False)  # Width in HP units

    # Module type/category
    module_type = Column(
        String(50), nullable=False, index=True
    )  # VCO, VCF, VCA, ENV, LFO, SEQ, UTIL, MIX, FX, etc.

    # Power specifications
    power_12v_ma = Column(Integer, nullable=True)  # +12V power draw in mA
    power_neg12v_ma = Column(Integer, nullable=True)  # -12V power draw in mA
    power_5v_ma = Column(Integer, nullable=True)  # +5V power draw in mA

    # I/O ports (stored as JSON array)
    # Format: [{"name": "CV In 1", "type": "cv_in"}, {"name": "Audio Out", "type": "audio_out"}, ...]
    io_ports = Column(JSON, nullable=False, default=list)

    # Metadata
    tags = Column(JSON, nullable=False, default=list)  # ["analog", "digital", "west-coast", etc.]
    description = Column(Text, nullable=True)
    manufacturer_url = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    replacement_module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)
    deprecated_at = Column(DateTime, nullable=True)
    tombstoned_at = Column(DateTime, nullable=True)

    # Data provenance (SEED principle)
    source = Column(String(50), nullable=False)  # "Manual", "CSV", "ModularGrid", etc.
    source_reference = Column(String(500), nullable=True)  # URL, filename, etc.
    imported_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    rack_modules = relationship("RackModule", back_populates="module", cascade="all, delete-orphan")
