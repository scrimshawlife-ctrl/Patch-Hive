from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
import json


class CapabilityCategory(str, Enum):
    sources = "sources"
    shapers = "shapers"
    controllers = "controllers"
    modulators = "modulators"
    routers_mix = "routers_mix"
    clock_domain = "clock_domain"
    fx_space = "fx_space"
    io_external = "io_external"
    normals_internal = "normals_internal"


class SignalKind(str, Enum):
    audio = "audio"
    pitch_cv = "pitch_cv"
    gate = "gate"
    trigger = "trigger"
    clock = "clock"
    envelope = "envelope"
    lfo = "lfo"
    random = "random"
    midi = "midi"
    cv = "cv"
    cv_or_audio = "cv_or_audio"
    unknown = "unknown"


class SignalRate(str, Enum):
    audio = "audio"
    control = "control"


class FieldStatus(str, Enum):
    inferred = "inferred"
    confirmed = "confirmed"


class ProvenanceType(str, Enum):
    derived = "derived"
    manual = "manual"


@dataclass(frozen=True)
class Provenance:
    type: ProvenanceType
    timestamp: datetime
    evidence_ref: str
    method: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(timespec="seconds"),
            "evidence_ref": self.evidence_ref,
        }
        if self.method is not None:
            payload["method"] = self.method
        return payload


@dataclass(frozen=True)
class FieldMeta:
    provenance: List[Provenance]
    confidence: float
    status: FieldStatus

    def to_dict(self) -> Dict[str, object]:
        return {
            "provenance": [p.to_dict() for p in self.provenance],
            "confidence": self.confidence,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class PowerSpec:
    plus12_ma: Optional[float]
    minus12_ma: Optional[float]
    plus5_ma: Optional[float]
    meta: Optional[FieldMeta] = None


class JackDir(str, Enum):
    in_ = "in"
    out = "out"
    bidir = "bidir"


@dataclass(frozen=True)
class SignalContract:
    kind: SignalKind
    rate: SignalRate
    range_v: Optional[Tuple[float, float]]
    polarity: str
    meta: Optional[FieldMeta] = None


@dataclass(frozen=True)
class ModuleJack:
    jack_id: str
    label: str
    dir: JackDir
    signal: SignalContract
    meta: Optional[FieldMeta] = None


@dataclass(frozen=True)
class ModuleGalleryEntry:
    module_gallery_id: str
    rev: datetime
    name: str
    manufacturer: str
    hp: int
    tags: List[str] = field(default_factory=list)
    power: Optional[PowerSpec] = None
    jacks: List[ModuleJack] = field(default_factory=list)
    modes: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    sketch_svg: Optional[str] = None
    provenance: List[Provenance] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


class RigSource(str, Enum):
    manual_picklist = "manual_picklist"


class NormalledBehavior(str, Enum):
    break_on_insert = "break_on_insert"


@dataclass(frozen=True)
class NormalledEdge:
    from_jack: str
    to_jack: str
    behavior: NormalledBehavior
    meta: Optional[FieldMeta] = None


@dataclass(frozen=True)
class RigModuleInstance:
    instance_id: str
    gallery_module_id: str
    gallery_rev: Optional[datetime]
    observed_placement: Optional[str]
    meta: Optional[FieldMeta] = None


@dataclass(frozen=True)
class RigSpec:
    rig_id: str
    name: str
    source: RigSource
    modules: List[RigModuleInstance] = field(default_factory=list)
    normalled_edges: List[NormalledEdge] = field(default_factory=list)
    provenance: List[Provenance] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class SignalSpec:
    kind: SignalKind


@dataclass(frozen=True)
class CanonicalJack:
    jack_id: str
    label: str
    dir: JackDir
    signal: SignalContract


@dataclass(frozen=True)
class CanonicalMode:
    name: str
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CanonicalModule:
    instance_id: str
    hp: int
    tags: List[str] = field(default_factory=list)
    modes: List[CanonicalMode] = field(default_factory=list)
    jacks: List[CanonicalJack] = field(default_factory=list)


@dataclass(frozen=True)
class CanonicalRig:
    rig_id: str
    modules: List[CanonicalModule] = field(default_factory=list)


@dataclass(frozen=True)
class RigMetricsPacket:
    rig_id: str
    module_count: int
    category_counts: Dict[CapabilityCategory, int]
    modulation_budget: float
    routing_flex_score: float
    clock_coherence_score: float
    chaos_headroom: float
    learning_gradient_index: float
    performance_density_index: float
    meta: FieldMeta

    def to_canonical_dict(self) -> Dict[str, object]:
        category_counts = {
            cat.value: int(self.category_counts.get(cat, 0))
            for cat in sorted(self.category_counts, key=lambda c: c.value)
        }
        return {
            "rig_id": self.rig_id,
            "module_count": self.module_count,
            "category_counts": category_counts,
            "modulation_budget": self.modulation_budget,
            "routing_flex_score": self.routing_flex_score,
            "clock_coherence_score": self.clock_coherence_score,
            "chaos_headroom": self.chaos_headroom,
            "learning_gradient_index": self.learning_gradient_index,
            "performance_density_index": self.performance_density_index,
            "meta": self.meta.to_dict(),
        }

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_canonical_dict(), sort_keys=True)


class LayoutType(str, Enum):
    beginner = "Beginner"
    performance = "Performance"
    experimental = "Experimental"


@dataclass(frozen=True)
class LayoutPlacement:
    instance_id: str
    row: int
    x_hp: int

    def to_dict(self) -> Dict[str, object]:
        return {
            "instance_id": self.instance_id,
            "row": self.row,
            "x_hp": self.x_hp,
        }


