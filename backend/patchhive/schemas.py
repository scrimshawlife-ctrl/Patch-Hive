"""
Schema objects for deterministic patch semantics and rendering.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Sequence, Tuple, Union


class SignalKind(str, Enum):
    """Signal types used in patch semantics."""

    audio = "audio"
    cv = "cv"
    random = "random"
    lfo = "lfo"
    clock = "clock"
    envelope = "envelope"
    gate = "gate"


class SignalRate(str, Enum):
    """Signal rate classification used in VL2 schemas."""

    audio = "audio"
    control = "control"


class CableType(str, Enum):
    """Cable types supported by patch diagrams."""

    audio = "audio"
    cv = "cv"
    clock = "clock"
    gate = "gate"


class JackDir(str, Enum):
    """Direction of a jack on a module."""

    in_ = "in"
    out = "out"


class FieldStatus(str, Enum):
    """Status of a field's provenance."""

    confirmed = "confirmed"
    inferred = "inferred"
    unknown = "unknown"


class ProvenanceType(str, Enum):
    """Origins of a schema field."""

    manual = "manual"
    gallery = "gallery"
    derived = "derived"


class NormalledBehavior(str, Enum):
    """Rules for normalled connections."""

    break_on_insert = "break_on_insert"
    hard_normalled = "hard_normalled"


class RigSource(str, Enum):
    """Origin of a rig specification."""

    manual_picklist = "manual_picklist"


@dataclass(frozen=True)
class Provenance:
    """Provenance record for a field."""

    type: ProvenanceType
    timestamp: datetime
    evidence_ref: str
    method: Optional[str] = None


@dataclass(frozen=True)
class FieldMeta:
    """Metadata describing the source and confidence of a field."""

    provenance: Sequence[Provenance] = field(default_factory=list)
    confidence: float = 1.0
    status: FieldStatus = FieldStatus.unknown


@dataclass(frozen=True)
class Signal:
    """Signal metadata for a jack."""

    kind: SignalKind


@dataclass(frozen=True)
class Jack:
    """Canonical representation of a jack on a module."""

    jack_id: str
    label: str
    signal: Signal


@dataclass(frozen=True)
class SignalContract:
    """Detailed signal contract for module jacks."""

    kind: SignalKind
    rate: SignalRate
    range_v: Tuple[float, float]
    polarity: str
    meta: Optional[FieldMeta] = None


@dataclass(frozen=True)
class ModuleJack:
    """Gallery jack definition."""

    jack_id: str
    label: str
    dir: JackDir
    signal: SignalContract
    meta: FieldMeta


@dataclass(frozen=True)
class ModuleMode:
    """Selectable mode for a module."""

    mode_id: str
    label: str
    jack_overrides: Optional[Sequence[ModuleJack]]
    tags: Sequence[str]
    meta: FieldMeta


@dataclass(frozen=True)
class PowerSpec:
    """Power specification for a module."""

    plus12_ma: Optional[float]
    minus12_ma: Optional[float]
    plus5_ma: Optional[float]
    meta: FieldMeta


@dataclass(frozen=True)
class ModuleGalleryEntry:
    """Canonical gallery entry for a module."""

    module_gallery_id: str
    rev: datetime
    name: str
    manufacturer: str
    hp: float
    tags: Sequence[str]
    power: PowerSpec
    jacks: Sequence[ModuleJack]
    modes: Sequence[ModuleMode]
    images: Sequence[str]
    sketch_svg: Optional[str]
    provenance: Sequence[Provenance]
    notes: Sequence[str]


@dataclass(frozen=True)
class JackRef:
    """Reference to a jack on a module instance."""

    instance_id: str
    jack_id: str


@dataclass(frozen=True)
class Module:
    """Module instance inside a canonical rig."""

    instance_id: str
    hp: float
    jacks: Sequence[Jack] = field(default_factory=list)


@dataclass(frozen=True)
class ObservedPlacement:
    """Observed placement in a physical rack."""

    row_index: int
    start_hp: float


@dataclass(frozen=True)
class RigModuleInstance:
    """Instance of a module used in a rig."""

    instance_id: str
    gallery_module_id: str
    gallery_rev: Optional[datetime]
    observed_placement: Optional[ObservedPlacement]
    meta: FieldMeta


@dataclass(frozen=True)
class NormalledEdge:
    """Explicit normalled edge defined in a rig."""

    from_jack: str
    to_jack: str
    behavior: NormalledBehavior
    meta: FieldMeta


@dataclass(frozen=True)
class RigSpec:
    """Specification for a canonical rig."""

    rig_id: str
    name: str
    source: RigSource
    modules: Sequence[RigModuleInstance]
    normalled_edges: Sequence[NormalledEdge]
    provenance: Sequence[Provenance]
    notes: Sequence[str]


@dataclass(frozen=True)
class CanonicalJack:
    """Canonical jack representation with provenance."""

    jack_id: str
    label: str
    dir: JackDir
    signal: SignalContract
    meta: FieldMeta


@dataclass(frozen=True)
class CanonicalModule:
    """Module inside a canonical rig."""

    instance_id: str
    module_gallery_id: str
    module_rev: datetime
    name: str
    manufacturer: str
    hp: float
    tags: Sequence[str]
    power: PowerSpec
    jacks: Sequence[CanonicalJack]
    modes: Sequence[ModuleMode]
    observed_placement: Optional[ObservedPlacement]
    meta: FieldMeta


@dataclass(frozen=True)
class CanonicalRig:
    """Normalized module list used for semantic derivation and rendering."""

    rig_id: str
    name: str
    modules: Sequence[CanonicalModule] = field(default_factory=list)
    normalled_edges: Sequence[NormalledEdge] = field(default_factory=list)
    provenance: Sequence[Provenance] = field(default_factory=list)


@dataclass(frozen=True)
class Cable:
    """Connection between two module jacks."""

    from_jack: Union[JackRef, str]
    to_jack: Union[JackRef, str]
    type: CableType


@dataclass(frozen=True)
class PatchGraph:
    """Patch graph for deterministic semantics."""

    patch_id: str
    cables: Sequence[Cable] = field(default_factory=list)


@dataclass(frozen=True)
class Placement:
    """Module placement in a diagram layout."""

    instance_id: str
    x_hp: float
    row: int


@dataclass(frozen=True)
class Layout:
    """Row-aware layout of modules used by diagram rendering."""

    placements: List[Placement] = field(default_factory=list)
