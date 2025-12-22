from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field


# =========================
# Determinism & Serialization
# =========================


class PHBase(BaseModel):
    """
    PatchHive base model:
    - strict-ish validation
    - deterministic JSON export via explicit helpers
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=False,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    def to_canonical_dict(self) -> Dict[str, Any]:
        """
        Deterministic dict form for hashing / golden tests.
        - no None fields
        - stable key ordering achieved at json serialization time via sort_keys=True
        """

        return self.model_dump(mode="json", exclude_none=True)

    def to_canonical_json(self) -> str:
        """
        Deterministic JSON (sort_keys, compact separators) for byte-identical tests.
        """

        import json

        return json.dumps(self.to_canonical_dict(), sort_keys=True, separators=(",", ":"))


# =========================
# Provenance / Confidence
# =========================


class ProvenanceType(str, Enum):
    gemini = "gemini"
    gallery = "gallery"
    derived = "derived"
    manual = "manual"


class FieldStatus(str, Enum):
    confirmed = "confirmed"
    inferred = "inferred"
    disputed = "disputed"
    missing = "missing"


class Provenance(PHBase):
    type: ProvenanceType
    timestamp: datetime
    evidence_ref: str = Field(
        ...,
        description="Opaque pointer: image_id:bbox:..., doc id, user confirmation id, etc.",
    )
    model_version: Optional[str] = Field(
        default=None,
        description="Model/version string when type=gemini or similar.",
    )
    method: Optional[str] = Field(
        default=None,
        description="Derivation method description when type=derived.",
    )


class FieldMeta(PHBase):
    provenance: List[Provenance] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    status: FieldStatus


# =========================
# Vision Output
# =========================

BBox = Tuple[float, float, float, float]  # x1,y1,x2,y2 normalized 0..1


class VisionEvidence(PHBase):
    image_id: str
    bbox: BBox


class DetectedModule(PHBase):
    """
    Output of detect_modules_from_photo (Gemini wrapper).
    This is a proposal only. Never authoritative.
    """

    temp_id: str
    label_guess: str
    brand_guess: Optional[str] = None
    hp_guess: Optional[int] = Field(default=None, ge=1)
    position_guess: Optional[Dict[str, int]] = Field(
        default=None,
        description="Optional hint: {'row': int, 'x_hp': int}. Observed, not ideal.",
    )
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: VisionEvidence


class MatchMethod(str, Enum):
    exact = "exact"
    fuzzy = "fuzzy"
    unknown_stub = "unknown_stub"


class ResolvedModuleRef(PHBase):
    """
    Output of resolve_modules. Exactly one of gallery_module_id or unknown_stub_id must be present.
    """

    detected_id: str
    gallery_module_id: Optional[str] = None
    unknown_stub_id: Optional[str] = None
    match_method: MatchMethod
    confidence: float = Field(ge=0.0, le=1.0)
    status: FieldStatus

    def model_post_init(self, __context: Any) -> None:
        has_gallery = self.gallery_module_id is not None
        has_stub = self.unknown_stub_id is not None
        if has_gallery == has_stub:
            raise ValueError(
                "ResolvedModuleRef: exactly one of gallery_module_id or unknown_stub_id must be set."
            )


# =========================
# Module Gallery
# =========================


class SignalRate(str, Enum):
    control = "control"
    audio = "audio"
    either = "either"


class SignalKind(str, Enum):
    pitch_cv = "pitch_cv"
    gate = "gate"
    trigger = "trigger"
    clock = "clock"
    envelope = "envelope"
    lfo = "lfo"
    random = "random"
    cv = "cv"
    audio = "audio"
    cv_or_audio = "cv_or_audio"
    midi = "midi"
    unknown = "unknown"


class SignalContract(PHBase):
    kind: SignalKind
    rate: SignalRate
    # range may be unknown; if known, keep as volts; if not, None
    range_v: Optional[Tuple[float, float]] = None
    polarity: Optional[Literal["unipolar", "bipolar", "unknown"]] = "unknown"
    notes: Optional[str] = None
    meta: Optional[FieldMeta] = None


class JackDir(str, Enum):
    in_ = "in"
    out = "out"
    bidir = "bidir"


class ModuleJack(PHBase):
    jack_id: str
    label: str
    dir: JackDir
    signal: SignalContract
    meta: FieldMeta


class ModuleMode(PHBase):
    """
    Modeful blocks: distinct capability profiles and/or jack contract overrides.
    """

    mode_id: str
    label: str
    # If present, overrides apply to jack signal contracts for this mode
    jack_overrides: Optional[Dict[str, SignalContract]] = None
    # Capability tags (e.g., "envelope", "lfo", "oscillator")
    tags: List[str] = Field(default_factory=list)
    meta: FieldMeta


class PowerSpec(PHBase):
    """
    NEVER invent power specs. Missing means missing.
    Use integers where known; None where missing.
    """

    plus12_ma: Optional[int] = Field(default=None, ge=0)
    minus12_ma: Optional[int] = Field(default=None, ge=0)
    plus5_ma: Optional[int] = Field(default=None, ge=0)
    meta: FieldMeta


class ModuleGalleryEntry(PHBase):
    """
    Append-only, versioned.
    module_gallery_id stable across revs; rev identifies immutable revision.
    """

    module_gallery_id: str
    rev: datetime
    name: str
    manufacturer: str
    hp: int = Field(ge=1)
    tags: List[str] = Field(default_factory=list)

    power: PowerSpec
    jacks: List[ModuleJack] = Field(default_factory=list)
    modes: List[ModuleMode] = Field(default_factory=list)

    provenance: List[Provenance] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


# =========================
# Rig Spec / Canonical Rig
# =========================


class RigSource(str, Enum):
    photo_gemini = "photo_gemini"
    manual_picklist = "manual_picklist"
    hybrid = "hybrid"


class ObservedPlacement(PHBase):
    """
    Observed case position for a module instance. Not considered ideal.
    """

    row: int = Field(ge=0)
    x_hp: int = Field(ge=0)
    meta: FieldMeta


class RigModuleInstance(PHBase):
    """
    A module instance as it appears in a rig.
    This points to a gallery id + optional rev (rev optional to allow "latest").
    """

    instance_id: str
    gallery_module_id: str
    gallery_rev: Optional[datetime] = None
    observed_placement: Optional[ObservedPlacement] = None
    meta: FieldMeta


class NormalledBehavior(str, Enum):
    break_on_insert = "break_on_insert"
    always_connected = "always_connected"
    unknown = "unknown"


class NormalledEdge(PHBase):
    """
    Explicit semi-normalled/internal routes (VL2 critical).
    """

    from_jack: str
    to_jack: str
    behavior: NormalledBehavior
    meta: FieldMeta


class RigSpec(PHBase):
    rig_id: str
    name: str
    source: RigSource
    modules: List[RigModuleInstance] = Field(default_factory=list)
    normalled_edges: List[NormalledEdge] = Field(default_factory=list)
    provenance: List[Provenance] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class CanonicalJack(PHBase):
    """
    Normalized jack in CanonicalRig.
    """

    jack_id: str
    label: str
    dir: JackDir
    signal: SignalContract
    # mode-specific overrides are represented in CanonicalModeState (below)
    meta: FieldMeta


class CanonicalModule(PHBase):
    """
    Normalized module representation after gallery resolution + rev pinning.
    """

    instance_id: str
    module_gallery_id: str
    module_rev: datetime
    name: str
    manufacturer: str
    hp: int
    tags: List[str] = Field(default_factory=list)
    power: PowerSpec
    jacks: List[CanonicalJack] = Field(default_factory=list)
    modes: List[ModuleMode] = Field(default_factory=list)
    observed_placement: Optional[ObservedPlacement] = None
    meta: FieldMeta


class CanonicalRig(PHBase):
    rig_id: str
    name: str
    modules: List[CanonicalModule] = Field(default_factory=list)
    normalled_edges: List[NormalledEdge] = Field(default_factory=list)
    provenance: List[Provenance] = Field(default_factory=list)


# =========================
# Rig Metrics Packet (Abraxas surface)
# =========================


class CapabilityCategory(str, Enum):
    sources = "Sources"
    shapers = "Shapers"
    controllers = "Controllers"
    modulators = "Modulators"
    routers_mix = "Routers/Mix"
    clock_domain = "Clock Domain"
    fx_space = "FX/Space"
    io_external = "IO/External"
    normals_internal = "Normals/Internal Busses"


class RigMetricsPacket(PHBase):
    rig_id: str
    module_count: int = Field(ge=0)
    category_counts: Dict[CapabilityCategory, int] = Field(default_factory=dict)

    modulation_budget: float = Field(ge=0.0)
    routing_flex_score: float = Field(ge=0.0)
    clock_coherence_score: float = Field(ge=0.0)
    chaos_headroom: float = Field(ge=0.0)

    learning_gradient_index: float = Field(ge=0.0)
    performance_density_index: float = Field(ge=0.0)

    meta: FieldMeta


# =========================
# Layout Suggestions
# =========================


class LayoutType(str, Enum):
    beginner = "Beginner"
    performance = "Performance"
    experimental = "Experimental"


class LayoutPlacement(PHBase):
    instance_id: str
    row: int = Field(ge=0)
    x_hp: int = Field(ge=0)


class LayoutScoreBreakdown(PHBase):
    reach_cost: float = Field(ge=0.0)
    cable_cross_cost: float = Field(ge=0.0)
    learning_gradient: float = Field(ge=0.0)
    utility_proximity: float = Field(ge=0.0)
    patch_template_coverage: float = Field(ge=0.0)


class SuggestedLayout(PHBase):
    rig_id: str
    layout_type: LayoutType
    placements: List[LayoutPlacement] = Field(default_factory=list)
    total_score: float
    score_breakdown: LayoutScoreBreakdown
    rationale: str
    meta: FieldMeta


# =========================
# PatchGraph / PatchPlan / Validation
# =========================


class CableType(str, Enum):
    pitch_cv = "pitch_cv"
    gate = "gate"
    trigger = "trigger"
    clock = "clock"
    cv = "cv"
    audio = "audio"
    unknown = "unknown"


class PatchCable(PHBase):
    from_jack: str
    to_jack: str
    type: CableType
    meta: FieldMeta


class MacroControl(PHBase):
    target: str
    range: Tuple[float, float]
    meta: FieldMeta


class PatchMacro(PHBase):
    macro_id: str
    controls: List[MacroControl] = Field(default_factory=list)
    meta: FieldMeta


class TimelineSection(str, Enum):
    prep = "prep"
    threshold = "threshold"
    peak = "peak"
    release = "release"
    seal = "seal"


class PatchTimeline(PHBase):
    clock_bpm: Optional[float] = Field(default=None, ge=1.0)
    sections: List[TimelineSection] = Field(default_factory=list)
    meta: FieldMeta


class ModeSelection(PHBase):
    """
    Explicit mode selections per module or section.
    Keys should reference known module instance ids (or sub-section ids if you model them).
    """

    target_id: str
    mode_id: str
    meta: FieldMeta


class PatchGraph(PHBase):
    patch_id: str
    rig_id: str
    cables: List[PatchCable] = Field(default_factory=list)
    macros: List[PatchMacro] = Field(default_factory=list)
    timeline: PatchTimeline
    mode_selections: List[ModeSelection] = Field(default_factory=list)
    meta: FieldMeta


class PatchIntent(PHBase):
    archetype: str
    energy: str
    focus: str
    meta: FieldMeta


class PatchPlan(PHBase):
    patch_id: str
    intent: PatchIntent
    setup: List[str] = Field(default_factory=list)
    perform: List[str] = Field(
        default_factory=list,
        description="Must contain ritual sequence: prep→threshold→peak→release→seal (human-readable steps).",
    )
    warnings: List[str] = Field(default_factory=list)
    why_it_works: List[str] = Field(default_factory=list)
    meta: FieldMeta


class ValidationReport(PHBase):
    patch_id: str
    illegal_connections: List[str] = Field(default_factory=list)
    silence_risk: List[str] = Field(default_factory=list)
    runaway_risk: List[str] = Field(default_factory=list)
    stability_score: float = Field(ge=0.0, le=1.0)
    meta: FieldMeta


# =========================
# Abraxas Bridge: SymbolicPatchEnvelope
# =========================


class SymbolicPatchEnvelope(PHBase):
    """
    The only symbolic surface exposed to Abraxas for a patch.
    Must be derived mechanically from PatchGraph + PatchPlan later (not here).
    """

    patch_id: str
    archetype_vector: Dict[str, float] = Field(default_factory=dict)  # e.g. {"Trickster":0.7,"Architect":0.2}
    temporal_intensity_curve: List[float] = Field(default_factory=list)  # normalized 0..1
    chaos_modulation_curve: List[float] = Field(default_factory=list)  # normalized 0..1
    agency_distribution: Dict[str, float] = Field(default_factory=dict)  # e.g. {"performer":0.6,"automation":0.4}
    closure_strength: float = Field(ge=0.0, le=1.0)
    meta: FieldMeta
