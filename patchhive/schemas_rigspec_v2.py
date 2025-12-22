from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Literal

from pydantic import BaseModel, Field


class PHBase(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class RigInputMode(str, Enum):
    vision = "vision"
    manual = "manual"
    mixed = "mixed"


class CaseType(str, Enum):
    eurorack = "eurorack"
    semi_modular = "semi_modular"


class CaseSpecV2(PHBase):
    case_type: CaseType = CaseType.eurorack
    rows: int = 1
    row_hp: int = 104
    notes: Optional[str] = None


class InstancePlacementV2(PHBase):
    """
    Optional user-specified placement (HP units) used for diagram realism.
    If omitted, PatchHive suggests a layout.
    """
    row: int = 0
    x_hp: int = 0


class RigModuleInstanceV2(PHBase):
    instance_id: str
    module_key: str                  # links to gallery entry
    display_name: str
    hp: int

    placement: Optional[InstancePlacementV2] = None

    # Optional override set from vision extraction if gallery lacks details
    override_jack_labels: Optional[List[str]] = None


class RigSpecV2(PHBase):
    rig_id: str
    input_mode: RigInputMode = RigInputMode.mixed
    case: CaseSpecV2 = Field(default_factory=CaseSpecV2)

    modules: List[RigModuleInstanceV2]

    # provenance pointers
    image_ref: Optional[str] = None
    evidence_ref: Optional[str] = None
    notes: Optional[str] = None
