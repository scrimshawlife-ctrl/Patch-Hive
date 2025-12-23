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
    total_hp: int = Field(..., gt=0, description="Total width in HP")
    rows: int = Field(..., gt=0, description="Number of rows")
    hp_per_row: list[int] = Field(..., description="HP per row, e.g., [84, 84]")
    power_12v_ma: Optional[int] = Field(None, ge=0)
    power_neg12v_ma: Optional[int] = Field(None, ge=0)
    power_5v_ma: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    manufacturer_url: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class CaseCreate(CaseBase):
    """Schema for creating a new case."""

    source: str = Field(..., max_length=50, description="Manual, CSV, etc.")
    source_reference: Optional[str] = Field(None, max_length=500)


class CaseUpdate(BaseModel):
    """Schema for updating a case."""

    brand: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=200)
    total_hp: Optional[int] = Field(None, gt=0)
    rows: Optional[int] = Field(None, gt=0)
    hp_per_row: Optional[list[int]] = None
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
