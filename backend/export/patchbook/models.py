"""PatchBook export contract models."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

PATCHBOOK_TEMPLATE_VERSION = "1.1.0"


class PatchBookTier(str, Enum):
    """PatchBook export tier."""

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


class WiringDelta(BaseModel):
    """Connection delta for patch variants."""

    action: str
    from_module: str
    from_port: str
    to_module: str
    to_port: str
    cable_type: str


class ParameterDelta(BaseModel):
    """Parameter delta for patch variants."""

    module_id: int
    module_name: str
    parameter: str
    from_value: str
    to_value: str


class PatchVariant(BaseModel):
    """Optional patch variant."""

    variant_type: str
    wiring_diff: list[WiringDelta] = Field(default_factory=list)
    parameter_deltas: list[ParameterDelta] = Field(default_factory=list)
    behavioral_delta_summary: str


class ComplexityVector(BaseModel):
    """Patch complexity metrics."""

    cable_count: int
    unique_jack_count: int
    modulation_source_count: int
    probability_locus_count: int
    feedback_present: bool


class DominantRoles(BaseModel):
    """Dominant role distribution (%)."""

    time: float
    voice: float
    modulation: float
    probability: float
    gesture: float


class PatchFingerprint(BaseModel):
    """Computed patch fingerprint."""

    topology_hash: str
    complexity_vector: ComplexityVector
    dominant_roles: DominantRoles
    rack_fit_score: Optional[float] = None


class StabilityEnvelope(BaseModel):
    """Computed stability envelope."""

    stability_class: str
    primary_instability_sources: list[str] = Field(default_factory=list)
    safe_start_ranges: list[str] = Field(default_factory=list)
    recovery_procedure: list[str] = Field(default_factory=list)


class TroubleshootingDecisionTree(BaseModel):
    """Troubleshooting decision tree."""

    no_sound_checks: list[str] = Field(default_factory=list)
    no_modulation_checks: list[str] = Field(default_factory=list)
    timing_instability_checks: list[str] = Field(default_factory=list)
    gain_staging_checks: list[str] = Field(default_factory=list)


class PerformanceMacroCard(BaseModel):
    """Performance macro card."""

    macro_id: str
    controls_involved: list[str]
    expected_effect: str
    safe_bounds: str
    risk_level: str


class GoldenRackLayout(BaseModel):
    """Single rack layout option."""

    layout_id: str
    score: float
    modules: list[PatchModulePosition]


class GoldenRackArrangement(BaseModel):
    """Computed golden rack arrangement."""

    layouts: list[GoldenRackLayout]
    scoring_explanation: list[str] = Field(default_factory=list)
    adjacency_heatmap_summary: str
    missing_utility_warnings: list[str] = Field(default_factory=list)


class CompatibilityGapReport(BaseModel):
    """Compatibility and utility gap report."""

    required_missing_utilities: list[str] = Field(default_factory=list)
    workaround_suggestions: list[str] = Field(default_factory=list)
    patch_compatibility_warnings: list[str] = Field(default_factory=list)


class LearningPathStep(BaseModel):
    """Learning path step."""

    patch_id: int
    patch_name: str
    concept: str
    effort_score: int


class LearningPath(BaseModel):
    """Learning path for PatchBook."""

    ordered_patch_sequence: list[LearningPathStep]
    effort_score_progression: list[int]


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
    patch_fingerprint: Optional[PatchFingerprint] = None
    stability_envelope: Optional[StabilityEnvelope] = None
    troubleshooting_tree: Optional[TroubleshootingDecisionTree] = None
    performance_macros: Optional[list[PerformanceMacroCard]] = None


class PatchBookDocument(BaseModel):
    """PatchBook document containing pages and branding."""

    branding: PatchBookBranding
    pages: list[PatchBookPage]
    content_hash: Optional[str] = None
    tier_name: str = PatchBookTier.CORE.value
    golden_rack_arrangement: Optional[GoldenRackArrangement] = None
    compatibility_report: Optional[CompatibilityGapReport] = None
    learning_path: Optional[LearningPath] = None


class PatchBookExportRequest(BaseModel):
    """Export request payload for PatchBook."""

    rack_id: Optional[int] = None
    patch_ids: list[int] = Field(default_factory=list)
    patch_set_id: Optional[int] = None
    tier: PatchBookTier = PatchBookTier.CORE
