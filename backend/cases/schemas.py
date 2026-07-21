"""
Pydantic schemas for Case API.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CaseBase(BaseModel):
    """Base schema for case data."""

    brand: str = Field(..., max_length=100)
    name: str = Field(..., max_length=200)
    total_hp: int = Field(..., gt=0, description="Capacity total (HP when capacity_unit=hp)")
    rows: int = Field(..., gt=0, description="Number of rows")
    hp_per_row: list[int] = Field(..., description="Capacity per row")
    format_family: Optional[str] = Field(
        None, max_length=64, description="Eurorack | Buchla | 5U MU | Serge 4U | Frac"
    )
    capacity_unit: Optional[str] = Field(
        None, max_length=64, description="hp | buchla_panels | mu_spaces | …"
    )
    powered: Optional[bool] = Field(
        None, description="False = unpowered; True = powered product; null = unknown flag"
    )
    power_12v_ma: Optional[int] = Field(None, ge=0)
    power_neg12v_ma: Optional[int] = Field(None, ge=0)
    power_5v_ma: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    manufacturer_url: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class CaseCreate(CaseBase):
    """Schema for creating a new case."""

    source: str = Field(..., max_length=50, description="Manual, CSV, ResearchCSV, etc.")
    source_reference: Optional[str] = Field(None, max_length=500)


class CaseUpdate(BaseModel):
    """Schema for updating a case."""

    brand: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=200)
    total_hp: Optional[int] = Field(None, gt=0)
    rows: Optional[int] = Field(None, gt=0)
    hp_per_row: Optional[list[int]] = None
    format_family: Optional[str] = Field(None, max_length=64)
    capacity_unit: Optional[str] = Field(None, max_length=64)
    powered: Optional[bool] = None
    power_12v_ma: Optional[int] = Field(None, ge=0)
    power_neg12v_ma: Optional[int] = Field(None, ge=0)
    power_5v_ma: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    manufacturer_url: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class CaseResponse(CaseBase):
    """Schema for case response."""

    id: int
    source: str
    source_reference: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    """Schema for paginated case list."""

    total: int
    cases: list[CaseResponse]
