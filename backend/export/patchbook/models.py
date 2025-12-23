"""PatchBook export contract models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

PATCHBOOK_TEMPLATE_VERSION = "1.0.0"


class PatchBookHeader(BaseModel):
    """Header metadata for a PatchBook page."""

    title: str
    patch_id: int
    rack_id: int
    rack_name: str
    template_version: str = PATCHBOOK_TEMPLATE_VERSION


class PatchModulePosition(BaseModel):
    """Module inventory item with position data."""

    module_id: int
    brand: str
    name: str
    hp: int
    row_index: Optional[int] = None
    start_hp: Optional[int] = None


class IOEndpoint(BaseModel):
    """I/O endpoint used by the patch."""

    module_id: int
    module_name: str
    port_name: str
    port_type: Optional[str] = None
    direction: str


class ParameterSnapshot(BaseModel):
    """Captured parameter state for a module."""

    module_id: int
    module_name: str
    parameter: str
    value: str


class WiringConnection(BaseModel):
    """Fallback wiring list entry."""

    from_module: str
    from_port: str
    to_module: str
    to_port: str
    cable_type: str


class PatchSchematic(BaseModel):
    """Rendered schematic data for a patch."""

    diagram_svg: Optional[str] = None
    wiring_list: list[WiringConnection] = Field(default_factory=list)


class PatchingStep(BaseModel):
    """One step in the patching order."""

    step: int = Field(..., ge=0, le=6)
    action: str
    expected_behavior: str
    fail_fast_check: str


class PatchingOrder(BaseModel):
    """Ordered patching instructions (Step 0-6)."""

    steps: list[PatchingStep]


class PatchVariant(BaseModel):
    """Optional patch variant."""

    name: str
    description: Optional[str] = None


class PatchBookBranding(BaseModel):
    """Branding metadata for PatchBook exports."""

    primary_color: str
    accent_color: str
    font_family: str
    template_version: str = PATCHBOOK_TEMPLATE_VERSION
    wordmark_svg: Optional[str] = None


class PatchBookPage(BaseModel):
    """PatchBook page contract."""

    header: PatchBookHeader
    module_inventory: list[PatchModulePosition] = Field(default_factory=list)
    io_inventory: list[IOEndpoint] = Field(default_factory=list)
    parameter_snapshot: list[ParameterSnapshot] = Field(default_factory=list)
    schematic: PatchSchematic
    patching_order: PatchingOrder
    variants: Optional[list[PatchVariant]] = None


class PatchBookDocument(BaseModel):
    """PatchBook document containing pages and branding."""

    branding: PatchBookBranding
    pages: list[PatchBookPage]
    content_hash: Optional[str] = None


class PatchBookExportRequest(BaseModel):
    """Export request payload for PatchBook."""

    rack_id: Optional[int] = None
    patch_ids: list[int] = Field(default_factory=list)
    patch_set_id: Optional[int] = None
