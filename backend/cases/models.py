"""
SQLAlchemy models for modular cases (Eurorack primary; multi-format via capacity_unit).
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from core.database import Base


class Case(Base):
    """Case / cabinet envelope for rack placement and power budgets."""

    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    brand = Column(String(100), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)

    # Layout (total_hp is primary capacity number; unit named by capacity_unit)
    total_hp = Column(Integer, nullable=False)  # Capacity total (HP for Eurorack)
    rows = Column(Integer, nullable=False, default=1)
    hp_per_row = Column(JSON, nullable=False, default=list)

    # Format honesty (C1) — first-class filters; meta retains raw research fields
    format_family = Column(String(64), nullable=True, index=True)  # Eurorack, Buchla, …
    capacity_unit = Column(String(64), nullable=True, index=True)  # hp, buchla_panels, …
    powered = Column(Boolean, nullable=True, index=True)  # None = unknown product flag

    # Power specifications (null = unspecified — fail-closed, never invent)
    power_12v_ma = Column(Integer, nullable=True)
    power_neg12v_ma = Column(Integer, nullable=True)
    power_5v_ma = Column(Integer, nullable=True)

    # Metadata
    description = Column(Text, nullable=True)
    manufacturer_url = Column(String(500), nullable=True)
    meta = Column(JSON, nullable=True)

    # Data provenance
    source = Column(String(50), nullable=False)
    source_reference = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    racks = relationship("Rack", back_populates="case", cascade="all, delete-orphan")
