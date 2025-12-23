"""
SQLAlchemy models for Eurorack cases.
"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from core.database import Base


class Case(Base):
    """Eurorack case model with power and layout specifications."""

    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    brand = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)

    # Layout
    total_hp = Column(Integer, nullable=False)  # Total width in HP
    rows = Column(Integer, nullable=False, default=1)  # Number of rows
    hp_per_row = Column(JSON, nullable=False, default=list)  # HP per row, e.g., [84, 84] for 2x84HP

    # Power specifications
    power_12v_ma = Column(Integer, nullable=True)  # +12V rail capacity in mA
    power_neg12v_ma = Column(Integer, nullable=True)  # -12V rail capacity in mA
    power_5v_ma = Column(Integer, nullable=True)  # +5V rail capacity in mA

    # Metadata
    description = Column(Text, nullable=True)
    manufacturer_url = Column(String(500), nullable=True)
    meta = Column(JSON, nullable=True)  # Additional metadata

    # Data provenance
    source = Column(String(50), nullable=False)  # "Manual", "CSV", etc.
    source_reference = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    racks = relationship("Rack", back_populates="case", cascade="all, delete-orphan")
