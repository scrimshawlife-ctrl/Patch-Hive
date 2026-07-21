"""PatchPageLayoutIR — authoritative composition IR before PDF/SVG adapters."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from canon.contracts import canonical_sha256

LAYOUT_IR_SCHEMA_VERSION = "patchhive.layout_ir.v1"


class PageKind(str, Enum):
    EXECUTION = "execution"
    PLATE = "plate"
    FRONT_MATTER = "front_matter"
    BACK_MATTER = "back_matter"
    APPENDIX_EXECUTION = "appendix_execution"


RegionRole = Literal[
    "identity",
    "diagram",
    "intent",
    "construction",
    "operation",
    "warnings",
    "footer",
    "decoration",
    "caption",
]

StyleRole = Literal["display", "body", "mono", "caption", "footer", "warning"]


class LayoutRegion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    region_id: str
    role: RegionRole
    required: bool
    bbox_pt: tuple[float, float, float, float] = Field(description="x, y, width, height in points")
    z_index: int = 0
    reading_order: int = Field(ge=0)

    @model_validator(mode="after")
    def _bbox_ok(self) -> LayoutRegion:
        _, _, w, h = self.bbox_pt
        if w <= 0 or h <= 0:
            raise ValueError("bbox_pt width and height must be positive")
        return self


class TextRun(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str
    region_id: str
    text: str
    style_role: StyleRole
    font_size_pt: float = Field(gt=0)


class BrandMarkRef(BaseModel):
    """Brand mark placement checked against BrandSurfacePolicy in later PRs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mark_id: Literal["patchhive", "zero_state"]
    page_role: Literal[
        "cover",
        "title_signature",
        "colophon",
        "footer",
        "back_cover",
        "pdf_metadata",
        "copyright",
    ]
    bbox_pt: tuple[float, float, float, float]
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)


class PatchPageLayoutIR(BaseModel):
    """Authoritative composition IR before PDF/SVG adapters."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = LAYOUT_IR_SCHEMA_VERSION
    page_id: str
    page_index: int = Field(ge=0)
    page_kind: PageKind
    patch_artifact_id: str | None = None
    page_size: Literal["us_letter", "a4", "a5", "screen"]
    orientation: Literal["portrait", "landscape"] = "portrait"
    regions: tuple[LayoutRegion, ...]
    text_runs: tuple[TextRun, ...] = ()
    diagram_asset_id: str | None = None
    diagram_literal: bool = True
    reading_order: tuple[str, ...] = ()
    fit: dict[str, float | str | bool] = Field(default_factory=dict)
    brand_marks: tuple[BrandMarkRef, ...] = ()
    layout_algorithm_id: str | None = None

    @model_validator(mode="after")
    def _execution_requires_patch(self) -> PatchPageLayoutIR:
        if self.page_kind in (PageKind.EXECUTION, PageKind.APPENDIX_EXECUTION):
            if not self.patch_artifact_id:
                raise ValueError(f"page_kind={self.page_kind.value} requires patch_artifact_id")
        if self.schema_version != LAYOUT_IR_SCHEMA_VERSION:
            raise ValueError(f"unsupported layout IR schema: {self.schema_version}")
        region_ids = {r.region_id for r in self.regions}
        for rid in self.reading_order:
            if rid not in region_ids:
                raise ValueError(f"reading_order references unknown region_id: {rid}")
        for run in self.text_runs:
            if run.region_id not in region_ids:
                raise ValueError(f"text_run {run.run_id} unknown region_id: {run.region_id}")
        return self


def composition_hash(
    *,
    library_content_hash: str,
    bridge_artifact_manifest_hash: str,
    resolved_recipe_hash: str,
    layout_irs: list[PatchPageLayoutIR],
    design_engine_version: str,
) -> str:
    """Hash composition inputs (excludes PDF timestamps, store URIs, rasters)."""
    pages = sorted(
        (page.model_dump(mode="json") for page in layout_irs),
        key=lambda p: p["page_index"],
    )
    payload = {
        "library_content_hash": library_content_hash,
        "bridge_artifact_manifest_hash": bridge_artifact_manifest_hash,
        "resolved_recipe_hash": resolved_recipe_hash,
        "design_engine_version": design_engine_version,
        "layout_ir_schema_version": LAYOUT_IR_SCHEMA_VERSION,
        "pages": pages,
    }
    return canonical_sha256(payload)
