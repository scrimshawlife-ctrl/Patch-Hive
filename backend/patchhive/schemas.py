from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Literal

from pydantic import BaseModel, Field, ConfigDict


class PHBase(BaseModel):
    """Base model with canonical serialization helpers."""

    model_config = ConfigDict(extra="forbid", frozen=False)

    def to_canonical_dict(self) -> dict:
        return self.model_dump(mode="json", exclude_none=True)

    def to_canonical_json(self) -> str:
        return self.model_dump_json(exclude_none=True)


class SignalKind(str, Enum):
    audio = "audio"
    cv = "cv"
    cv_or_audio = "cv_or_audio"
    gate = "gate"
    trigger = "trigger"
    clock = "clock"
    lfo = "lfo"
    envelope = "envelope"
    random = "random"
    pitch_cv = "pitch_cv"
    unknown = "unknown"


class SignalRate(str, Enum):
    audio = "audio"
    control = "control"
    event = "event"
    unknown = "unknown"


class CableType(str, Enum):
    audio = "audio"
    cv = "cv"
    gate = "gate"
    trigger = "trigger"
    clock = "clock"
    pitch_cv = "pitch_cv"
    unknown = "unknown"


class ProvenanceType(str, Enum):
    derived = "derived"
    imported = "imported"
    manual = "manual"
    gemini = "gemini"
    unknown = "unknown"


class Provenance(PHBase):
    type: ProvenanceType
    timestamp: datetime
    evidence_ref: Optional[str] = None
    method: Optional[str] = None


class FieldStatus(str, Enum):
    inferred = "inferred"
    confirmed = "confirmed"
    unknown = "unknown"


class FieldMeta(PHBase):
    provenance: List[Provenance] = Field(default_factory=list)
    confidence: float = 0.0
    status: FieldStatus = FieldStatus.unknown


class JackDir(str, Enum):
    in_ = "in"
    out = "out"
    bidir = "bidir"


class GalleryImageRef(PHBase):
    url: str
    kind: str
    meta: FieldMeta


class ModuleJackEntry(PHBase):
    jack_id: str
    label: Optional[str] = None
    dir: JackDir = JackDir.bidir
    signal: SignalContract


class ModuleGalleryEntry(PHBase):
    module_gallery_id: str
    rev: datetime
    canonical_name: str
    hp: Optional[int] = None
    images: List[GalleryImageRef] = Field(default_factory=list)
    jacks: List[ModuleJackEntry] = Field(default_factory=list)
    sketch: Optional[str] = None
    meta: Optional[FieldMeta] = None


class JackFunctionEntry(PHBase):
    """
    Append-only registry of jack-level functions.
    This is how we represent proprietary / vendor-specific behaviors
    without exploding SignalKind.

    Example:
      function_id: "fn.erica.vl2.chaos_bus"
      label_aliases: ["CHAOS", "XBUS", "FOLD AMT"]
      kind_hint: "cv" (still coarse)
    """

    function_id: str
    rev: datetime
    canonical_name: str
    description: str
    label_aliases: List[str] = Field(default_factory=list)

    # coarse mapping stays separate from true function identity
    kind_hint: SignalKind = SignalKind.unknown

    provenance: List[Provenance] = Field(default_factory=list)
    meta: FieldMeta


class SignalContract(PHBase):
    kind: SignalKind
    rate: SignalRate
    range_v: Optional[Tuple[float, float]] = None
    polarity: Optional[Literal["unipolar", "bipolar", "unknown"]] = "unknown"
    notes: Optional[str] = None

    # NEW:
    function_id: Optional[str] = Field(
        default=None,
        description="Optional pointer to JackFunctionEntry.function_id for proprietary named behaviors.",
    )

    meta: Optional[FieldMeta] = None


class VisionEvidence(PHBase):
    image_id: str
    bbox: Optional[Tuple[float, float, float, float]] = None


class DetectedModule(PHBase):
    """
    Vision-only detection of a module.
    Never canonical. Used to propose gallery matches later.
    """

    temp_id: str
    label_guess: str
    brand_guess: Optional[str] = None
    hp_guess: Optional[int] = None
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: VisionEvidence


class DetectedJack(PHBase):
    """
    Vision-only detection of a jack.
    Never canonical. Used to propose SignalContract + function_id later.
    """

    temp_jack_id: str
    label_guess: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: Optional[Tuple[float, float, float, float]] = None
    meta: FieldMeta


