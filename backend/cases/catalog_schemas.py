"""Pydantic schemas for the normalized modular case catalog read API."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CaseRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    row_index: int
    format_family: str
    capacity_value: Optional[float] = None
    capacity_unit: Optional[str] = None
    usable_capacity_value: Optional[float] = None
    depth_min_mm: Optional[float] = None
    depth_max_mm: Optional[float] = None
    notes: Optional[str] = None


class CasePowerSystemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    supply_type: Optional[str] = None
    external_input: Optional[str] = None
    busboard_type: Optional[str] = None
    connector_count: Optional[int] = None
    current_pos12_ma: Optional[int] = None
    current_neg12_ma: Optional[int] = None
    current_pos5_ma: Optional[int] = None
    power_watts: Optional[float] = None
    zoned_distribution: Optional[bool] = None
    protections: Optional[str] = None
    notes: Optional[str] = None


class CaseFeatureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feature_key: str
    feature_value: Optional[str] = None
    verified: bool = False


class CasePriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_name: str
    source_url: Optional[str] = None
    amount: Decimal
    currency: str
    region: Optional[str] = None
    price_type: str
    in_stock: Optional[bool] = None
    captured_at: datetime


class CaseSourcePolicyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_basis: str
    license_status: str
    evidence_status: str
    review_state: str
    observed_at: Optional[datetime] = None
    retrieved_at: Optional[datetime] = None
    content_hash: Optional[str] = None
    normalizer_version: Optional[str] = None
    external_record_id: Optional[str] = None
    notes: Optional[str] = None


class CaseSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_type: str
    title: Optional[str] = None
    url: str
    field_path: Optional[str] = None
    published_value: Optional[str] = None
    normalized_value: Optional[str] = None
    discrepancy_note: Optional[str] = None
    confidence: str
    captured_at: datetime
    policy: Optional[CaseSourcePolicyOut] = None


class CaseRevisionSummaryOut(BaseModel):
    """Lightweight revision fields used on list cards and filter joins."""

    model_config = ConfigDict(from_attributes=True)

    revision_key: str
    revision_label: Optional[str] = None
    row_count: Optional[int] = None
    capacity_value: Optional[float] = None
    capacity_unit: Optional[str] = None
    depth_min_mm: Optional[float] = None
    depth_max_mm: Optional[float] = None
    portable: Optional[bool] = None
    removable_lid: Optional[bool] = None
    integrated_stand: Optional[bool] = None
    confidence: str


class CaseRevisionDetailOut(CaseRevisionSummaryOut):
    usable_capacity_value: Optional[float] = None
    depth_notes: Optional[str] = None
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None
    depth_mm: Optional[float] = None
    weight_kg: Optional[float] = None
    materials: Optional[str] = None
    mounting_type: Optional[str] = None
    close_patched_lid: Optional[bool] = None
    rack_mountable: Optional[bool] = None
    notes: Optional[str] = None
    rows: list[CaseRowOut] = Field(default_factory=list)
    power_systems: list[CasePowerSystemOut] = Field(default_factory=list)
    features: list[CaseFeatureOut] = Field(default_factory=list)


class CaseCatalogListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    manufacturer: str
    model: str
    format_family: str
    production_status: str
    powered: Optional[bool] = None
    official_url: Optional[str] = None
    image_url: Optional[str] = None
    primary_revision: Optional[CaseRevisionSummaryOut] = None


class CaseCatalogListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    cases: list[CaseCatalogListItem]


class CaseCatalogDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    manufacturer: str
    model: str
    format_family: str
    production_status: str
    powered: Optional[bool] = None
    official_url: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    revisions: list[CaseRevisionDetailOut] = Field(default_factory=list)
    prices: list[CasePriceOut] = Field(default_factory=list)
    sources: list[CaseSourceOut] = Field(default_factory=list)


class ManufacturerCount(BaseModel):
    name: str
    case_count: int


class ManufacturerListResponse(BaseModel):
    total: int
    manufacturers: list[ManufacturerCount]


class FormatCount(BaseModel):
    format_family: str
    case_count: int


class FormatListResponse(BaseModel):
    total: int
    formats: list[FormatCount]


class CaseCatalogStatsResponse(BaseModel):
    """Coverage-oriented snapshot for the normalized catalog tables."""

    case_count: int
    revision_count: int
    manufacturer_count: int
    format_family_counts: dict[str, int]
    production_status_counts: dict[str, int]
    powered_counts: dict[str, int]
    capacity_unit_counts: dict[str, int]
    with_power_rails: int
    with_depth: int
    with_prices: int
    with_sources: int
    source_packet_count: int
    publication_note: str = (
        "Stats reflect current database state. Research seed is not manufacturer-verified."
    )


class CaseRevisionListResponse(BaseModel):
    slug: str
    manufacturer: str
    model: str
    revisions: list[CaseRevisionDetailOut]
