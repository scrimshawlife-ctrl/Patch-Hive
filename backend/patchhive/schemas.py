"""PatchHive canonical schemas (Pydantic)."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal, Dict

from pydantic import BaseModel, Field, ConfigDict


ProvenanceType = Literal["gemini", "gallery", "derived", "manual"]
StatusType = Literal["confirmed", "inferred", "disputed", "missing"]
RigSourceType = Literal["photo_gemini", "manual_picklist", "hybrid"]
LayoutType = Literal["Beginner", "Performance", "Experimental"]
SignalType = Literal["audio", "cv", "gate", "clock", "unknown"]
DirectionType = Literal["input", "output", "bidir"]
MatchMethod = Literal["exact", "fuzzy", "stub"]


class ProvenanceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: ProvenanceType
    model_version: Optional[str] = None
    timestamp: datetime
    evidence_ref: str


class EvidenceBBox(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_id: str
    bbox: List[float] = Field(..., min_length=4, max_length=4)


class DetectedModule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    temp_id: str
    label_guess: str
    brand_guess: Optional[str] = None
    hp_guess: Optional[int] = None
    position_guess: Optional[int] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: EvidenceBBox


class ResolvedModuleRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detected_id: str
    gallery_module_id: Optional[str] = None
    unknown_stub_id: Optional[str] = None
    match_method: MatchMethod
    confidence: float = Field(..., ge=0.0, le=1.0)
    status: StatusType


class JackSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jack_id: Optional[str] = None
    label: Optional[str] = None
    name: str
    signal_type: SignalType
    direction: DirectionType
    normalled_to: Optional[str] = None


class GalleryImageRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str
    kind: Literal["photo", "panel", "manual_upload", "unknown"] = "unknown"
    meta: Optional[Dict[str, str]] = None


class ModeProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    capability_profile: List[str]


class ModuleGalleryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    module_gallery_id: str
    rev: datetime
    name: str
    manufacturer: str
    hp: int
    power: Optional[Dict[str, float]] = None
    jacks: List[JackSpec]
    modes: Optional[List[ModeProfile]] = None
    images: List[GalleryImageRef] = Field(default_factory=list)
    sketch_svg: Optional[str] = Field(
        default=None,
        description="Deterministic SVG sketch (plain box + jack circles + labels).",
    )
    provenance: List[ProvenanceRecord]
    notes: List[str]

    def to_canonical_dict(self) -> Dict[str, object]:
        return self.model_dump(mode="json", by_alias=False)


class RigSpecModule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    module_gallery_id: Optional[str] = None
    unknown_stub_id: Optional[str] = None
    position_guess: Optional[int] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    provenance: ProvenanceRecord
    status: StatusType


class RigSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rig_id: str
    source: RigSourceType
    modules: List[RigSpecModule]
    observed_layout: Optional[List[Dict[str, int]]] = None
    provenance_summary: str


class NormalledEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_jack: str
    to_jack: str
    break_on_insert: bool = True


class ModuleInstance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stable_id: str
    gallery_entry: ModuleGalleryEntry
    capability_categories: List[str]
    normalled_edges: List[NormalledEdge]


class CanonicalRig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rig_id: str
    stable_ids: List[str]
    explicit_signal_contracts: List[str]
    explicit_normalled_edges: List[NormalledEdge]
    capability_surface: Dict[str, int]
    modules: List[ModuleInstance]


class RigMetricsPacket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rig_id: str
    module_count: int
    category_counts: Dict[str, int]
    modulation_budget: float
    routing_flex_score: float
    clock_coherence_score: float
    chaos_headroom: float
    learning_gradient_index: float
    performance_density_index: float


class ModulePlacement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    module_id: str
    row: int
    hp_offset: int


class SuggestedLayout(BaseModel):
    model_config = ConfigDict(extra="forbid")

    layout_type: LayoutType
    placements: List[ModulePlacement]
    total_score: float
    score_breakdown: Dict[str, float]
    rationale: str


class PatchNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    module_id: str
    label: str


class PatchCable(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_module_id: str
    from_port: str
    to_module_id: str
    to_port: str
    cable_type: SignalType


class PatchGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodes: List[PatchNode]
    cables: List[PatchCable]
    macros: List[str]
    timeline: List[str]
    mode_selections: Dict[str, str]


class PatchPlanSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    actions: List[str]


class PatchPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str
    setup: List[str]
    perform: List[PatchPlanSection]
    warnings: List[str]
    why_it_works: str


class ValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    illegal_connections: List[str]
    silence_risk: bool
    runaway_risk: bool
    stability_score: float


class SymbolicPatchEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    archetype_vector: Dict[str, float]
    temporal_intensity_curve: List[float]
    chaos_modulation_curve: List[float]
    agency_distribution: Dict[str, float]
    closure_strength: float
