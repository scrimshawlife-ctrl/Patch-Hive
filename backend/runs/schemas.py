"""
Pydantic schemas for Run API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RunBase(BaseModel):
    """Base schema for a generation run."""

    rack_id: int
    status: str


class RunResponse(RunBase):
    """Schema for run response."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RunListResponse(BaseModel):
    """Schema for paginated run list."""

    total: int
    runs: list[RunResponse]


class RunCreate(BaseModel):
    """Schema for creating a run."""

    rack_id: int
    status: Optional[str] = None
