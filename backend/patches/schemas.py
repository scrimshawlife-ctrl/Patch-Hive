"""
Pydantic schemas for Patch API.
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class ConnectionResponse(BaseModel):
    """Schema for a connection in a patch."""

    from_module_id: int
    from_port: str
    to_module_id: int
    to_port: str
    cable_type: str


class PatchBase(BaseModel):
    """Base schema for patch data."""

    name: str
    suggested_name: Optional[str] = None
    name_override: Optional[str] = None
    category: str  # "Voice", "Modulation", "Clock-Rhythm", "Generative", "Utility", "Performance Macro", "Texture-FX", "Study", "Experimental-Feedback"
    description: Optional[str] = None
    is_public: bool = False


class PatchCreate(PatchBase):
    """Schema for creating a new patch."""

    rack_id: int
    run_id: Optional[int] = None
    connections: list[dict[str, Any]]
    generation_seed: int
    generation_version: str
    engine_config: Optional[dict[str, Any]] = None
    waveform_params: Optional[dict[str, Any]] = None


class PatchUpdate(BaseModel):
    """Schema for updating a patch."""

    name: Optional[str] = None
    name_override: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class PatchResponse(PatchBase):
    """Schema for patch response."""

    id: int
    rack_id: int
    run_id: Optional[int] = None
    connections: list[dict[str, Any]]
    generation_seed: int
    generation_version: str
    engine_config: Optional[dict[str, Any]]
    waveform_svg_path: Optional[str]
    waveform_params: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    vote_count: int = 0

    class Config:
        from_attributes = True


class PatchListResponse(BaseModel):
    """Schema for paginated patch list."""

    total: int
    patches: list[PatchResponse]


class GeneratePatchesRequest(BaseModel):
    """Schema for patch generation request."""

    seed: Optional[int] = None
    max_patches: Optional[int] = Field(None, ge=1, le=50)
    allow_feedback: bool = False
    prefer_simple: bool = False


class GeneratePatchesResponse(BaseModel):
    """Schema for patch generation response."""

    generated_count: int
    patches: list[PatchResponse]
