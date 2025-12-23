"""Rack layout recommendation logic."""

from __future__ import annotations

from collections import defaultdict

from .models import ConnectionFrequency, LayoutRecommendation, ModuleSpec, RackRecommendationResponse
from .scoring import score_layout, ZONE_ORDER, _normalize_role


def _build_role_sort_key(module: ModuleSpec) -> tuple[int, int]:
    roles = [_normalize_role(tag) for tag in module.role_tags]
    role_index = next((ZONE_ORDER.index(role) for role in roles if role in ZONE_ORDER), len(ZONE_ORDER))
    return (role_index, module.module_id)


def _candidate_layouts(modules: list[ModuleSpec]) -> list[list[int]]:
    by_role = sorted(modules, key=_build_role_sort_key)
    by_id = sorted(modules, key=lambda m: m.module_id)
    by_hp_desc = sorted(modules, key=lambda m: (-m.hp, m.module_id))
    by_hp_asc = sorted(modules, key=lambda m: (m.hp, m.module_id))
    by_role_rev = list(reversed(by_role))

    layouts = [
        [m.module_id for m in by_role],
        [m.module_id for m in by_role_rev],
        [m.module_id for m in by_id],
        [m.module_id for m in by_hp_desc],
        [m.module_id for m in by_hp_asc],
    ]

    deduped = []
    seen = set()
    for layout in layouts:
        key = tuple(layout)
        if key not in seen:
            seen.add(key)
            deduped.append(layout)
    return deduped


def _rationale(score: float, adjacency: float, zoning: float, access: float, cable: float) -> list[str]:
    reasons = []
    reasons.append(f"Adjacency score: {adjacency:.3f} (frequent neighbors closer)")
    reasons.append(f"Zoning score: {zoning:.3f} (functional grouping)")
    reasons.append(f"Access score: {access:.3f} (performance edge access)")
    reasons.append(f"Cable score: {cable:.3f} (distance proxy)")
    reasons.append(f"Total score: {score:.3f}")
    return reasons


def recommend_layouts(
    rack_hp: int,
    modules: list[ModuleSpec],
    connections: list[ConnectionFrequency] | None = None,
) -> RackRecommendationResponse:
    if not modules:
        return RackRecommendationResponse(decision="none", layouts=[])

    modules_by_id = {module.module_id: module for module in modules}
    connections = connections or []

    layouts = _candidate_layouts(modules)
    scored = []
    warnings_map = defaultdict(list)

    total_hp = sum(module.hp for module in modules)
    if total_hp > rack_hp:
        warning = f"Modules exceed rack width by {total_hp - rack_hp}HP."
        for layout in layouts:
            warnings_map[tuple(layout)].append(warning)

    if not connections:
        for layout in layouts:
            warnings_map[tuple(layout)].append("No connection frequency data provided.")

    for layout in layouts:
        score = score_layout(layout, modules_by_id, connections)
        scored.append((layout, score))

    scored.sort(key=lambda item: item[1].total_score, reverse=True)
    top_layout, top_score = scored[0]
    runner_up_score = scored[1][1].total_score if len(scored) > 1 else 0.0

    decision = "candidates"
    selected = scored
    if runner_up_score > 0 and top_score.total_score >= runner_up_score * 1.1:
        decision = "golden"
        selected = scored[:1]
    elif len(scored) > 5:
        selected = scored[:5]

    recommendations = []
    for layout, score in selected:
        recommendations.append(
            LayoutRecommendation(
                layout=layout,
                score=score,
                rationale=_rationale(
                    score.total_score,
                    score.adjacency_score,
                    score.zoning_score,
                    score.access_score,
                    score.cable_score,
                ),
                warnings=warnings_map.get(tuple(layout), []),
            )
        )

    return RackRecommendationResponse(decision=decision, layouts=recommendations)
