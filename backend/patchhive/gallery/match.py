"""Module matching helpers."""
from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, Iterable, Optional

from patchhive.schemas import ModuleGalleryEntry


def _norm(text: str) -> str:
    normalized = text.lower().strip()
    normalized = re.sub(r"[^a-z0-9\s\-]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


@dataclass(frozen=True)
class MatchCandidate:
    module_gallery_id: str
    score: float


def build_index(entries: Iterable[ModuleGalleryEntry]) -> Dict[str, ModuleGalleryEntry]:
    return {entry.module_gallery_id: entry for entry in entries}


def exact_match(
    entries: Iterable[ModuleGalleryEntry],
    *,
    manufacturer: Optional[str],
    name: str,
) -> Optional[ModuleGalleryEntry]:
    n_name = _norm(name)
    n_mfg = _norm(manufacturer) if manufacturer else None
    for entry in entries:
        if _norm(entry.name) != n_name:
            continue
        if n_mfg is not None and _norm(entry.manufacturer) != n_mfg:
            continue
        return entry
    return None


def fuzzy_match(
    entries: Iterable[ModuleGalleryEntry],
    *,
    manufacturer: Optional[str],
    name: str,
    hp_guess: Optional[int],
    min_score: float = 0.72,
    hp_tolerance: int = 2,
) -> Optional[MatchCandidate]:
    best: Optional[MatchCandidate] = None
    for entry in entries:
        score = similarity(name, entry.name)
        if manufacturer:
            score = (score * 0.85) + (similarity(manufacturer, entry.manufacturer) * 0.15)
        if hp_guess is not None:
            if abs(entry.hp - hp_guess) <= hp_tolerance:
                score = min(1.0, score + 0.05)
            else:
                score = max(0.0, score - 0.05)
        if score < min_score:
            continue
        if best is None or score > best.score:
            best = MatchCandidate(module_gallery_id=entry.module_gallery_id, score=score)
    return best
