from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PatchTier(str, Enum):
    starter = "starter"
    core = "core"
    deep = "deep"


@dataclass(frozen=True)
class PatchSpaceConstraints:
    tier: PatchTier
    max_cables: int
    allow_feedback: bool
    require_output_path: bool
    max_candidates_per_template: int
    keep_top_per_template: int
