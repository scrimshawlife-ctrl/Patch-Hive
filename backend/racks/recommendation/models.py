"""Pydantic models for rack recommendations."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ModuleSpec(BaseModel):
    module_id: int
    name: str
    hp: int
    role_tags: list[str] = Field(default_factory=list)


class ConnectionFrequency(BaseModel):
    from_module_id: int
    to_module_id: int
    weight: float = Field(..., ge=0)


class RackRecommendationRequest(BaseModel):
    rack_hp: int
    modules: list[ModuleSpec] = Field(default_factory=list)
    connection_frequencies: Optional[list[ConnectionFrequency]] = None


class RackRecommendationFromRackRequest(BaseModel):
    connection_frequencies: Optional[list[ConnectionFrequency]] = None


class LayoutScore(BaseModel):
    adjacency_score: float
    zoning_score: float
    access_score: float
    cable_score: float
    total_score: float


class LayoutRecommendation(BaseModel):
    layout: list[int]
    score: LayoutScore
    rationale: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class RackRecommendationResponse(BaseModel):
    decision: str
    layouts: list[LayoutRecommendation]
