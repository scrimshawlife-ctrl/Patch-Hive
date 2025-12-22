from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from patchhive.schemas_library import PatchLibrary, PatchLibraryItem


@dataclass(frozen=True)
class LibraryPruneSpec:
    """
    Deterministic pruning controls for turning 'everything' into a usable book.
    """

    # hard limits
    max_total: int = 200
    max_per_category: int = 80
    max_per_template: int = 40  # requires template_id in rationale or card.tags

    # user preference weights (higher => keep more)
    category_weights: Dict[str, float] | None = None  # e.g. {"Voice": 2.0, "Generative": 0.6}
    difficulty_weights: Dict[str, float] | None = None  # e.g. {"Beginner": 2.0, "Advanced": 0.7}

    # tag filters
    include_tags_any: Optional[Set[str]] = None
    exclude_tags_any: Optional[Set[str]] = None

    # safety shaping
    drop_runaway: bool = True
    drop_silence: bool = False  # some users want utility/silent patches


def _w(d: Optional[Dict[str, float]], key: str, default: float = 1.0) -> float:
    if not d:
        return default
    return float(d.get(key, default))


def prune_library(lib: PatchLibrary, spec: LibraryPruneSpec) -> PatchLibrary:
    items: List[PatchLibraryItem] = list(lib.patches)

    # 1) hard safety filters
    if spec.drop_runaway:
        items = [it for it in items if not it.validation.runaway_risk]
    if spec.drop_silence:
        items = [it for it in items if not it.validation.silence_risk]

    # 2) tag include/exclude
    if spec.include_tags_any:
        items = [it for it in items if any(t in spec.include_tags_any for t in it.card.tags)]
    if spec.exclude_tags_any:
        items = [it for it in items if not any(t in spec.exclude_tags_any for t in it.card.tags)]

    # 3) score shaped by user weights (still deterministic)
    def shaped_score(it: PatchLibraryItem) -> Tuple[float, float, int, str]:
        cw = _w(spec.category_weights, it.card.category.value, 1.0)
        dw = _w(spec.difficulty_weights, it.card.difficulty.value, 1.0)

        # stability is king; weights shape selection pressure
        base = float(it.card.stability_score)
        shaped = base * cw * dw

        # tie-breaks: closure strength, fewer cables, stable id
        closure = float(it.envelope.closure_strength)
        return (shaped, closure, -it.card.cable_count, it.card.patch_id)

    items.sort(key=shaped_score, reverse=True)

    # 4) enforce per-category caps + per-template caps
    per_cat: Dict[str, int] = {}
    per_tmpl: Dict[str, int] = {}
    kept: List[PatchLibraryItem] = []

    for it in items:
        if len(kept) >= spec.max_total:
            break

        cat = it.card.category.value
        per_cat[cat] = per_cat.get(cat, 0)

        # template_id extraction from rationale (v1 uses "tmpl...." prefix)
        tmpl = "unknown"
        r = it.card.rationale or ""
        if "tmpl." in r:
            # naive but deterministic parse
            start = r.find("tmpl.")
            end = r.find(":", start)
            tmpl = r[start:end] if end != -1 else r[start:]

        per_tmpl[tmpl] = per_tmpl.get(tmpl, 0)

        if per_cat[cat] >= spec.max_per_category:
            continue
        if per_tmpl[tmpl] >= spec.max_per_template:
            continue

        kept.append(it)
        per_cat[cat] += 1
        per_tmpl[tmpl] += 1

    new_lib = lib.model_copy(update={"patches": kept})
    return new_lib
