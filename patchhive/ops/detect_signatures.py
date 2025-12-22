from __future__ import annotations

from typing import Dict

from patchhive.schemas import CanonicalRig


def detect_signatures(canon: CanonicalRig) -> Dict[str, bool]:
    """
    Deterministic signature detection.
    Expand this as you add signature rigs (e.g., Make Noise Shared System, etc).
    """
    names = " | ".join([m.name.lower() for m in canon.modules])

    return {
        "has_vl2": ("voltage lab 2" in names) or ("pittsburgh" in names and "voltage lab" in names),
    }
