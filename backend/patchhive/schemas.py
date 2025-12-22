from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class SignalKind(str, Enum):
    audio = "audio"
    cv = "cv"
    cv_or_audio = "cv_or_audio"
    lfo = "lfo"
    envelope = "envelope"
    random = "random"
    clock = "clock"
    gate = "gate"
    trigger = "trigger"
    pitch_cv = "pitch_cv"


class JackDir(str, Enum):
    in_ = "in"
    out = "out"
    bidir = "bidir"


@dataclass(frozen=True)
class Signal:
    kind: SignalKind


@dataclass(frozen=True)
class Jack:
    jack_id: str
    dir: JackDir
    signal: Signal


@dataclass(frozen=True)
class Module:
    instance_id: str
    jacks: List[Jack]


@dataclass(frozen=True)
class CanonicalRig:
    modules: List[Module]
