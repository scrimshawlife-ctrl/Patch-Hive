"""Pydantic models for PatchHive rig ingestion and patch generation."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, Field

CONFIRM_THRESHOLD: float = 0.82
DEFAULT_TIMESTAMP = datetime(1970, 1, 1, tzinfo=timezone.utc)


class ProvenanceType(str, Enum):
    GEMINI = "gemini"
    GALLERY = "gallery"
    DERIVED = "derived"
    MANUAL = "manual"


class ProvenanceStatus(str, Enum):
    CONFIRMED = "confirmed"
    INFERRED = "inferred"
    DISPUTED = "disputed"
    MISSING = "missing"


class Provenance(BaseModel):
    type: ProvenanceType
    model_version: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: DEFAULT_TIMESTAMP)
    evidence_ref: Optional[str] = None


T = TypeVar("T")


class ProvenancedValue(BaseModel, Generic[T]):
    value: Optional[T]
    provenance: Provenance
    confidence: float = Field(ge=0.0, le=1.0)
    status: ProvenanceStatus

    @classmethod
    def missing(cls, provenance_type: ProvenanceType, evidence_ref: Optional[str] = None) -> "ProvenancedValue[T]":
        return cls(
            value=None,
            provenance=Provenance(type=provenance_type, evidence_ref=evidence_ref),
            confidence=0.0,
            status=ProvenanceStatus.MISSING,
        )


class JackDirection(str, Enum):
    IN = "in"
    OUT = "out"
    BIDIRECTIONAL = "bidirectional"


class JackSignalType(str, Enum):
    AUDIO = "audio"
    CV = "cv"
    GATE = "gate"
    CLOCK = "clock"
    TRIGGER = "trigger"
    LOGIC = "logic"
    UNKNOWN = "unknown"


class JackSpec(BaseModel):
    jack_id: str
    label: str
    direction: JackDirection
    signal_type: JackSignalType
    normalled_to: Optional[str] = None


class ModeSpec(BaseModel):
    mode_id: str
    label: str
    capability_profile: list[str] = Field(default_factory=list)
    jack_overrides: list[JackSpec] = Field(default_factory=list)


class ModuleSection(BaseModel):
    section_id: str
    label: str
    capability_profile: list[str] = Field(default_factory=list)
    jacks: list[JackSpec] = Field(default_factory=list)
    modes: list[ModeSpec] = Field(default_factory=list)


class NormalledEdge(BaseModel):

class ModuleSpec(BaseModel):
    module_id: str
    name: str
    manufacturer: Optional[str] = None
    width_hp: Optional[int] = None
    sections: list[ModuleSection] = Field(default_factory=list)
    normalled_edges: list[NormalledEdge] = Field(default_factory=list)
    power_12v_ma: Optional[int] = None
    power_minus12v_ma: Optional[int] = None
    power_5v_ma: Optional[int] = None


class RigModuleInput(BaseModel):
    module_id: Optional[str] = None
    name: ProvenancedValue[str]
    manufacturer: Optional[ProvenancedValue[str]] = None
    width_hp: Optional[ProvenancedValue[int]] = None
    position_hint: Optional[ProvenancedValue[str]] = None
    observed_photo_ref: Optional[str] = None


class RigSpec(BaseModel):
    rig_id: str
    modules: list[RigModuleInput]
    notes: Optional[str] = None


class CanonicalModule(BaseModel):
    canonical_id: str
    module_spec: ModuleSpec
    provenance: Provenance
    confidence: float = Field(ge=0.0, le=1.0)
    status: ProvenanceStatus
    observed_position: Optional[str] = None


class CanonicalRig(BaseModel):
    rig_id: str
    modules: list[CanonicalModule]
    normalled_edges: list[NormalledEdge] = Field(default_factory=list)


class RigMetricsCategory(str, Enum):
    SOURCES = "Sources"
    SHAPERS = "Shapers"
    CONTROLLERS = "Controllers"
    MODULATORS = "Modulators"
    ROUTERS_MIX = "Routers/Mix"
    CLOCK_DOMAIN = "Clock Domain"
    FX_SPACE = "FX/Space"
    IO_EXTERNAL = "IO/External"
    NORMALS_INTERNAL_BUSSES = "Normals/Internal Busses"


class RigMetricsPacket(BaseModel):
    rig_id: str
    categories: dict[RigMetricsCategory, list[str]]
    summary: dict[str, int]


class DetectedModule(BaseModel):
    detection_id: str
    name: ProvenancedValue[str]
    manufacturer: Optional[ProvenancedValue[str]] = None
    photo_position: Optional[ProvenancedValue[str]] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ResolvedModuleRef(BaseModel):
    detection_id: str
    gallery_entry_id: Optional[str]
    match_confidence: float = Field(ge=0.0, le=1.0)
    status: ProvenanceStatus
    module_spec: Optional[ModuleSpec] = None
    provenance: Provenance


class ModuleGalleryEntry(BaseModel):
    entry_id: str
    revision_id: str
    previous_revision_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: DEFAULT_TIMESTAMP)
    name: str
    manufacturer: Optional[str] = None
    spec: ModuleSpec
    provenance: Provenance


class SuggestedPlacement(BaseModel):
    module_id: str
    row: int
    x_hp: int
    observed: bool = False


class SuggestedLayout(BaseModel):
    layout_id: str
    profile: str
    placements: list[SuggestedPlacement]
    score: float
    breakdown: dict[str, float]

class PatchNode(BaseModel):
    node_id: str
    module_id: str
    section_id: Optional[str] = None


class PatchEdge(BaseModel):
    edge_id: str
    from_jack: str
    to_jack: str
    signal_type: JackSignalType
    provenance: Provenance


class PatchMacro(BaseModel):
    macro_id: str
    label: str
    description: str
    nodes: list[str]


class PatchTimelinePhase(BaseModel):
    phase_id: Literal["prep", "threshold", "peak", "release", "seal"]
    description: str


class PatchGraph(BaseModel):
    rig_id: str
    nodes: list[PatchNode]
    edges: list[PatchEdge]
    normalled_edges: list[NormalledEdge] = Field(default_factory=list)
    macros: list[PatchMacro] = Field(default_factory=list)
    timeline: list[PatchTimelinePhase] = Field(default_factory=list)
    node_state: dict[str, dict[str, str]] = Field(default_factory=dict)


class PatchStep(BaseModel):
    phase_id: Literal["prep", "threshold", "peak", "release", "seal"]
    instruction: str


class PatchPlan(BaseModel):
    rig_id: str
    intent: str
    steps: list[PatchStep]
    closure: list[PatchTimelinePhase]


class ValidationIssue(BaseModel):
    code: str
    message: str
    severity: Literal["error", "warning"]


class ValidationReport(BaseModel):
    rig_id: str
    issues: list[ValidationIssue]
    warnings: list[ValidationIssue]
    stability_score: float = Field(ge=0.0, le=1.0)


class PatchIntent(BaseModel):
    description: str
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