@dataclass(frozen=True)
class LayoutScoreBreakdown:
    reach_cost: float
    cable_cross_cost: float
    learning_gradient: float
    utility_proximity: float
    patch_template_coverage: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "reach_cost": self.reach_cost,
            "cable_cross_cost": self.cable_cross_cost,
            "learning_gradient": self.learning_gradient,
            "utility_proximity": self.utility_proximity,
            "patch_template_coverage": self.patch_template_coverage,
        }


@dataclass(frozen=True)
class SuggestedLayout:
    rig_id: str
    layout_type: LayoutType
    placements: List[LayoutPlacement]
    total_score: float
    score_breakdown: LayoutScoreBreakdown
    rationale: str
    meta: FieldMeta

    def to_canonical_dict(self) -> Dict[str, object]:
        placements = [p.to_dict() for p in self.placements]
        return {
            "rig_id": self.rig_id,
            "layout_type": self.layout_type.value,
            "placements": placements,
            "total_score": self.total_score,
            "score_breakdown": self.score_breakdown.to_dict(),
            "rationale": self.rationale,
            "meta": self.meta.to_dict(),
        }

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_canonical_dict(), sort_keys=True)


class CableType(str, Enum):
    audio = "audio"
    pitch_cv = "pitch_cv"
    gate = "gate"
    trigger = "trigger"
    clock = "clock"
    cv = "cv"


@dataclass(frozen=True)
class PatchCable:
    from_jack: str
    to_jack: str
    type: CableType
    meta: FieldMeta

    def to_dict(self) -> Dict[str, object]:
        return {
            "from_jack": self.from_jack,
            "to_jack": self.to_jack,
            "type": self.type.value,
            "meta": self.meta.to_dict(),
        }


@dataclass(frozen=True)
class MacroControl:
    target: str
    range: Tuple[float, float]
    meta: FieldMeta

    def to_dict(self) -> Dict[str, object]:
        return {
            "target": self.target,
            "range": list(self.range),
            "meta": self.meta.to_dict(),
        }


@dataclass(frozen=True)
class PatchMacro:
    macro_id: str
    controls: List[MacroControl]
    meta: FieldMeta

    def to_dict(self) -> Dict[str, object]:
        return {
            "macro_id": self.macro_id,
            "controls": [c.to_dict() for c in self.controls],
            "meta": self.meta.to_dict(),
        }


class TimelineSection(str, Enum):
    prep = "prep"
    threshold = "threshold"
    peak = "peak"
    release = "release"
    seal = "seal"


@dataclass(frozen=True)
class PatchTimeline:
    clock_bpm: Optional[float]
    sections: List[TimelineSection]
    meta: FieldMeta

    def to_dict(self) -> Dict[str, object]:
        return {
            "clock_bpm": self.clock_bpm,
            "sections": [s.value for s in self.sections],
            "meta": self.meta.to_dict(),
        }


@dataclass(frozen=True)
class PatchGraph:
    patch_id: str
    rig_id: str
    cables: List[PatchCable]
    macros: List[PatchMacro]
    timeline: PatchTimeline
    mode_selections: List[str]
    meta: FieldMeta

    def to_canonical_dict(self) -> Dict[str, object]:
        return {
            "patch_id": self.patch_id,
            "rig_id": self.rig_id,
            "cables": [c.to_dict() for c in self.cables],
            "macros": [m.to_dict() for m in self.macros],
            "timeline": self.timeline.to_dict(),
            "mode_selections": list(self.mode_selections),
            "meta": self.meta.to_dict(),
        }

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_canonical_dict(), sort_keys=True)

    def model_copy(self, update: Dict[str, object]) -> "PatchGraph":
        data = {
            "patch_id": self.patch_id,
            "rig_id": self.rig_id,
            "cables": self.cables,
            "macros": self.macros,
            "timeline": self.timeline,
            "mode_selections": self.mode_selections,
            "meta": self.meta,
        }
        data.update(update)
        return PatchGraph(**data)


@dataclass(frozen=True)
class PatchIntent:
    archetype: str
    energy: str
    focus: str
    meta: FieldMeta

    def to_dict(self) -> Dict[str, object]:
        return {
            "archetype": self.archetype,
            "energy": self.energy,
            "focus": self.focus,
            "meta": self.meta.to_dict(),
        }


@dataclass(frozen=True)
class PatchPlan:
    patch_id: str
    intent: PatchIntent
    setup: List[str]
    perform: List[str]
    warnings: List[str]
    why_it_works: List[str]
    meta: FieldMeta

    def to_canonical_dict(self) -> Dict[str, object]:
        return {
            "patch_id": self.patch_id,
            "intent": self.intent.to_dict(),
            "setup": list(self.setup),
            "perform": list(self.perform),
            "warnings": list(self.warnings),
            "why_it_works": list(self.why_it_works),
            "meta": self.meta.to_dict(),
        }

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_canonical_dict(), sort_keys=True)


@dataclass(frozen=True)
class ValidationReport:
    patch_id: str
    illegal_connections: List[str]
    silence_risk: List[str]
    runaway_risk: List[str]
    stability_score: float
    meta: FieldMeta

    def to_canonical_dict(self) -> Dict[str, object]:
        return {
            "patch_id": self.patch_id,
            "illegal_connections": list(self.illegal_connections),
            "silence_risk": list(self.silence_risk),
            "runaway_risk": list(self.runaway_risk),
            "stability_score": self.stability_score,
            "meta": self.meta.to_dict(),
        }

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_canonical_dict(), sort_keys=True)
