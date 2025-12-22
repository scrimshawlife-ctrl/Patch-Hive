"""
Schema objects for deterministic patch semantics and rendering.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Sequence, Union


class SignalKind(str, Enum):
    """Signal types used in patch semantics."""

    audio = "audio"
    cv = "cv"
    random = "random"
    lfo = "lfo"
    clock = "clock"
    envelope = "envelope"
    gate = "gate"


class CableType(str, Enum):
    """Cable types supported by patch diagrams."""

    audio = "audio"
    cv = "cv"
    clock = "clock"
    gate = "gate"


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
class CanonicalRig:
    """Normalized module list used for semantic derivation and rendering."""

    modules: Sequence[Module] = field(default_factory=list)


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
