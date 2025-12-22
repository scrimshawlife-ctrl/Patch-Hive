from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from patchhive.schemas import PatchGraph, PatchPlan, ValidationReport


class PatchCategory(str, Enum):
    Voice = "Voice"
    Clocked = "Clocked"
    Generative = "Generative"
    StudyPatches = "Study Patches"
    UtilityCalibration = "Utility / Calibration"
    TextureFXSpace = "Texture / FX Space"
    PerformanceMacro = "Performance Macro"


class PatchDifficulty(str, Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Advanced = "Advanced"
    Experimental = "Experimental"


class LibraryTier(str, Enum):
    starter = "starter"
    core = "core"
    deep = "deep"


@dataclass(frozen=True)
class PatchCard:
    patch_id: str
    name: str
    category: PatchCategory
    difficulty: PatchDifficulty
    cable_count: int
    stability_score: float
    tags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rationale: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "patch_id": self.patch_id,
            "name": self.name,
            "category": self.category.value,
            "difficulty": self.difficulty.value,
            "cable_count": self.cable_count,
            "stability_score": self.stability_score,
            "tags": list(self.tags),
            "warnings": list(self.warnings),
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class PatchEnvelope:
    closure_strength: float

    def to_dict(self) -> Dict[str, float]:
        return {"closure_strength": self.closure_strength}


@dataclass(frozen=True)
class PatchLibraryItem:
    patch: PatchGraph
    plan: PatchPlan
    validation: ValidationReport
    card: PatchCard
    envelope: PatchEnvelope

    def to_dict(self) -> Dict[str, object]:
        return {
            "patch": self.patch.to_canonical_dict(),
            "plan": self.plan.to_canonical_dict(),
            "validation": self.validation.to_canonical_dict(),
            "card": self.card.to_dict(),
            "envelope": self.envelope.to_dict(),
        }


@dataclass(frozen=True)
class LibraryConstraints:
    tier: LibraryTier
    max_cables: int
    allow_feedback: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "tier": self.tier.value,
            "max_cables": self.max_cables,
            "allow_feedback": self.allow_feedback,
        }


@dataclass(frozen=True)
class PatchLibrary:
    patches: List[PatchLibraryItem] = field(default_factory=list)
    constraints: LibraryConstraints = field(
        default_factory=lambda: LibraryConstraints(
            tier=LibraryTier.core,
            max_cables=12,
            allow_feedback=False,
        )
    )

    def model_copy(self, update: Dict[str, object]) -> "PatchLibrary":
        data = {
            "patches": self.patches,
            "constraints": self.constraints,
        }
        data.update(update)
        return PatchLibrary(**data)

    def to_dict(self) -> Dict[str, object]:
        return {
            "constraints": self.constraints.to_dict(),
            "patches": [p.to_dict() for p in self.patches],
        }
