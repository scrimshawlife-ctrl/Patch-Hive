from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class VisionModuleHit:
    """
    Output of vision extraction:
      - module name + manufacturer (optional)
      - hp estimate (optional)
      - jack labels (optional)
    """

    module_name: str
    manufacturer: Optional[str]
    hp: Optional[int]
    jack_labels: List[str]


@dataclass(frozen=True)
class VisionRigSpec:
    rig_id: str
    modules: List[VisionModuleHit]
    evidence_ref: str


class GeminiVisionClient:
    """
    This is a boundary, not an implementation.
    Real implementation calls Gemini API; PatchHive code stays deterministic and testable by mocking this.
    """

    def extract_rig(self, image_ref: str, *, rig_id: str) -> VisionRigSpec:
        raise NotImplementedError("Implement Gemini API call in an overlay/service, not core.")
