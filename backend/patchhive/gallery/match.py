"""Fuzzy matching for module gallery entries."""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Iterable

from patchhive.schemas import ModuleGalleryEntry


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def match_module(
    name: str,
    manufacturer: str | None,
    entries: Iterable[ModuleGalleryEntry],
) -> list[tuple[ModuleGalleryEntry, float]]:
    """Return candidate matches with deterministic scores."""
    normalized_name = _normalize(name)
    normalized_mfr = _normalize(manufacturer or "")
    scored: list[tuple[ModuleGalleryEntry, float]] = []
    for entry in entries:
        score = SequenceMatcher(None, normalized_name, _normalize(entry.name)).ratio()
        if manufacturer and entry.manufacturer:
            score = (score * 0.8) + (0.2 * SequenceMatcher(None, normalized_mfr, _normalize(entry.manufacturer)).ratio())
        scored.append((entry, score))
    scored.sort(key=lambda item: (-item[1], item[0].name))
    return scored
