"""Book-level PatchBook analytics."""

from __future__ import annotations

from typing import Iterable

from .computation import PatchInsights, _matches_keywords
from .models import (
    CompatibilityGapReport,
    GoldenRackArrangement,
    GoldenRackLayout,
    LearningPath,
    LearningPathStep,
    PatchModulePosition,
)

UTILITY_KEYWORDS = {
    "clock": {"clock", "tempo", "sync"},
    "attenuator": {"attenuator", "attenuverter", "atten"},
    "mixer": {"mixer", "mix"},
    "vca": {"vca", "amp"},
    "quantizer": {"quant", "quantizer"},
}

WORKAROUND_SUGGESTIONS = {
    "clock": "Use a manual trigger or external clock source",
    "attenuator": "Use smaller modulation ranges on source modules",
    "mixer": "Balance levels at the source module outputs",
    "vca": "Use module output level controls as a stand-in for VCA",
    "quantizer": "Use oscillator tuning controls to approximate quantization",
}


def _missing_utilities(module_inventory: list[PatchModulePosition]) -> list[str]:
    names = " ".join(module.name.lower() for module in module_inventory)
    missing = []
    for utility, keywords in UTILITY_KEYWORDS.items():
        if not _matches_keywords(names, keywords):
            missing.append(utility)
    return missing


def _layout_score(module_inventory: list[PatchModulePosition], connections: list[dict[str, str | int]]) -> float:
    positions = {
        module.module_id: (module.row_index, module.start_hp, module.hp)
        for module in module_inventory
        if module.row_index is not None and module.start_hp is not None
    }
    if len(positions) != len(module_inventory):
        return 0.0
    centers = [start + hp / 2 for _, start, hp in positions.values()]
    max_span = max(centers) - min(centers) if centers else 1
    total_distance = 0.0
    count = 0
    for conn in connections:
        from_id = conn.get("from_module_id")
        to_id = conn.get("to_module_id")
        if from_id not in positions or to_id not in positions:
            continue
        from_row, from_start, from_hp = positions[from_id]
        to_row, to_start, to_hp = positions[to_id]
        from_center = from_start + from_hp / 2
        to_center = to_start + to_hp / 2
        total_distance += abs(from_center - to_center) + abs((from_row or 0) - (to_row or 0)) * max_span
        count += 1
    if count == 0:
        return 100.0
    avg_distance = total_distance / count
    score = 100 - (avg_distance / (max_span or 1)) * 50
    return round(max(0.0, score), 1)


def compute_golden_rack_arrangement(
    module_inventory: list[PatchModulePosition],
    all_connections: list[dict[str, str | int]],
) -> GoldenRackArrangement | None:
    if not module_inventory:
        return None
    if any(module.row_index is None or module.start_hp is None for module in module_inventory):
        return None

    score = _layout_score(module_inventory, all_connections)
    layout = GoldenRackLayout(layout_id="current", score=score, modules=module_inventory)

    adjacency_pairs: dict[tuple[str, str], int] = {}
    for conn in all_connections:
        from_id = conn.get("from_module_id")
        to_id = conn.get("to_module_id")
        if from_id is None or to_id is None:
            continue
        from_name = next((m.name for m in module_inventory if m.module_id == from_id), "Unknown")
        to_name = next((m.name for m in module_inventory if m.module_id == to_id), "Unknown")
        pair = tuple(sorted((from_name, to_name)))
        adjacency_pairs[pair] = adjacency_pairs.get(pair, 0) + 1

    hottest = max(adjacency_pairs.items(), key=lambda item: item[1])[0] if adjacency_pairs else None
    adjacency_summary = (
        f"Hottest adjacency: {hottest[0]} ↔ {hottest[1]}" if hottest else "No adjacency hot spots detected"
    )

    missing_utilities = _missing_utilities(module_inventory)
    scoring_explanation = [
        f"Average cable span score: {score}",
        "Based on current rack layout and cable distances",
    ]
    if missing_utilities:
        scoring_explanation.append("Missing utilities reduce routing flexibility")
    scoring_explanation = scoring_explanation[:5]

    return GoldenRackArrangement(
        layouts=[layout],
        scoring_explanation=scoring_explanation,
        adjacency_heatmap_summary=adjacency_summary,
        missing_utility_warnings=[f"Missing {utility}" for utility in missing_utilities],
    )


def compute_compatibility_report(
    module_inventory: list[PatchModulePosition],
    insights: Iterable[PatchInsights],
) -> CompatibilityGapReport:
    missing = _missing_utilities(module_inventory)
    warnings = []
    if missing and any(item.complexity.feedback_present for item in insights):
        warnings.append("Feedback patches without attenuation may be unstable")
    if missing and any(item.probability_loci for item in insights):
        warnings.append("Probability-heavy patches may need quantization")

    return CompatibilityGapReport(
        required_missing_utilities=missing,
        workaround_suggestions=[WORKAROUND_SUGGESTIONS[item] for item in missing if item in WORKAROUND_SUGGESTIONS],
        patch_compatibility_warnings=warnings,
    )


def compute_learning_path(patches: list[dict[str, str | int]], insights: list[PatchInsights]) -> LearningPath:
    combined = [
        (patch, insight)
        for patch, insight in zip(patches, insights)
    ]
    combined.sort(key=lambda item: item[1].effort_score)

    steps: list[LearningPathStep] = []
    effort_scores: list[int] = []
    for patch, insight in combined:
        if insight.complexity.feedback_present:
            concept = "Feedback control"
        elif insight.probability_loci:
            concept = "Probability modulation"
        elif insight.modulation_sources:
            concept = "Modulation routing"
        else:
            concept = "Core signal flow"
        effort_scores.append(insight.effort_score)
        steps.append(
            LearningPathStep(
                patch_id=int(patch.get("patch_id", 0)),
                patch_name=str(patch.get("patch_name", "")),
                concept=concept,
                effort_score=insight.effort_score,
            )
        )

    return LearningPath(
        ordered_patch_sequence=steps,
        effort_score_progression=effort_scores,
    )
