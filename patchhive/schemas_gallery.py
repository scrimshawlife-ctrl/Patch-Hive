from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PHBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class FieldStatus(str, Enum):
    confirmed = "confirmed"
    inferred = "inferred"
    unknown = "unknown"


class ProvenanceType(str, Enum):
    manual = "manual"
    derived = "derived"
    vision = "vision"
    scraped = "scraped"


class Provenance(PHBase):
    type: ProvenanceType
    timestamp: datetime
    evidence_ref: str
    method: Optional[str] = None


class FieldMeta(PHBase):
    provenance: List[Provenance]
    confidence: float = 0.8
    status: FieldStatus = FieldStatus.inferred


class FunctionDef(PHBase):
    """
    Function registry entry: maps a jack label/name to a normalized function id + semantics.
    This is how we normalize proprietary jack names over time.
    """

    function_id: str
    display_name: str
    aliases: List[str] = Field(default_factory=list)
    signal_kind: str
    direction: str
    notes: Optional[str] = None
    meta: FieldMeta


class FunctionRegistry(PHBase):
    """
    Registry keyed by function_id; also supports alias lookup.
    """

    functions: Dict[str, FunctionDef] = Field(default_factory=dict)
    alias_index: Dict[str, str] = Field(default_factory=dict)
    meta: FieldMeta


class JackSketch(PHBase):
    """
    Minimal jack visual metadata (plain sketch).
    """

    jack_id: str
    label: str
    x: float
    y: float
    meta: FieldMeta


class ModuleSketch(PHBase):
    """
    Plain sketch for a module: rectangle + jack coordinates.
    The gallery always has this even if we don't have a real image.
    """

    module_key: str
    width_px: int = 512
    height_px: int = 768
    hp: int
    jacks: List[JackSketch]
    svg: str
    meta: FieldMeta


class ModuleImage(PHBase):
    """
    Optional real image asset. User can upload this if auto-find fails.
    """

    module_key: str
    image_ref: str
    source: str
    meta: FieldMeta
