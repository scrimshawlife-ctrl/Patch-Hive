from __future__ import annotations

from typing import Optional

from patchhive.schemas import PatchGraph, PatchPlan, ValidationReport


def validate_patch(patch: PatchGraph, plan: Optional[PatchPlan] = None) -> ValidationReport:
    """
    Deterministic validation placeholder.
    """
    warnings = list(plan.warnings) if plan else []
    stability_score = max(0.0, 1.0 - (0.05 * len(patch.cables)))
    return ValidationReport(
        ok=True,
        warnings=warnings,
        stability_score=stability_score,
        illegal_connections=[],
        silence_risk=[],
        runaway_risk=[],