class VisionRigDetection(PHBase):
    """
    Output of Phase 7.
    This is a proposal bundle only.
    """

    image_id: str
    detected_modules: List[DetectedModule] = Field(default_factory=list)
    detected_jacks: dict[str, List[DetectedJack]] = Field(default_factory=dict)
    proposed_functions: List[JackFunctionEntry] = Field(default_factory=list)
    provenance: List[Provenance] = Field(default_factory=list)


class PatchIntent(PHBase):
    archetype: str
    energy: str
    focus: str
    meta: FieldMeta


class PatchPlan(PHBase):
    intent: PatchIntent
    patch_id: Optional[str] = None
    setup: List[str] = Field(default_factory=list)
    perform: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    why_it_works: List[str] = Field(default_factory=list)
    meta: Optional[FieldMeta] = None


class TimelineSection(str, Enum):
    prep = "prep"
    threshold = "threshold"
    peak = "peak"
    release = "release"
    seal = "seal"


class PatchTimeline(PHBase):
    clock_bpm: Optional[float] = None
    sections: List[TimelineSection] = Field(default_factory=list)
    meta: Optional[FieldMeta] = None


class PatchCable(PHBase):
    from_jack: Optional[str] = None
    to_jack: Optional[str] = None
    type: CableType
    meta: Optional[FieldMeta] = None


class MacroControl(PHBase):
    range: Tuple[float, float]


class PatchMacro(PHBase):
    macro_id: str
    controls: List[MacroControl] = Field(default_factory=list)


class PatchGraph(PHBase):
    patch_id: str
    rig_id: str
    timeline: PatchTimeline
    cables: List[PatchCable] = Field(default_factory=list)
    macros: List[PatchMacro] = Field(default_factory=list)
    mode_selections: List[str] = Field(default_factory=list)
    meta: Optional[FieldMeta] = None


class SymbolicPatchEnvelope(PHBase):
    patch_id: str
    archetype_vector: Dict[str, float]
    temporal_intensity_curve: List[float]
    chaos_modulation_curve: List[float]
    agency_distribution: Dict[str, float]
    closure_strength: float
    meta: FieldMeta


class RigMetricsPacket(PHBase):
    routing_flex_score: float


class LayoutType(str, Enum):
    grid = "grid"
    stacked = "stacked"
    vertical = "vertical"


class LayoutScoreBreakdown(PHBase):
    learning_gradient: float


class SuggestedLayout(PHBase):
    layout_type: LayoutType
    total_score: float
    score_breakdown: LayoutScoreBreakdown
    placements: List["LayoutPlacement"] = Field(default_factory=list)


class LayoutPlacement(PHBase):
    instance_id: str
    x_hp: float
    hp: Optional[float] = None


class RigSpec(PHBase):
    rig_id: str
    module_gallery_ids: List[str] = Field(default_factory=list)


class CanonicalRigJack(PHBase):
    jack_id: str
    label: Optional[str] = None
    dir: JackDir
    signal: SignalContract


class CanonicalRigModule(PHBase):
    instance_id: str
    name: str
    hp: int = 0
    jacks: List[CanonicalRigJack] = Field(default_factory=list)


class CanonicalRig(PHBase):
    rig_id: str
    modules: List[CanonicalRigModule] = Field(default_factory=list)


class ValidationReport(PHBase):
    ok: bool
    warnings: List[str] = Field(default_factory=list)
    stability_score: float = 1.0
    illegal_connections: List[str] = Field(default_factory=list)
    silence_risk: List[str] = Field(default_factory=list)
    runaway_risk: List[str] = Field(default_factory=list)


class PatchHiveBundle(PHBase):
    """
    One-shot export artifact for UI + Abraxas consumption.
    Pure data bundle; no side effects.
    """

    image_id: Optional[str] = None
    rig_id: str
    canonical_rig: CanonicalRig
    metrics: RigMetricsPacket
    layouts: List[SuggestedLayout]
    patch: PatchGraph
    plan: PatchPlan
    validation: ValidationReport
    envelope: SymbolicPatchEnvelope
    variations: List[PatchGraph] = Field(default_factory=list)
    meta: FieldMeta
