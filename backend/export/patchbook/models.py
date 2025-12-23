"""PatchBook export contract models."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

PATCHBOOK_TEMPLATE_VERSION = "1.1.0"


class PatchBookTier(str, Enum):
    """Monetization tiers for PatchBook exports."""

    FREE = "free"
    CORE = "core"
    PRO = "pro"
    STUDIO = "studio"


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


class ComplexityVector(BaseModel):
    """Patch complexity metrics."""

    cable_count: int
    unique_jack_count: int
    modulation_source_count: int
    probability_locus_count: int
    feedback_present: bool


class DominantRoles(BaseModel):
    """Distribution of module roles in the patch."""

    time_pct: float
    voice_pct: float
    modulation_pct: float
    probability_pct: float
    gesture_pct: float


class PatchFingerprint(BaseModel):
    """Computed topology fingerprint (Tier 1+)."""

    topology_hash: str
    complexity_vector: ComplexityVector
    dominant_roles: DominantRoles
    rack_fit_score: Optional[float] = None


class StabilityEnvelope(BaseModel):
    """Computed stability analysis (Tier 1+)."""

    stability_class: str  # Stable | Sensitive | Wild
    primary_instability_sources: list[str]
    safe_start_ranges: list[str]
    recovery_procedure: list[str]


class TroubleshootingTree(BaseModel):
    """Computed troubleshooting decision tree (Tier 1+)."""

    no_sound_checks: list[str]
    no_modulation_checks: list[str]
    timing_instability_checks: list[str]
    gain_staging_checks: list[str]


class PerformanceMacroCard(BaseModel):
    """Computed performance macro (Tier 1+)."""

    macro_id: str
    controls_involved: list[str]
    expected_effect: str
    safe_bounds: str
    risk_level: str  # Low | Medium | High


class WiringDiff(BaseModel):
    """Cable add/remove instruction."""

    action: str  # "add" | "remove"
    from_module: str
    from_port: str
    to_module: str
    to_port: str
    cable_type: str


class ParameterDelta(BaseModel):
    """Parameter change instruction."""

    module_name: str
    parameter: str
    from_value: str
    to_value: str


class PatchVariantComputed(BaseModel):
    """Graph-derived patch variant (Tier 2+)."""

    variant_type: str  # stabilize | wild | performance
    wiring_diff: list[WiringDiff]
    parameter_deltas: list[ParameterDelta]
    behavioral_delta_summary: str


class PatchBookPage(BaseModel):
    """PatchBook page contract."""

    header: PatchBookHeader
    module_inventory: list[PatchModulePosition] = Field(default_factory=list)
    io_inventory: list[IOEndpoint] = Field(default_factory=list)
    parameter_snapshot: list[ParameterSnapshot] = Field(default_factory=list)
    schematic: PatchSchematic
    patching_order: PatchingOrder
    variants: Optional[list[PatchVariant]] = None

    # Computed panels (tier-gated)
    fingerprint: Optional[PatchFingerprint] = None
    stability: Optional[StabilityEnvelope] = None
    troubleshooting: Optional[TroubleshootingTree] = None
    performance_macros: Optional[list[PerformanceMacroCard]] = None
    computed_variants: Optional[list[PatchVariantComputed]] = None


class RackArrangement(BaseModel):
    """Computed rack arrangement."""

    layout_id: str
    modules_in_order: list[str]
    scoring_rationale: list[str]
    adjacency_summary: str
    missing_utility_warnings: list[str]


class GoldenRackAnalysis(BaseModel):
    """Golden rack arrangement analysis (Tier 2+)."""

    golden_arrangement: Optional[RackArrangement] = None
    alternative_arrangements: list[RackArrangement] = Field(default_factory=list)


class CompatibilityReport(BaseModel):
    """Compatibility and gap analysis (Tier 2+)."""

    required_missing_utilities: list[str]
    workaround_suggestions: list[str]
    patch_compatibility_warnings: list[str]


class LearningPathStep(BaseModel):
    """One step in the learning path."""

    patch_id: int
    patch_name: str
    concepts_introduced: list[str]
    effort_score: float


class LearningPath(BaseModel):
    """Ordered learning path (Tier 2+)."""

    steps: list[LearningPathStep]


class PatchBookDocument(BaseModel):
    """PatchBook document containing pages and branding."""

    branding: PatchBookBranding
    pages: list[PatchBookPage]
    content_hash: Optional[str] = None
    tier: PatchBookTier = PatchBookTier.FREE

    # Book-level computed sections (tier-gated)
    golden_rack: Optional[GoldenRackAnalysis] = None
    compatibility: Optional[CompatibilityReport] = None
    learning_path: Optional[LearningPath] = None


class PatchBookExportRequest(BaseModel):
    """Export request payload for PatchBook."""

    rack_id: Optional[int] = None
    patch_ids: list[int] = Field(default_factory=list)
    patch_set_id: Optional[int] = None
    tier: PatchBookTier = PatchBookTier.CORE
