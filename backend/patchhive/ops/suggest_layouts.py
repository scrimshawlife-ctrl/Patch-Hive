"""Layout suggestion engine."""
from __future__ import annotations

from typing import Dict, List, Tuple

from core.discovery import register_function
from patchhive.schemas import CanonicalRig, SuggestedLayout, ModulePlacement


WEIGHTS = {
    "reach_cost": 1.2,
    "cable_cross_cost": 1.1,
    "learning_gradient": 1.0,
    "utility_proximity": 0.9,
    "patch_template_coverage": 1.3,
}


def _layout_order(canonical_rig: CanonicalRig, layout_type: str) -> List[Tuple[str, int]]:
    modules = canonical_rig.modules
    if layout_type == "Beginner":
        ordered = sorted(modules, key=lambda m: (m.capability_categories[0], m.gallery_entry.name))
    elif layout_type == "Performance":
        ordered = sorted(modules, key=lambda m: (m.gallery_entry.hp * -1, m.gallery_entry.name))
    else:
        ordered = list(reversed(sorted(modules, key=lambda m: m.gallery_entry.name)))
    return [(m.stable_id, m.gallery_entry.hp) for m in ordered]


def _place_modules(ordered: List[Tuple[str, int]], row_hp: int) -> List[ModulePlacement]:
    placements: List[ModulePlacement] = []
    row = 0
    hp_offset = 0
    for module_id, hp in ordered:
        if hp_offset + max(hp, 1) > row_hp:
            row += 1
            hp_offset = 0
        placements.append(ModulePlacement(module_id=module_id, row=row, hp_offset=hp_offset))
        hp_offset += max(hp, 1)
    return placements


def _score_layout(placements: List[ModulePlacement]) -> Dict[str, float]:
    reach_cost = sum(p.row for p in placements) * 0.5
    cable_cross_cost = sum(p.hp_offset for p in placements) * 0.01
    learning_gradient = max(1.0, len({p.row for p in placements})) * 0.8
    utility_proximity = max(1.0, len(placements)) * 0.2
    patch_template_coverage = max(1.0, len(placements)) * 0.3
    return {
        "reach_cost": round(reach_cost, 4),
        "cable_cross_cost": round(cable_cross_cost, 4),
        "learning_gradient": round(learning_gradient, 4),
        "utility_proximity": round(utility_proximity, 4),
        "patch_template_coverage": round(patch_template_coverage, 4),
    }


def _total_score(breakdown: Dict[str, float]) -> float:
    return round(sum(breakdown[key] * WEIGHTS[key] for key in WEIGHTS), 4)


def suggest_layouts(canonical_rig: CanonicalRig, row_hp: int = 84) -> List[SuggestedLayout]:
    layouts: List[SuggestedLayout] = []
    for layout_type in ("Beginner", "Performance", "Experimental"):
        ordered = _layout_order(canonical_rig, layout_type)
        placements = _place_modules(ordered, row_hp=row_hp)
        breakdown = _score_layout(placements)
        total = _total_score(breakdown)
        rationale = f"{layout_type} layout balances reach and cable paths deterministically."
        layouts.append(
            SuggestedLayout(
                layout_type=layout_type,
                placements=placements,
                total_score=total,
                score_breakdown=breakdown,
                rationale=rationale,
            )
        )
    return layouts


register_function(
    name="suggest_layouts",
    function=suggest_layouts,
    description="Suggest deterministic layouts for Beginner, Performance, Experimental.",
    input_model="CanonicalRig",
    output_model="List[SuggestedLayout]",
)
