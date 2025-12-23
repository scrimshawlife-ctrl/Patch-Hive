from __future__ import annotations

from dataclasses import dataclass
from typing import List

from patchhive.schemas import (
    CanonicalRig,
    LayoutPlacement,
    LayoutScoreBreakdown,
    LayoutType,
    RigMetricsPacket,
    SuggestedLayout,
)


@dataclass(frozen=True)
class CaseSpec:
    rows: int = 1
    row_hp: int = 104


def suggest_layouts(
    rig: CanonicalRig,
    metrics: RigMetricsPacket,
    *,
    case: CaseSpec,
) -> List[SuggestedLayout]:
    """
    Deterministic layout suggestion placeholder.
    """
    base = metrics.routing_flex_score

    placements: List[LayoutPlacement] = []
    cursor = 0.0
    for module in sorted(rig.modules, key=lambda m: m.instance_id):
        placements.append(LayoutPlacement(instance_id=module.instance_id, x_hp=cursor, hp=module.hp))
        cursor += float(module.hp or 0)

    return [
        SuggestedLayout(
            layout_type=LayoutType.grid,
            total_score=base + 0.1,
            score_breakdown=LayoutScoreBreakdown(learning_gradient=0.7),
            placements=placements,
        ),
        SuggestedLayout(
            layout_type=LayoutType.stacked,
            total_score=base + 0.05,
            score_breakdown=LayoutScoreBreakdown(learning_gradient=0.6),
            placements=placements,
        ),
        SuggestedLayout(
            layout_type=LayoutType.vertical,
            total_score=base,
            score_breakdown=LayoutScoreBreakdown(learning_gradient=0.5),
            placements=placements,
        ),
    ]
