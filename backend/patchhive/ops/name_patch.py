from __future__ import annotations

import hashlib
from typing import List

from patchhive.schemas import PatchGraph
from patchhive.schemas_library import PatchCategory, PatchDifficulty


def _h4(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:4].upper()


def categorize_patch(archetype: str) -> PatchCategory:
    key = archetype.strip().lower()
    if "clock" in key:
        return PatchCategory.clocked
    if "generative" in key:
        return PatchCategory.generative
    if "voice" in key:
        return PatchCategory.voice
    return PatchCategory.study


def difficulty_from_cables(n: int, feedback: bool) -> PatchDifficulty:
    if feedback:
        return PatchDifficulty.experimental
    if n <= 3:
        return PatchDifficulty.beginner
    if n <= 6:
        return PatchDifficulty.intermediate
    return PatchDifficulty.advanced


def name_patch(archetype: str, patch: PatchGraph, tags: List[str]) -> str:
    """
    Deterministic, structure-derived.
    """
    cat = categorize_patch(archetype).value

    noun = (
        "Voice"
        if cat == "Voice"
        else ("Clockwright" if cat == "Clocked" else ("Generator" if cat == "Generative" else "Study"))
    )
    verb = "Pulse" if "clock" in archetype else ("Drift" if "generative" in archetype else "Cutglass")

    focus = "Path"
    if any("mod" in t for t in tags):
        focus = "Motion"
    if any("sequence" in t or "clocked" in t for t in tags):
        focus = "Ladder"

    mk = _h4(patch.patch_id)
    return f"{noun} {verb} {focus} Mk.{mk}"
