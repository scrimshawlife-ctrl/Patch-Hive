"""Suggest deterministic layouts for a canonical rig."""

from __future__ import annotations

import random
from typing import Iterable

from patchhive.schemas import (
    CanonicalRig,
    SuggestedLayout,
    SuggestedPlacement,
)

WEIGHTS = {
    "reach_cost": 0.25,
    "cable_cross_cost": 0.2,
    "learning_gradient": 0.15,
    "utility_proximity": 0.25,
    "patch_template_coverage": 0.15,
}


def _score_layout(
    placements: Iterable[SuggestedPlacement],
    seed: int,
) -> tuple[float, dict[str, float]]:
    rng = random.Random(seed)
    reach_cost = sum(abs(p.row) * 0.5 for p in placements) * WEIGHTS["reach_cost"]
    cable_cross_cost = rng.random() * WEIGHTS["cable_cross_cost"]
    learning_gradient = rng.random() * WEIGHTS["learning_gradient"]
    utility_proximity = (1.0 - (rng.random() * 0.5)) * WEIGHTS["utility_proximity"]
    patch_template_coverage = (1.0 - (rng.random() * 0.5)) * WEIGHTS["patch_template_coverage"]
    breakdown = {
        "reach_cost": reach_cost,
        "cable_cross_cost": cable_cross_cost,
        "learning_gradient": learning_gradient,
        "utility_proximity": utility_proximity,
        "patch_template_coverage": patch_template_coverage,
    }
    score = sum(breakdown.values())
    return score, breakdown


def _placements_for_profile(
    canonical: CanonicalRig, profile: str, seed: int
) -> list[SuggestedPlacement]:
    rng = random.Random(seed)
    placements: list[SuggestedPlacement] = []
    for index, module in enumerate(canonical.modules):
        row = 0 if profile == "Beginner" else rng.randint(0, 2)
        x_hp = index * 6
        placements.append(
            SuggestedPlacement(
                module_id=module.canonical_id,
                row=row,
                x_hp=x_hp,
                observed=bool(module.observed_position),
            )
        )
    return placements


def suggest_layouts_v1(canonical: CanonicalRig, user_profile: str, seed: int) -> list[SuggestedLayout]:
    profiles = ["Beginner", "Performance", "Experimental"]
    layouts: list[SuggestedLayout] = []
    for index, profile in enumerate(profiles):
        profile_seed = seed + index
        placements = _placements_for_profile(canonical, profile, profile_seed)
        score, breakdown = _score_layout(placements, profile_seed)
        layouts.append(
            SuggestedLayout(
                layout_id=f"layout-{profile.lower()}-{seed}",
                profile=profile,
                placements=placements,
                score=score,
                breakdown=breakdown,
                rationale=(
                    f"{profile} layout weighted by reach, cable crossings, and proximity."
                ),
            )
        )
    return layouts
