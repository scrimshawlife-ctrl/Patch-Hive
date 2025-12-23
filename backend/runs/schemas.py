"""Pydantic schemas for run APIs."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from patches.schemas import PatchResponse


class RunResponse(BaseModel):
    id: int
    rack_id: int
    status: str

    class Config:
        from_attributes = True


class RunListResponse(BaseModel):
    total: int
    runs: list[RunResponse]


class RunPatchesResponse(BaseModel):
    total: int
    patches: list[PatchResponse]
