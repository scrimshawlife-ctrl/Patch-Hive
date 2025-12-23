from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field

from patchhive.schemas import (
    PHBase,
    PatchGraph,
    PatchPlan,
    SymbolicPatchEnvelope,
    ValidationReport,
)


class PatchCategory(str, Enum):
    voice = "Voice"
    clocked = "Clocked"
    generative = "Generative"
    performance = "Performance Macro"
    texture = "Texture / FX Space"
    utility = "Utility / Calibration"
    study = "Study Patches"


class PatchDifficulty(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"
    experimental = "Experimental"


class PatchTier(str, Enum):
    starter = "Starter"
    core = "Core"
    deep = "Deep"
    abyss = "Abyss"


class PatchSpaceConstraints(PHBase):
    """
    Bounded patch space = what "all possible patches" means.
    """

    tier: PatchTier = PatchTier.core
    max_cables: int = 6
    allow_feedback: bool = False
    require_output_path: bool = True

    max_fan_in_per_input: int = 1
    max_fan_out_per_output: int = 4

    allow_clock_only_patches: bool = True

    max_candidates_per_template: int = 2000
    keep_top_per_template: int = 80


class PatchCard(PHBase):
    patch_id: str
    name: str
    category: PatchCategory
    difficulty: PatchDifficulty
    tags: List[str] = Field(default_factory=list)

    archetype: str
    cable_count: int
    stability_score: float
    novelty_score: float

    warnings: List[str] = Field(default_factory=list)
    rationale: str


class PatchDiagram(PHBase):
    patch_id: str
    svg: str
    width: int = 1024
    height: int = 768


class PatchLibraryItem(PHBase):
    card: PatchCard
    patch: PatchGraph
    plan: PatchPlan
    validation: ValidationReport
    envelope: SymbolicPatchEnvelope
    diagram: Optional[PatchDiagram] = None


class PatchLibrary(PHBase):
    rig_id: str
    generated_at: datetime
    constraints: PatchSpaceConstraints
    patches: List[PatchLibraryItem]


class ExportPackFile(PHBase):
    path: str
    sha256: str


class ExportPackManifest(PHBase):
    rig_id: str
    generated_at: datetime
    files: List[ExportPackFile] = Field(default_factory=list)
